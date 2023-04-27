from typing import List

from fastapi_mail import MessageSchema

from apps.settings.local import settings


async def send_mail(ctx, recepient, subject, body):
    try:
        message = MessageSchema(
            recipients=[recepient], subject=subject, body=body, subtype="html"
        )
    except:
        raise ValueError("doinfowr")
    try:
        await settings.SEND_MAIL.send_message(message)
    except:
        raise ValueError("request failed")
