import secrets, string
from typing import List

from fastapi import HTTPException, status

from apps.modules.applications import models as application_models, schemas as application_schemas
from apps.modules.applications import constants as application_constants
from apps.modules.common.services import CommonServices


class ApplicationServices:
    async def create_application(
        application_name: application_models.ApplicationInput,
    ) -> application_models.ApplicationOutput:
        """
        function to create Application by System Admin
        """
        new_application = await application_schemas.Application.create(
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

    async def get_application_list() -> List[application_schemas.Application]:
        """
        function to get the List of Applications
        """
        application_List = await application_schemas.Application.all()
        if application_List is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=application_constants.ERROR_MESSAGES["EMPTY_LIST"],
            )
        return application_List
    