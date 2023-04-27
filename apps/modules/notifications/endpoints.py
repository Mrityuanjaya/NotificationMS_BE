from fastapi import APIRouter
from fastapi import status, Depends, HTTPException
from jinja2 import Environment, FileSystemLoader

from apps.modules.notifications import models as notification_models
from apps.libs.arq import setup as arq_setup

router = APIRouter()

env = Environment(loader=FileSystemLoader("apps/templates/"))


@router.post("/send_notifications")
async def send_notifications(notification_data: notification_models.NotificationData):
    body: str = ""
    if notification_data.template:
        try:
            template = env.get_template("app/" + notification_data.template + ".html")
        except:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Template not found"
            )
        body = (
            template.render(**notification_data.template_data)
            if notification_data.template_data
            else template.render({})
        )
    else:
        body = notification_data.description
    for recepient in notification_data.recepients:
        await arq_setup.redis_pool.enqueue_job(
            "send_mail", recepient, notification_data.subject, body
        )
