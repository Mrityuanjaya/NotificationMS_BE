import datetime
from dateutil.relativedelta import relativedelta
from typing import List

from fastapi import HTTPException, status

from apps.modules.notifications import schemas as notification_schema
from apps.modules.notifications import models as notification_models
from apps.modules.notifications import constants as notification_constants
from apps.modules.users import schemas as user_schemas
from firebase_admin import messaging

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
        print(start_date, "  ", end_date)
        if application_id == 0 and current_user.role == 1:
            request_list = (
                await notification_schema.Request.filter(
                    created_at__range=(start_date, end_date)
                )
                .all()
                .values()
            )
            if not request_list:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=notification_constants.ERROR_MESSAGES["EMPTY_REQUESTS"],
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
            if not request_list:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=notification_constants.ERROR_MESSAGES["EMPTY_REQUESTS"],
                )

            return await NotificationServices.response(request_list)
        request_list = (
            await notification_schema.Request.filter(
                application_id=application_id, created_at__range=(start_date, end_date)
            )
            .all()
            .values()
        )
        if not request_list:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=notification_constants.ERROR_MESSAGES["EMPTY_REQUESTS"],
            )
        return await NotificationServices.response(request_list)


    async def send_bulk_push_web_notifications_batch(token_batch, title, body):
        batch_success_count = 0
        batch_failure_count = 0
        message = messaging.MulticastMessage(
                notification=messaging.Notification(
                    title=title,
                    body=body,
                ),
                tokens=token_batch,
            )
        response : messaging.BatchResponse = messaging.send_multicast(message)
        print(len(response.responses))           #-> List of SendResponse
        for idx, single_response in enumerate(response.responses):
            if single_response.success:
                batch_success_count += 1
            else:
                print(f"Failed to send notification to {token_batch[idx]} with error: {single_response.exception}")
                batch_failure_count += 1
        return {'batch_success_count': batch_success_count, "batch_failure_count": batch_failure_count}

    async def send_bulk_push_web_notification(tokens, title, body):
        token_batches = [tokens[i:i+500] for i in range(0, len(tokens), 500)]
        total_failure_count = 0
        total_success_count = 0
        for token_batch in token_batches:
            response = await NotificationServices.send_bulk_push_web_notifications_batch(token_batch=token_batch, title=title, body=body)
            total_success_count += response["batch_success_count"]
            total_failure_count += response["batch_failure_count"]
        return {"total success": total_success_count, "total_failure": total_failure_count}