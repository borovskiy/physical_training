from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.base import BaseModel


class JWTToken(BaseModel):
    __tablename__ = "tokens"

    token: Mapped[str] = mapped_column(String(600), index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    user: Mapped["UserModel"] = relationship(back_populates="token")
