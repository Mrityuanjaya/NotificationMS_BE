from fastapi import HTTPException, status

from apps.modules.applications import (
    models as application_models,
    schemas as application_schemas,
)
from apps.modules.applications import constants as application_constants
from apps.modules.common.services import CommonServices
from apps.modules.users import schemas as user_schemas
from apps.modules.common import services as common_services


class ApplicationServices:
    async def create_application(
        application_name: application_models.ApplicationInput,
    ) -> application_models.ApplicationOutput:
        """
        function to create Application by System Admin
        """
        new_application = await application_schemas.Application.create(
            name=application_name.name,
            access_key=common_services.CommonServices.generate_unique_string(
                application_constants.SECRET_KEY_LIMIT
            ),
        )

        return new_application

    async def get_application_list(current_user):
        """
        function to get the List of Applications
        """
        if current_user.role == 2:
            application_List = (
                await user_schemas.Admin.filter(user_id=current_user.id)
                .all()
                .prefetch_related("user", "application")
                .all()
            )
            if application_List is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=application_constants.ERROR_MESSAGES["EMPTY_LIST"],
                )
            applications = []
            for app in application_List:
                applications.append(
                    {"id": app.application.id, "name": app.application.name}
                )
            return applications

        application_List = await application_schemas.Application.all().values()
        if application_List is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=application_constants.ERROR_MESSAGES["EMPTY_LIST"],
            )
        return application_List

    async def get_application_by_id(id: int):
        """
        function to get application by it's id
        """
        return await application_schemas.Application.get_or_none(id=id)

    async def get_active_application_by_id(id: int):
        """
        function to get active application by it's id
        """
        return await application_schemas.Application.get_or_none(
            id=id, deleted_at__isnull=True
        )

    async def get_application_by_access_key(access_key: str):
        return await application_schemas.Application.filter(
            access_key=access_key
        ).first()
