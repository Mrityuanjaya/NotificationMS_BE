import asyncio, datetime
from dateutil.relativedelta import relativedelta
from typing import List

import asyncpg.exceptions as postgres_exceptions
from tortoise import transactions

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
                .all()
                .values()
            )
            # if not request_list:
            #     raise HTTPException(
            #         status_code=status.HTTP_400_BAD_REQUEST,
            #         detail=notification_constants.ERROR_MESSAGES["EMPTY_REQUESTS"],
            #     )

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
            # if not request_list:
            #     raise HTTPException(
            #         status_code=status.HTTP_400_BAD_REQUEST,
            #         detail=notification_constants.ERROR_MESSAGES["EMPTY_REQUESTS"],
            #     )

            return await NotificationServices.response(request_list)
        request_list = (
            await notification_schema.Request.filter(
                application_id=application_id, created_at__range=(start_date, end_date)
            )
            .all()
            .values()
        )
        # if not request_list:
        # raise HTTPException(
        #     status_code=status.HTTP_400_BAD_REQUEST,
        #     detail=notification_constants.ERROR_MESSAGES["EMPTY_REQUESTS"],
        # )
        return await NotificationServices.response(request_list)

    async def update_status(request_id, recipient_id):
        notification = await notification_schema.Notification.filter(
            request_id=request_id, recipient_id=recipient_id
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
