from pydantic import BaseModel

from core.config import settings


class QeueSignupUserSchema(BaseModel):
    base_url: str = settings.APP_BASE_URL
    token: str
    verify_token_ttl_min: int = settings.VERIFY_TOKEN_TTL_MIN
    email_to: str
    subject: str
