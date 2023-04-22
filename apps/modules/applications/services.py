from typing import List

from fastapi import HTTPException, status

from apps.modules.applications import schemas as application_schema
from apps.modules.applications import models as application_model
from apps.modules.applications import constants as application_constants


def generate_access_key():
    """
    function to generate the access_key for Application
    """
    res = "".join(
        secrets.choice(string.ascii_letters + string.digits)
        for i in range(application_constants.SECRET_KEY_LIMIT)
    )
    return str(res)


class ApplicationServices:
    async def create_application(
        application_name: application_model.ApplicationInput,
    ) -> application_model.ApplicationOutput:
        """
        function to create Application by System Admin
        """
        new_application = await application_schema.Application.create(
            name=application_name.name,
            access_key=CommonServices.generate_unique_string(
                application_constants.SECRET_KEY_LIMIT
            ),
        )

        if new_application is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=application_constants.ERROR_MESSAGES["UNAUTHORIZED_USER"],
            )
        return new_application

    async def get_application_list() -> List[application_schema.Application]:
        """
        function to get the List of Applapplication_schemaications
        """
        application_List = await application_schema.Application.all().values()
        if application_List is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=application_constants.ERROR_MESSAGES["EMPTY_LIST"],
            )
        return application_List
