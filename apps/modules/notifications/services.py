import asyncio, datetime
from dateutil.relativedelta import relativedelta
from typing import List

import asyncpg.exceptions as postgres_exceptions
from tortoise import transactions
from apps.libs import arq
from apps.modules.notifications import schemas as notification_schema
from apps.modules.notifications import models as notification_models
from apps.modules.notifications import constants as notification_constants
from apps.modules.users import schemas as user_schemas


class NotificationServices:
    async def response(request_list):
        success = 0
        failure = 0
        for i in request_list:
            success += i["response"]["success"]
            failure += i["response"]["failure"]

        output = {}
        output["total_success"] = success
        output["total_failure"] = failure
        output["response"] = request_list
        return output

    async def get_requests_list(
        application_id: int,
        current_user: user_schemas.User,
        start_date: datetime.datetime = datetime.datetime.utcnow()
        - relativedelta(months=int(notification_constants.END_DATE_TIME)),
        end_date: datetime.datetime = datetime.datetime.utcnow(),
    ) -> List[notification_models.RequestReport]:
        """
        function to get the List of Requests
        """
        if application_id == 0 and current_user.role == 1:
            request_list = (
                await notification_schema.Request.filter(
                    created_at__range=(start_date, end_date)
                )
                .order_by("created_at")
                .all()
                .values()
            )
            return await NotificationServices.response(request_list)

        elif application_id == 0 and current_user.role == 2:
            application_list = (
                await user_schemas.Admin.filter(user_id=current_user.id)
                .all()
                .prefetch_related("user", "application")
                .all()
            )
            request_list = (
                await notification_schema.Request.filter(
                    application_id=application_list[0].id,
                    created_at__range=(start_date, end_date),
                )
                .all()
                .values()
            )

            return await NotificationServices.response(request_list)
        request_list = (
            await notification_schema.Request.filter(
                application_id=application_id, created_at__range=(start_date, end_date)
            )
            .all()
            .values()
        )
        return await NotificationServices.response(request_list)

    async def update_status(request_id, notification_id):
        notification = await notification_schema.Notification.filter(
            id=notification_id
        ).first()
        notification.status = 1
        await notification.save()

        for retry in range(0, notification_constants.MAX_RETRY):
            try:
                async with transactions.in_transaction():
                    request = (
                        await notification_schema.Request.filter(id=request_id)
                        .select_for_update()
                        .first()
                    )
                    request.response["success"] += 1
                    request.response["failure"] -= 1
                    await request.save()
                    break
            except postgres_exceptions.DeadlockDetectedError:
                asyncio.sleep((retry + 1) * notification_constants.SLEEP_TIME)

    async def send_bulk_push_web_notification(
        notification_ids, request_id, tokens, title, body
    ):
        """
        Sends notifications to all the tokens with title and body. It internally calls send_bulk_push_web_notifications_batch
        with at max 500 tokens as fcm can multicast a message to upto 500 tokens at once

        Args:
        notification_ids: IDs of notifications to update notification schema after sending the notification
        request_id: ID of request to update success and failure count after sending the notification
        tokens: List of tokens to which we want to send notifications
        title: title of the notification message
        body: body of the notification

        Returns:
        None

        Raises:
        None
        """

        token_batches = [tokens[i : i + 500] for i in range(0, len(tokens), 500)]
        notification_ids_batches = [
            notification_ids[i : i + 500] for i in range(0, len(notification_ids), 500)
        ]
        total_no_of_batches = len(token_batches)
        for i in range(total_no_of_batches):
            await arq.broker.enqueue_job(
                "send_bulk_push_web_notifications_batch",
                notification_ids_batches[i],
                request_id,
                token_batches[i],
                title,
                body,
            )
