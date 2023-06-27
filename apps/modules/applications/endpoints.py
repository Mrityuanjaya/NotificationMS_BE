from typing import List

from fastapi import APIRouter, HTTPException
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
    if await application_services.ApplicationServices.get_application_by_name(application_name) is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Application with same name already exists")
    return await application_services.ApplicationServices.create_application(
        application_name
    )


@router.get(
    "/applications",
    status_code=status.HTTP_200_OK,
    response_model=application_models.ApplicationResponse, 
)
async def get_application_list(
    current_user: user_schemas.User = Depends(auth.get_current_user),page_no: int = None, records_per_page: int = None
):
    if page_no == None:
        return await application_services.ApplicationServices.get_active_application_list(current_user)
    else:
        return await application_services.ApplicationServices.get_limited_active_application_list(
        current_user, page_no, records_per_page
    )
