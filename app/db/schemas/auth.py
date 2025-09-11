from pydantic import BaseModel


class SignupUserRequest(BaseModel):
    email: str
    password: str


class LoginRequest(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class PayloadToken(BaseModel):
    token_limit_verify: int
    time_now: int
    user_id: int
    type: str
