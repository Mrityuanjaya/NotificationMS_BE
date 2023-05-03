from typing import Annotated
import datetime
import uuid
from dateutil.relativedelta import relativedelta

from fastapi import APIRouter, Header, status, Depends, HTTPException

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

router = APIRouter(tags=["notifications"])


@router.post("/send_notifications")
async def send_notifications(
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

    recipients = await recipients_services.RecipientServices.get_recipients_by_emails(
        notification_data.recipients, application_id=application.id
    )

    devices = await recipients_services.RecipientServices.get_devices_by_recipient_instances_and_priority(
        recipients, notification_data.priority
    )

    body: str = ""
    template_name = notification_data.template if notification_data.template else ""
    template_data = (
        notification_data.template_data if notification_data.template_data else {}
    )
    if template_name != "":
        try:
            body = jinja_setup.find_template(
                application.name, template_name, template_data
            )
        except:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Template not found"
            )
    else:
        body = notification_data.description
    body_data = {
        "subject": notification_data.subject,
        "description": notification_data.description,
        "template": template_name,
        "template_data": template_data,
    }
    response = {"success": 0, "failure": len(recipients) + len(devices)}
    request = await notification_schemas.Request.create(
        application_id=application.id,
        body=body_data,
        total_recipients=len(recipients) + len(devices),
        response=response,
        priority=notification_data.priority,
    )
    notifications = []
    email_notification_ids = []
    for i in range(0, len(recipients)):
        notification_id = uuid.uuid4()
        email_notification_ids.append(notification_id)
        notifications.append(
            notification_schemas.Notification(
                id=notification_id,
                request_id=request.id,
                recipient_id=recipients[i].id,
                status=0,
                type=1,
            )
        )

    tokens = []
    push_web_notification_ids = []
    for device in devices:
        notification_id = uuid.uuid4()
        push_web_notification_ids.append(notification_id)
        tokens.append(device.token)
        notifications.append(
            notification_schemas.Notification(
                id=notification_id,
                request_id=request.id,
                recipient_id=device.recipient_id,
                status=0,
                type=device.token_type,
            )
        )

    await notification_schemas.Notification.bulk_create(notifications)
    await notification_services.NotificationServices.send_bulk_push_web_notification(
        request_id=request.id,
        tokens=tokens,
        title=notification_data.subject,
        body=notification_data.description,
        notification_ids=push_web_notification_ids,
    )
    email_conf = await channel_services.ChannelServices.get_email_channel(
        application.id
    )
    if email_conf is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Email Configuration Not Found",
        )
    for recipient in recipients:
        await arq.redis_pool.enqueue_job(
            "send_mail",
            email_conf["configuration"],
            recipient.email,
            notification_data.subject,
            body,
            request.id,
            notification_id,
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
