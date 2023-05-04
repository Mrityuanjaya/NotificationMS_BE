from typing import List

from fastapi_mail import MessageSchema
from fastapi_mail import ConnectionConfig, FastMail
from arq import Worker, jobs
from firebase_admin import messaging
from tortoise import transactions
from apps.modules.notifications import (
    services as notification_services,
    schemas as notification_schemas,
)


async def send_bulk_push_web_notifications_batch(
    ctx, notification_ids_batch, request_id, token_batch, title, body
):
    """
    Sends notifications to all the tokens of token_batch with title and body.

    Args:
    ctx: context obj that stores information like job_id, jpb_try, enqueue_time, etc
    notification_ids_batch: a list of at max 500 notification ids used to update notifications status after
                            successfully sending each notifications
    request_id: request id needed to update success and failure count after sending each notification
    token_batch: list of at max 500 tokens to which we have to send notifications
    title: title of the notification
    body: body of the notification

    Returns:
    A dictionary containing success and failure count
    {batch_success_count: , batch_failure_count: }
    """

    batch_success_count = 0
    batch_failure_count = 0
    message = messaging.MulticastMessage(
        notification=messaging.Notification(
            title=title,
            body="www.google.com",
        ),
        data={"url": "asdfas"},
        tokens=token_batch,
    )
    response: messaging.BatchResponse = messaging.send_multicast(message)
    for idx, single_response in enumerate(response.responses):
        if single_response.success:
            batch_success_count += 1
            notification = await notification_schemas.Notification.filter(
                id=notification_ids_batch[idx]
            ).first()
            notification.status = 1
            await notification.save()
        else:
            batch_failure_count += 1

    async with transactions.in_transaction():
        request = (
            await notification_schemas.Request.filter(id=request_id)
            .select_for_update()
            .first()
        )
        request.response["success"] += batch_success_count
        request.response["failure"] -= batch_success_count
        await request.save()
    return {
        "batch_success_count": batch_success_count,
        "batch_failure_count": batch_failure_count,
    }


async def send_invitation(ctx, email_conf, recipient: str, subject: str, body: str):
    config = ConnectionConfig(**email_conf)
    fm = FastMail(config=config)
    message = MessageSchema(
        recipients=[recipient], subject=subject, body=body, subtype="html"
    )
    await fm.send_message(message)


async def send_mail(
    ctx,
    email_conf,
    recipient: str,
    subject: str,
    body: str,
    request_id: str,
    notification_id: str,
):
    config = ConnectionConfig(**email_conf)
    fm = FastMail(config=config)
    message = MessageSchema(
        recipients=[recipient], subject=subject, body=body, subtype="html"
    )
    await fm.send_message(message)


async def after_end_job(ctx):
    id = ctx["job_id"]
    job = jobs.Job(id, ctx["redis"])
    job_info = await job.info()
    if job_info.function != "send_mail":
        return
    try:
        await job.result()
        request_id = job_info.args[4]
        notification_id = job_info.args[5]
        await notification_services.NotificationServices.update_status(
            request_id, notification_id
        )
    except:
        pass


worker = Worker(
    functions=[send_mail, send_invitation, send_bulk_push_web_notifications_batch],
    after_job_end=after_end_job,
)
