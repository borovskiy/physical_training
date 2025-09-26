from email.message import EmailMessage
from typing import Any

from celery import shared_task

from app.core.config import settings
from app.db.schemas.qeue_schemas import QeueSignupUserSchema


@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=True, retry_kwargs={"max_retries": 5})
def send_signup_email_task(self, payload: dict[str, Any]) -> str:
    data = QeueSignupUserSchema(**payload)
    link = f"{settings.APP_BASE_URL}/api/v1/auth/confirm?token={data.token}"
    html = f"""
      <p>Привет! Подтверди e-mail: <a href="{link}">{link}</a></p>
      <p>Ссылка действует {data.verify_token_ttl_min} минут.</p>
    """
    msg = EmailMessage()
    msg["From"] = settings.SMTP_FROM
    msg["To"] = data.email_to
    msg["Subject"] = data.subject
    msg.add_alternative(html, subtype="html")

    import asyncio, aiosmtplib
    asyncio.run(aiosmtplib.send(
        msg,
        hostname=settings.SMTP_HOST,
        port=settings.SMTP_PORT,
        username=settings.SMTP_USER,
        password=settings.SMTP_PASS,
        start_tls=False,
        use_tls=True,
        timeout=30,
    ))
    return "ok"
