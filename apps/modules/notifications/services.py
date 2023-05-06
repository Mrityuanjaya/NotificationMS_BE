import asyncio, datetime
from dateutil.relativedelta import relativedelta
from typing import List
import time
import asyncpg.exceptions as postgres_exceptions
from fastapi import HTTPException, status
from tortoise import transactions
from apps.libs import arq
from apps.modules.notifications import schemas as notification_schemas
from apps.modules.notifications import models as notification_models
from apps.modules.notifications import constants as notification_constants
from apps.modules.users import schemas as user_schemas


class NotificationServices:
    def start_datetime():
        starting_time = datetime.datetime.utcnow() - relativedelta(
            months=int(notification_constants.END_DATE_TIME)
        )
        return starting_time

    def end_datetime():
        ending_time = datetime.datetime.utcnow()
        return ending_time

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

    async def get_requests_list_system_admin(
        start_date: datetime.datetime = start_datetime(),
        end_date: datetime.datetime = end_datetime(),
    ) -> List[notification_models.RequestReport]:
        """
        function to get the List of Requests on the basis of Start DateTime and End DateTime
        """
        request_list = (
            await notification_schemas.Request.filter(
                created_at__range=(start_date, end_date)
            )
            .all()
            .values()
        )
        return await NotificationServices.response(request_list)

    async def get_requests_list_admin(
        current_user: user_schemas.User,
        start_date: datetime.datetime = start_datetime(),
        end_date: datetime.datetime = end_datetime(),
    ) -> List[notification_models.RequestReport]:
        """
        function to get the List of Requests on the basis of User ID , Start DateTime and End DateTime
        """
        application = (
            await user_schemas.Admin.filter(
                user_id=current_user.id, status=2, deleted_at=None
            )
            .prefetch_related("user", "application")
            .first()
        )
        if application is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Application not found"
            )
        request_list = (
            await notification_schemas.Request.filter(
                application_id=application.id,
                created_at__range=(start_date, end_date),
            )
            .all()
            .values()
        )

        return await NotificationServices.response(request_list)

    async def get_request_list(
        application_id: int,
        start_date: datetime.datetime = start_datetime(),
        end_date: datetime.datetime = end_datetime(),
    ) -> List[notification_models.RequestReport]:
        """
        function to get the List of Requests on the basis of Application ID , Start DateTime and End DateTime
        """
        request_list = (
            await notification_schemas.Request.filter(
                application_id=application_id, created_at__range=(start_date, end_date)
            )
            .all()
            .values()
        )
        return await NotificationServices.response(request_list)

    async def update_status(request_id, notification_id):
        notification = await notification_schemas.Notification.filter(
            id=notification_id
        ).first()
        notification.status = 1
        await notification.save()

        for retry in range(0, notification_constants.MAX_RETRY):
            try:
                async with transactions.in_transaction():
                    request = (
                        await notification_schemas.Request.filter(id=request_id)
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
            await arq.redis_pool.enqueue_job(
                "send_bulk_push_web_notifications_batch",
                notification_ids_batches[i],
                request_id,
                token_batches[i],
                title,
                body,
            )

    async def get_limited_notifications_list(
        request_id, page_no: int = 1, records_per_page: int = 100
    ):
        """
        function to get the list of notifications on the basis of Request Id
        """
        notifications = (
            await notification_schemas.Notification.filter(request_id=request_id)
            .offset(records_per_page * (page_no - 1))
            .limit(records_per_page)
            .order_by("-created_at")
        )
        total_notifications = await notification_schemas.Notification.filter(
            request_id=request_id
        ).count()
        return {
            "total_notifications": total_notifications,
            "notifications": notifications,
        }

    async def get_request_by_request_id(request_id):
        """
        function to get request instance by it's request id
        """
        return await notification_schemas.Request.filter(id=request_id).first()

    async def get_requests_by_application_id(
        application_id: int, page_no: int, records_per_page: int
    ):
        """
        function to return all requests of an application
        """
        return (
            await notification_schemas.Request.filter(application_id=application_id)
            .offset(records_per_page * (page_no - 1))
            .limit(records_per_page)
            .order_by("-created_at")
        )

    async def get_limited_requests(page_no: int, records_per_page: int):
        """
        function to return limited requests
        """
        return (
            await notification_schemas.Request.all()
            .offset(records_per_page * (page_no - 1))
            .limit(records_per_page)
            .order_by("-created_at")
        )
