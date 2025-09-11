
from pydantic_settings import BaseSettings



class Settings(BaseSettings):
    DB_URL: str
    JWT_SECRET: str
    JWT_ALG: str
    VERIFY_TOKEN_TTL_MIN: int
    APP_BASE_URL: str

    SMTP_HOST: str
    SMTP_PORT: int
    SMTP_USER: str
    SMTP_PASS: str
    SMTP_FROM: str

    CLOUD_URL: str
    CLOUD_ACCESS_KEY: str
    CLOUD_SECRET_KEY: str
    CLOUD_REGION: str

    class Config:
        env_file = "../test.env"
        env_file_encoding = "utf-8"


settings = Settings()
