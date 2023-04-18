import secrets
import string
from fastapi import HTTPException
from fastapi import status
from apps.modules.applications.schemas import Application
from apps.modules.applications.models import ApplicationInput, ApplicationOutput
from apps.modules.applications.constants import SECRET_KEY_LIMIT


def generate_access_key():
    res = "".join(
        secrets.choice(string.ascii_letters + string.digits)
        for i in range(SECRET_KEY_LIMIT)
    )
    return str(res)


class ApplicationServices:
    async def create_application(
        application_name: ApplicationInput,
    ) -> ApplicationOutput:
        try:
            new_application = await Application.create(
                name=application_name.name,
                access_key=generate_access_key(),
            )
            return new_application
        except Exception as exp:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=str(exp)
            )
