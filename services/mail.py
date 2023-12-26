from typing import List

from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from pydantic import BaseModel, EmailStr

from core.config import settings


class EmailSchema(BaseModel):
    email: List[EmailStr]

conf = ConnectionConfig(
    MAIL_USERNAME=settings.EMAIL_NAME,
    MAIL_PASSWORD=settings.EMAIL_PASSWORD,
    MAIL_FROM=settings.EMAIL_NAME,
    MAIL_PORT=587,
    MAIL_SERVER=settings.EMAIL_SERVER,
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
)

fm = FastMail(conf)

async def send_verification_email(email: EmailSchema, token: str):
    email_body = """<a href=>http://localhost:8000/users/verify-email/?token={}</a>""".format(token)
    
    message = MessageSchema(
        subject="Online Shopping Platform Account Verification Mail",
        recipients=email.email,
        body=email_body,
        subtype=MessageType.html,
    )
    await fm.send_message(message)
