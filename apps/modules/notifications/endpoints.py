import datetime
from dateutil.relativedelta import relativedelta

from fastapi import APIRouter
from fastapi import status, Depends, HTTPException
from jinja2 import Environment, FileSystemLoader

from apps.libs.arq import setup as arq_setup
from apps.modules.common import auth
from apps.modules.users import schemas as user_schemas
from apps.modules.notifications import services as notification_services
from apps.modules.notifications import models as notification_models
from apps.modules.notifications import constants as notification_constants

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


@router.get(
    "/dashboard",
    status_code=status.HTTP_200_OK,
)
async def get_requests_list(
    application_id: int,
    start_date: datetime.datetime = datetime.datetime.utcnow()
    - relativedelta(months=int(notification_constants.END_DATE_TIME)),
    end_date: datetime.datetime = datetime.datetime.utcnow(),
    current_user: user_schemas.User = Depends(auth.get_current_user),
):
    return await notification_services.NotificationServices.get_requests_list(
        application_id, current_user, start_date, end_date
    )
