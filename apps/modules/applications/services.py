import secrets
import string
from fastapi import HTTPException
from fastapi import status
from apps.modules.applications.schemas import Application
from apps.modules.applications.models import ApplicationInput, ApplicationOutput
from apps.modules.common.constants import SECRET_KEY_LIMIT


class ApplicationServices:
    res = "".join(
        secrets.choice(string.ascii_uppercase + string.digits)
        for i in range(SECRET_KEY_LIMIT)
    )

    async def create_application(
        application_name: ApplicationInput,
    ) -> ApplicationOutput:
        try:
            new_application = await Application.create(
                name=application_name.name,
                access_key=str(ApplicationServices.res),
            )
            return new_application
        except Exception as exp:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=str(exp)
            )
