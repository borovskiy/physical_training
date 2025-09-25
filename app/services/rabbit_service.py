import asyncio
import json
from typing import Optional, Any, Awaitable, Callable, Tuple

import aio_pika
from aio_pika import Message, DeliveryMode, RobustConnection
from aio_pika.abc import AbstractIncomingMessage, AbstractChannel, AbstractQueue
from fastapi.encoders import jsonable_encoder

Handler = Callable[[bytes], Awaitable[None]] | Callable[[bytes], None]


class RabbitClientStateless:
    """
    Stateless-вариант: каждый метод сам открывает соединение/канал, делает работу и закрывает всё.
    Хорош для редких publish/consume. Для постоянного consume лучше держать соединение открытым.
    """

    def __init__(
            self,
            amqp_url: str,
            *,
            prefetch: int = 10,
            declare_durable: bool = True,
            default_queue: Optional[str] = None,
    ) -> None:
        self.amqp_url = amqp_url
        self.prefetch = prefetch
        self.declare_durable = declare_durable
        self.default_queue = default_queue

    # ---------- helpers ----------
    async def _open(self) -> Tuple[RobustConnection, AbstractChannel]:
        conn = await aio_pika.connect_robust(self.amqp_url)
        chan = await conn.channel()
        await chan.set_qos(prefetch_count=self.prefetch)
        return conn, chan

    async def _ensure_queue(self, chan: AbstractChannel, queue: Optional[str]) -> AbstractQueue:
        if not queue:
            if not self.default_queue:
                raise ValueError("Queue name is required (no default_queue configured).")
            queue = self.default_queue
        return await chan.declare_queue(queue, durable=self.declare_durable)

    # ---------- publish ----------
    async def publish_bytes(self, body: bytes, *, queue: Optional[str] = None, persistent: bool = True) -> None:
        conn, chan = await self._open()
        try:
            q = await self._ensure_queue(chan, queue)
            msg = Message(
                body=body,
                delivery_mode=DeliveryMode.PERSISTENT if persistent else DeliveryMode.NOT_PERSISTENT,
            )
            await chan.default_exchange.publish(msg, routing_key=q.name)
        finally:
            await chan.close()
            await conn.close()

    async def publish_json(self, payload: Any, *, queue: Optional[str] = None, persistent: bool = True) -> None:
        # корректно кодирует BaseModel/datetime/UUID и т.п.
        body = json.dumps(jsonable_encoder(payload), ensure_ascii=False).encode("utf-8")

        conn, chan = await self._open()
        try:
            q = await self._ensure_queue(chan, queue)
            msg = Message(
                body=body,
                delivery_mode=DeliveryMode.PERSISTENT if persistent else DeliveryMode.NOT_PERSISTENT,
                content_type="application/json",
                content_encoding="utf-8",
            )
            await chan.default_exchange.publish(msg, routing_key=q.name)
        finally:
            await chan.close()
            await conn.close()

    # ---------- pull one ----------
    async def receive_one(
            self,
            *,
            queue: Optional[str] = None,
            no_ack: bool = True,
    ) -> Optional[bytes]:
        """
        Забирает одно сообщение и сразу закрывает канал.
        Если no_ack=True (по умолчанию) — возвращает тело сообщения (bytes) и не ACK'ает.
        Если no_ack=False — сообщение вернётся тоже как bytes и будет ACK'нуто автоматически перед закрытием.
        """
        conn, chan = await self._open()
        try:
            q = await self._ensure_queue(chan, queue)
            msg = await q.get(no_ack=no_ack, fail=False)
            if msg is None:
                return None
            try:
                body = msg.body
                if not no_ack:
                    await msg.ack()
                return body
            finally:
                # если no_ack=False и тут случилось исключение — не ACK'нутое сообщение вернётся в очередь
                if not no_ack and not msg.processed:
                    await msg.nack(requeue=True)
        finally:
            await chan.close()
            await conn.close()

    async def receive_one_process(
            self,
            handler: Handler,
            *,
            queue: Optional[str] = None,
            requeue_on_fail: bool = True,
    ) -> bool:
        """
        Забирает 1 сообщение, вызывает handler(body) в том же канале и делает ACK/NAK.
        Возвращает True, если сообщение было; False — если очередь пуста.
        """
        conn, chan = await self._open()
        try:
            q = await self._ensure_queue(chan, queue)
            msg: AbstractIncomingMessage | None = await q.get(no_ack=False, fail=False)
            if msg is None:
                return False

            try:
                result = handler(msg.body)
                if asyncio.iscoroutine(result):
                    await result
                await msg.ack()
            except Exception:
                await msg.nack(requeue=requeue_on_fail)
                raise
            return True
        finally:
            await chan.close()
            await conn.close()

    # ---------- simple consume for a limited time/messages ----------
    async def consume_for(
            self,
            handler: Handler,
            *,
            queue: Optional[str] = None,
            max_messages: Optional[int] = None,
            processing_timeout: Optional[float] = None,
            requeue_on_timeout: bool = True,
    ) -> int:
        """
        Читает сообщения в цикле и закрывает соединение при завершении
        (по достижении max_messages или по отмене задачи). Возвращает число обработанных сообщений.
        """
        processed = 0
        conn, chan = await self._open()
        try:
            q = await self._ensure_queue(chan, queue)
            async with q.iterator() as it:
                async for msg in it:
                    try:
                        if processing_timeout:
                            result = handler(msg.body)
                            if asyncio.iscoroutine(result):
                                await asyncio.wait_for(result, timeout=processing_timeout)
                            else:
                                await asyncio.wait_for(
                                    asyncio.to_thread(handler, msg.body),
                                    timeout=processing_timeout,
                                )
                        else:
                            result = handler(msg.body)
                            if asyncio.iscoroutine(result):
                                await result
                            else:
                                await asyncio.to_thread(handler, msg.body)

                        await msg.ack()
                        processed += 1
                    except asyncio.TimeoutError:
                        await msg.nack(requeue=requeue_on_timeout)
                    except Exception:
                        await msg.nack(requeue=True)

                    if max_messages and processed >= max_messages:
                        break
        finally:
            await chan.close()
            await conn.close()
        return processed
