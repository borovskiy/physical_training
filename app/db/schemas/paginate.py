from pydantic import BaseModel, Field


class PageMeta(BaseModel):
    total: int
    limit: int
    pages: int

class PaginationGet(BaseModel):
    limit: int = Field(default=10, ge=1)
    start: int = Field(default=0, ge=0)