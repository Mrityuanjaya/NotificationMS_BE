from typing import Annotated
import datetime
from dateutil.relativedelta import relativedelta

from fastapi import APIRouter, Header, status, Depends, HTTPException, Request

from apps.libs import arq
from apps.modules.jinja import setup as jinja_setup
from apps.modules.common import auth
from apps.modules.users import schemas as user_schemas
from apps.modules.applications import services as application_services
from apps.modules.notifications import services as notification_services
from apps.modules.recipients import services as recipients_services
from apps.modules.notifications import (
    models as notification_models,
    schemas as notification_schemas,
)
from apps.modules.notifications import constants as notification_constants
from apps.modules.channels import services as channel_services

router = APIRouter()


@router.post("/send_notifications")
async def send_notifications(
    request: Request,
    access_key: Annotated[str, Header()],
    notification_data: notification_models.NotificationData,
):
    application = (
        await application_services.ApplicationServices.get_application_by_access_key(
            access_key
        )
    )
    if not application:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Invalid Access Key"
        )

    body: str = ""
    template_name = notification_data.template if notification_data.template else ""
    template_data = (
        notification_data.template_data if notification_data.template_data else {}
    )
    if template_name != "":
        # try:
        body = jinja_setup.find_template(
            request, application.name, template_name, template_data
        )
        # except:
        #     raise HTTPException(
        #         status_code=status.HTTP_404_NOT_FOUND, detail="Template not found"
        #     )
    else:
        body = notification_data.description
    body_data = {
        "subject": notification_data.subject,
        "description": notification_data.description,
        "template": template_name,
        "template_data": template_data,
    }
    print(body)
    recipients = await recipients_services.RecipientServices.get_recipients_by_emails(
        notification_data.recepients, application_id=application.id
    )
    response = {"success": 0, "failure": len(recipients)}
    request = await notification_schemas.Request.create(
        application_id=application.id,
        body=body_data,
        total_recipients=len(recipients),
        response=response,
        priority=1,
    )
    notifications = []
    for i in range(0, len(recipients)):
        notifications.append(
            notification_schemas.Notification(
                request_id=request.id, recipient_id=recipients[i]["id"], status=0
            )
        )
    await notification_schemas.Notification.bulk_create(notifications)
    email_conf = await channel_services.ChannelServices.get_email_channel(
        application.id
    )
    for recipient in recipients:
        await arq.pool_redis.enqueue_job(
            "send_mail",
            email_conf["configuration"],
            recipient["email"],
            notification_data.subject,
            body,
            request.id,
            recipient["id"],
        )
    return {"sending notifications"}


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
