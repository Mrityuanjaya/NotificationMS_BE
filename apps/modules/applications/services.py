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
        application = await application_schemas.Application.filter(name=application_name).first()
        if application:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Application with same name already exists")
        new_application = await application_schemas.Application.create(
            name=application_name.name,
            access_key=common_services.CommonServices.generate_unique_string(
                application_constants.SECRET_KEY_LIMIT
            ),
        )

        return new_application

    async def get_active_application_list(current_user):
        if current_user.role == 2:
            application_list = await user_schemas.Admin.filter(
                user_id=current_user.id, status=2, deleted_at=None
            ).prefetch_related("user", "application")
            applications = []
            for app in application_list:
                applications.append(
                    {"id": app.application.id, "name": app.application.name}
                )
            total_applications = await user_schemas.Admin.filter(
                user_id=current_user.id, status=2, deleted_at=None
            ).count()
        else:
            applications = await application_schemas.Application.all()
            total_applications = await application_schemas.Application.all().count()
        return {"total_applications": total_applications, "applications": applications}

    async def get_limited_active_application_list(
        current_user, page_no: int, records_per_page: int
    ):
        if current_user.role == 2:
            application_list = (
                await user_schemas.Admin.filter(
                    user_id=current_user.id, status=2, deleted_at=None
                )
                .offset(records_per_page * (page_no - 1))
                .limit(records_per_page)
                .prefetch_related("user", "application")
            )
            applications = []
            for app in application_list:
                applications.append(
                    {"id": app.application.id, "name": app.application.name}
                )
            total_applications = await user_schemas.Admin.filter(
                user_id=current_user.id, status=2, deleted_at=None
            ).count()
        else:
            applications = (
                await application_schemas.Application.all()
                .offset(records_per_page * (page_no - 1))
                .limit(records_per_page).values("id", "name")
            )
            total_applications = await application_schemas.Application.all().count()
        return {"total_applications": total_applications, "applications": applications}


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
