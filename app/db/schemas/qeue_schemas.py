from pydantic import BaseModel


class QeueSignupUserSchema(BaseModel):
    base_url: str
    token: str
    verify_token_ttl_min: int
    email_to: str
    subject: str
