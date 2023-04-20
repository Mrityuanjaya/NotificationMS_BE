from fastapi import HTTPException, status

from apps.modules.applications.schemas import Application
from apps.modules.applications.models import ApplicationInput, ApplicationOutput
from apps.modules.applications.constants import SECRET_KEY_LIMIT
from apps.modules.common.services import CommonServices


class ApplicationServices:
    async def create_application(
        application_name: ApplicationInput,
    ) -> ApplicationOutput:
        """
        function to create Application by System Admin
        """
        try:
            new_application = await Application.create(
                name=application_name.name,
                access_key=CommonServices.generate_unique_string(SECRET_KEY_LIMIT),
            )
            return new_application
        except Exception as exp:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=str(exp)
            )
