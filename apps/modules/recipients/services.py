from fastapi import File, HTTPException, UploadFile, status

from apps.modules.recipients import schemas as recipient_schema
from apps.modules.users import schemas as user_schemas
from apps.modules.applications import schemas as application_schema
from apps.modules.applications import constants as application_constants


class RecipientServices:
    async def get_records_from_csv(
        csv_file: UploadFile = File(..., media_type="text/csv")
    ):
        """
        function to return records from a csv file
        """

        if csv_file.content_type != "text/csv":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This file format is not supported",
            )
        csv_data = await csv_file.read()
        csv_data = csv_data.decode("utf-8-sig").splitlines()
        records = csv_data[1:]
        records = [line.split(",") for line in records]
        return records

    async def count_recipients(
        current_user: user_schemas.User, application_id: int = None
    ):
        """
        function to return count of recipients in perticular application
        """
        if application_id == 0 and current_user.role == 1:
            count = await recipient_schema.Recipient.all().count()
            return count

        elif application_id == 0 and current_user.role == 2:
            application_list = (
                await user_schemas.Admin.filter(
                    user_id=current_user.id, status=2, deleted_at=None
                )
                .all()
                .prefetch_related("user", "application")
                .all()
            )
            count = await recipient_schema.Recipient.filter(
                application=application_list[0].id
            ).count()
            return count

        application_count = await application_schema.Application.filter(
            id=application_id
        ).count()

        if application_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=application_constants.ERROR_MESSAGES["EMPTY_LIST"],
            )

        count = await recipient_schema.Recipient.filter(
            application=application_id
        ).count()
        return count
