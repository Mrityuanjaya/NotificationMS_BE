import datetime
from dateutil.relativedelta import relativedelta
from typing import List

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
        application_list = (
            await user_schemas.Admin.filter(
                user_id=current_user.id, status=2, deleted_at=None
            )
            .all()
            .prefetch_related("user", "application")
            .all()
        )
        request_list = (
            await notification_schemas.Request.filter(
                application_id=application_list[0].id,
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

    async def get_notifications_list(request_id):
        """
        function to get the list of notifications on the basis of Request Id
        """
        notifications_list = await notification_schemas.Notification.all().values()
        return notifications_list
