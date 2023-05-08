from typing import Annotated, List
import datetime
import uuid
from dateutil.relativedelta import relativedelta

from fastapi import APIRouter, Header, status, Depends, HTTPException, Request

from apps.libs import arq
from apps.modules.jinja import setup as jinja_setup
from apps.modules.common import auth, constants as common_constants
from apps.modules.users import schemas as user_schemas, services as user_services
from apps.modules.applications import services as application_services
from apps.modules.notifications import services as notification_services
from apps.modules.recipients import (
    services as recipients_services,
    schemas as recipient_schemas,
)
from apps.modules.notifications import (
    models as notification_models,
    schemas as notification_schemas,
)
from apps.modules.notifications import constants as notification_constants
from apps.modules.channels import services as channel_services

router = APIRouter(tags=["notifications"])


@router.post("/send_notifications", status_code=status.HTTP_201_CREATED)
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
    recipients_emails = []
    for recipient in notification_data.recipients:
        recipients_emails.append(recipient.email)
    recipients = await recipients_services.RecipientServices.get_recipients_by_emails(
        recipients_emails, application_id=application.id
    )
    devices = await recipients_services.RecipientServices.get_devices_by_recipient_instances_and_priority(
        recipients, notification_data.priority
    )

    template_name = notification_data.template if notification_data.template else ""
    common_template_data = (
        notification_data.common_template_data
        if notification_data.common_template_data
        else {}
    )

    if template_name != "":
        try:
            jinja_setup.find_template(application.name, template_name)
        except:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Template not found"
            )
    body_data = {
        "subject": notification_data.subject,
        "description": notification_data.description,
        "template": template_name,
        "template_data": common_template_data,
    }
    response = {"success": 0, "failure": len(recipients) + len(devices)}
    notification_request = await notification_schemas.Request.create(
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
                request_id=notification_request.id,
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
                request_id=notification_request.id,
                recipient_id=device.recipient_id,
                status=0,
                type=(2 if device.token_type == 1 else 3),
            )
        )
    await notification_schemas.Notification.bulk_create(notifications)
    await notification_services.NotificationServices.send_bulk_push_web_notification(
        request_id=notification_request.id,
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
            detail="Channel Not Found",
        )
    for recipient in notification_data.recipients:
        await arq.broker.enqueue_job(
            "send_mail",
            email_conf["configuration"],
            recipient.email,
            notification_data.subject,
            application.name,
            template_name,
            recipient.data,
            common_template_data,
            notification_data.description,
            notification_request.id,
            notification_id,
        )
    return {"sending notifications"}


@router.get(
    "/dashboard",
    status_code=status.HTTP_200_OK,
)
async def get_requests_list(
    application_id: int,
    start_date: datetime.datetime = None,
    end_date: datetime.datetime = None,
    current_user: user_schemas.User = Depends(auth.get_current_user),
):
    """
    function to get the List of Requests
    """
    if start_date == None:
        start_date = datetime.datetime.now(datetime.timezone.utc).astimezone()-relativedelta(months=int(notification_constants.END_DATE_TIME))
    if end_date == None:
        end_date = datetime.datetime.now(datetime.timezone.utc).astimezone()
    print(start_date, " ", end_date)
    if application_id == 0 and current_user.role == 1:
        return await notification_services.NotificationServices.get_requests_list_system_admin(
            start_date, end_date
        )
    elif application_id == 0 and current_user.role == 2:
        return await notification_services.NotificationServices.get_requests_list_admin(
            current_user, start_date, end_date
        )
    return await notification_services.NotificationServices.get_request_list(
        application_id, start_date, end_date
    )


@router.get("/requests")
async def get_requests(
    application_id: int,
    page_no: int = 1,
    records_per_page: int = 100,
    current_user: user_schemas.User = Depends(auth.get_current_user),
):
    if current_user.role == common_constants.ADMIN_ROLE:
        if application_id == 0:
            return
        admin = await user_services.UserServices.get_admin(
            current_user.id, application_id
        )
        if admin is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized Access"
            )
    if current_user.role == common_constants.SYSTEM_ADMIN_ROLE and application_id == 0:
        request_instances = (
            await notification_services.NotificationServices.get_limited_requests(
                page_no, records_per_page
            )
        )
        total_requests = await notification_schemas.Request.all().count()
    else:
        application = (
            await application_services.ApplicationServices.get_active_application_by_id(
                application_id
            )
        )
        if application is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Application not found"
            )
        request_instances = await notification_services.NotificationServices.get_requests_by_application_id(
            application_id, page_no, records_per_page
        )
        total_requests = await notification_schemas.Request.filter(
            application_id=application_id
        ).count()
    requests = []
    for request_instance in request_instances:
        requests.append(
            {
                "id": request_instance.id,
                "subject": request_instance.body["subject"],
                "priority": request_instance.priority,
                "total_recipients": request_instance.total_recipients,
                "success": request_instance.response["success"],
                "failure": request_instance.response["failure"],
                "created_at": request_instance.created_at,
            }
        )
    return {"total_requests": total_requests, "requests": requests}


@router.get(
    "/notifications",
    status_code=status.HTTP_200_OK,
)
async def get_notifications_list(
    request_id: str,
    current_user: user_schemas.User = Depends(auth.get_current_user),
    page_no: int = 1,
    records_per_page: int = 100,
):
    if current_user.role == common_constants.ADMIN_ROLE:
        request = (
            await notification_services.NotificationServices.get_request_by_request_id(
                request_id
            )
        )
        if request is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Request not found"
            )
        application_id = request.application_id
        admin = await user_services.UserServices.get_admin(
            current_user.id, application_id
        )
        if admin is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized Access"
            )
    response = (
        await notification_services.NotificationServices.get_limited_notifications_list(
            request_id, page_no, records_per_page
        )
    )
    notifications = []
    for notification in response["notifications"]:
        recipient_email = (
            await recipient_schemas.Recipient.filter(
                id=notification.recipient_id
            ).first()
        ).email
        notifications.append(
            {
                "id": notification.id,
                "recipient_email": recipient_email,
                "status": ("Success" if notification.status == 1 else "Failed"),
                "type": str(notification.type).rsplit(".", 1)[-1],
                "created_at": notification.created_at,
            }
        )
    return {
        "total_notifications": response["total_notifications"],
        "notifications": notifications,
    }
