# app/utils/email.py
from email.message import EmailMessage
import aiosmtplib
from app.core.config import settings


async def send_email(to: str, subject: str, html: str, text: str | None = None):
    msg = EmailMessage()
    msg["From"] = settings.SMTP_FROM
    msg["To"] = to
    msg["Subject"] = subject
    if text:
        msg.set_content(text)
    msg.add_alternative(html, subtype="html")

    # Порт 25 обычно с STARTTLS (или вовсе без TLS). Точно НЕ оба сразу.
    await aiosmtplib.send(
        msg,
        hostname=settings.SMTP_HOST,
        port=settings.SMTP_PORT,
        username=settings.SMTP_USER,
        password=settings.SMTP_PASS,
        start_tls=False,  #
        use_tls=True,
        timeout=30,
    )
