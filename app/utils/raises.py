from fastapi import HTTPException
from starlette import status


def _unauthorized(detail: str = "Not authenticated"):
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detail,
        headers={"WWW-Authenticate": "Bearer"},
    )


def _forbidden(detail: str = "Forbidden"):
    return HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=detail)


def _not_found(detail: str = "Not found"):
    return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


def _bad_request(detail: str = "Bad request"):
    return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)


def _ok(detail: str = "OK"):
    return HTTPException(status_code=status.HTTP_200_OK, detail=detail)


def _conflict(detail: str = "Conflict"):
    return HTTPException(status_code=status.HTTP_409_CONFLICT, detail=detail)
