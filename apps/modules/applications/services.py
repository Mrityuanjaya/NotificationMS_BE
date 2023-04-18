import secrets, string
from fastapi import HTTPException, status

from apps.modules.applications.schemas import Application
from apps.modules.applications.models import ApplicationInput, ApplicationOutput
from apps.modules.applications.constants import SECRET_KEY_LIMIT


def generate_access_key():
    """
    function to generate the access_key for Application
    """
    res = "".join(
        secrets.choice(string.ascii_letters + string.digits)
        for i in range(SECRET_KEY_LIMIT)
    )
    return str(res)


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
                access_key=generate_access_key(),
            )
            return new_application
        except Exception as exp:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=str(exp)
            )
