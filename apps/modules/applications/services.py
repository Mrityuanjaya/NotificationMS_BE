import secrets, string
from typing import List

from fastapi import HTTPException, status

from apps.modules.applications.schemas import Application
from apps.modules.applications.models import (
    ApplicationInput,
    ApplicationOutput,
)
from apps.modules.applications.constants import ERROR_MESSAGES, SECRET_KEY_LIMIT


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
        new_application = await Application.create(
            name=application_name.name,
            access_key=generate_access_key(),
        )

        if new_application is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=ERROR_MESSAGES["UNAUTHORIZED_USER"],
            )
        return new_application

    async def get_application_list() -> List[Application]:
        """
        function to get the List of Applications
        """
        application_List = await Application.all().values()
        if application_List is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ERROR_MESSAGES["EMPTY_LIST"],
            )
        return application_List
