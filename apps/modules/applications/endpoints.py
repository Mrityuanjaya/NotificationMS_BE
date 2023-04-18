from fastapi import APIRouter
from fastapi import status
from apps.modules.applications.services import ApplicationServices
from apps.modules.applications.models import ApplicationInput, ApplicationOutput


router = APIRouter()


@router.post(
    "/application/",
    status_code=status.HTTP_201_CREATED,
    response_model=ApplicationOutput,
)
async def create_application(application_name: ApplicationInput):
    return await ApplicationServices.create_application(application_name)
