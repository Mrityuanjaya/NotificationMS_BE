import datetime
from dateutil.relativedelta import relativedelta
from typing import List

from fastapi import APIRouter
from fastapi import status, Depends

from apps.modules.common import auth
from apps.modules.users import schemas as user_schemas
from apps.modules.notifications import services as notification_services
from apps.modules.notifications import constants as notification_constants


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
    return await notification_services.NotificationServices.get_requests_list(
        application_id, current_user, start_date, end_date
    )
