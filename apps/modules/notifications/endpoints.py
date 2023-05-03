import datetime
from dateutil.relativedelta import relativedelta
from typing import List

from fastapi import APIRouter
from fastapi import status, Depends

from apps.modules.common import auth
from apps.modules.users import schemas as user_schemas
from apps.modules.notifications import services as notification_services
from apps.modules.notifications import constants as notification_constants
from apps.modules.notifications import models as notification_models


router = APIRouter()


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
    """
    function to get the List of Requests
    """
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


@router.get(
    "/notifications",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(auth.get_current_user)],
    response_model=List[notification_models.Notifications],
)
async def get_notifications_list(
    request_id: str,
):
    return await notification_services.NotificationServices.get_notifications_list(
        request_id
    )
