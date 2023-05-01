from typing import List

from fastapi import APIRouter
from fastapi import status, Depends

from apps.modules.common import auth
from apps.modules.users import schemas as user_schemas
from apps.modules.applications import services as application_services
from apps.modules.applications import models as application_models


router = APIRouter(tags=["applications"])


@router.post(
    "/applications",
    status_code=status.HTTP_201_CREATED,
    response_model=application_models.ApplicationOutput,
    dependencies=[Depends(auth.is_system_admin)],
)
async def create_application(
    application_name: application_models.ApplicationInput,
):
    return await application_services.ApplicationServices.create_application(
        application_name
    )


@router.get(
    "/applications",
    status_code=status.HTTP_200_OK,
    response_model=List[application_models.Application],
)
async def get_application_list(
    current_user: user_schemas.User = Depends(auth.get_current_user),
):
    return await application_services.ApplicationServices.get_application_list(
        current_user
    )
