import json
import logging
import time
import uuid
from typing import Callable, Awaitable, Optional, Dict, Any
from urllib.parse import parse_qs

from starlette.types import Scope, Receive, Send, Message
from app.logging_conf import request_id_var, setup_logging

setup_logging()
_base_logger = logging.getLogger(__name__)

TEXTUAL_CT_PREFIXES = (
    "text/",
    "application/json",
    "application/xml",
    "application/x-www-form-urlencoded",
    "application/javascript",
)


def _is_textual(headers: Dict[bytes, bytes]) -> bool:
    ct = headers.get(b"content-type", b"").split(b";", 1)[0].strip().lower()
    return any(ct.startswith(p.encode()) for p in TEXTUAL_CT_PREFIXES)


def _content_type(headers: Dict[bytes, bytes]) -> bytes:
    return headers.get(b"content-type", b"").split(b";", 1)[0].strip().lower()


def _safe_decode(body: bytes, headers: Dict[bytes, bytes]) -> str:
    ct = headers.get(b"content-type", b"")
    charset = "utf-8"
    if b"charset=" in ct:
        try:
            charset = ct.split(b"charset=", 1)[1].split(b";", 1)[0].decode("ascii", "ignore")
        except Exception:
            charset = "utf-8"
    try:
        return body.decode(charset, errors="replace")
    except Exception:
        return body.decode("utf-8", errors="replace")


def _render_route_with_params(
        template: Optional[str],
        path_params: Optional[Dict[str, Any]],
        path: str,
        query: str,
) -> str:
    """Return '/route/with/values?query=..'. Falls back to raw path if template unknown."""
    base = path
    if template and path_params:
        try:
            base = template.format(**path_params)  # FastAPI style '/items/{item_id}'
        except Exception:
            base = path
    if query:
        base = f"{base}?{query}"
    return base


class CorrelationIdASGIMiddleware:
    def __init__(
            self,
            app: Callable[[Scope, Receive, Send], Awaitable[None]],
            *,
            request_body_limit: int = 8 * 1024,
            response_body_limit: int = 8 * 1024,
            log_headers: bool = False,
    ) -> None:
        self.app = app
        self.request_body_limit = request_body_limit
        self.response_body_limit = response_body_limit
        self.log_headers = log_headers

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        headers_raw = dict(scope.get("headers") or [])
        req_id_bytes = headers_raw.get(b"x-request-id")
        process_id = (req_id_bytes.decode("utf-8") if req_id_bytes else str(uuid.uuid4()))
        token = request_id_var.set(process_id)

        method = scope.get("method")
        path = scope.get("path")
        query_string = scope.get("query_string", b"").decode("utf-8")

        async def _read_full_body() -> bytes:
            chunks = []
            while True:
                message = await receive()
                if message["type"] != "http.request":
                    continue
                body = message.get("body", b"") or b""
                if body:
                    chunks.append(body)
                if not message.get("more_body", False):
                    break
            return b"".join(chunks)

        full_req_body = await _read_full_body()

        req_ct = _content_type(headers_raw)
        req_payload_body: Any = None
        if req_ct == b"application/json" and full_req_body:
            try:
                req_payload_body = json.loads(_safe_decode(full_req_body, headers_raw))
            except Exception:
                req_payload_body = _safe_decode(full_req_body, headers_raw)[: self.request_body_limit]
        elif req_ct == b"application/x-www-form-urlencoded" and full_req_body:
            try:
                qs = parse_qs(_safe_decode(full_req_body, headers_raw), keep_blank_values=True)
                req_payload_body = {k: (v[0] if isinstance(v, list) and v else v) for k, v in qs.items()}
            except Exception:
                req_payload_body = _safe_decode(full_req_body, headers_raw)[: self.request_body_limit]
        elif _is_textual(headers_raw) and full_req_body:
            req_payload_body = _safe_decode(full_req_body, headers_raw)[: self.request_body_limit]

        early_route = _render_route_with_params(None, None, path, query_string)
        logger_early = logging.LoggerAdapter(
            _base_logger, {"route": early_route, "method": (method or "").upper()}
        )

        if req_payload_body is not None:
            logger_early.info("HTTP request %s", {"body": req_payload_body})
        else:
            logger_early.info("HTTP request {}")

        replayed = False

        async def replay_receive() -> Message:
            nonlocal replayed
            if not replayed:
                replayed = True
                return {"type": "http.request", "body": full_req_body, "more_body": False}
            return {"type": "http.request", "body": b"", "more_body": False}

        status_code: Optional[int] = None
        resp_headers_raw: Dict[bytes, bytes] = {}
        resp_body_chunks: list[bytes] = []
        resp_total = 0

        async def send_wrapper(message: Message) -> None:
            nonlocal status_code, resp_total, resp_headers_raw
            if message["type"] == "http.response.start":
                status_code = message["status"]
                for k, v in (message.get("headers") or []):
                    resp_headers_raw[k.lower()] = v
            elif message["type"] == "http.response.body":
                body = message.get("body", b"") or b""
                if body and resp_total < self.response_body_limit:
                    take = min(len(body), self.response_body_limit - resp_total)
                    resp_body_chunks.append(body[:take])
                resp_total += len(body)
            await send(message)

        started = time.perf_counter()
        try:
            await self.app(scope, replay_receive, send_wrapper)
        finally:
            duration_ms = (time.perf_counter() - started) * 1000.0

            route_template = None
            path_params = None
            try:
                route = scope.get("route")
                if route is not None and hasattr(route, "path"):
                    route_template = getattr(route, "path", None) or getattr(route, "path_format", None)
                path_params = scope.get("path_params", None)
            except Exception:
                pass

            final_route = _render_route_with_params(route_template, path_params, path, query_string)
            logger = logging.LoggerAdapter(
                _base_logger, {"route": final_route, "method": (method or "").upper()}
            )

            resp_body_b = b"".join(resp_body_chunks)
            resp_ct = _content_type(resp_headers_raw)
            resp_payload_body: Any = None
            if resp_ct == b"application/json" and resp_body_b:
                try:
                    resp_payload_body = json.loads(_safe_decode(resp_body_b, resp_headers_raw))
                except Exception:
                    resp_payload_body = _safe_decode(resp_body_b, resp_headers_raw)[: self.response_body_limit]
            elif _is_textual(resp_headers_raw) and resp_body_b:
                resp_payload_body = _safe_decode(resp_body_b, resp_headers_raw)[: self.response_body_limit]

            if resp_payload_body is not None:
                logger.info("HTTP response %s %s", status_code, {"body": resp_payload_body})
            else:
                logger.info("HTTP response %s {}", status_code)

            request_id_var.reset(token)
