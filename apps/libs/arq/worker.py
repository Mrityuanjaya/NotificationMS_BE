from typing import List

from fastapi_mail import MessageSchema
from fastapi_mail import ConnectionConfig, FastMail
from arq import Worker, jobs

from apps.modules.notifications import services as notification_services


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
    recipient_id: str,
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
        await notification_services.NotificationServices.update_status(
            job_info.args[4], job_info.args[5]
        )
    except:
        pass


worker = Worker(functions=[send_mail, send_invitation], after_job_end=after_end_job)
