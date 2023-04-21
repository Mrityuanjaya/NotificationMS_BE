from typing import List

from fastapi import APIRouter
from fastapi import status, Depends

from apps.modules.common.auth import is_system_admin
from apps.modules.applications.services import ApplicationServices
from apps.modules.applications.models import (
    Application,
    ApplicationInput,
    ApplicationOutput,
)


router = APIRouter()


@router.post(
    "/application",
    status_code=status.HTTP_201_CREATED,
    response_model=ApplicationOutput,
    dependencies=[Depends(is_system_admin)],
)
async def create_application(
    application_name: ApplicationInput,
):
    return await ApplicationServices.create_application(application_name)


@router.get(
    "/applications",
    status_code=status.HTTP_200_OK,
    response_model=List[Application],
    dependencies=[Depends(is_system_admin)],
)
async def get_application_list():
    return await ApplicationServices.get_application_list()
