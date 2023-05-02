import datetime
from dateutil.relativedelta import relativedelta
from typing import List

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
        print(start_date, "  ", end_date)
        if application_id == 0 and current_user.role == 1:
            request_list = (
                await notification_schema.Request.filter(
                    created_at__range=(start_date, end_date)
                )
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
