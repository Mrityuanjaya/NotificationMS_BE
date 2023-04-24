from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from apps.modules.common import auth
from apps.modules.common.services import CommonServices
from apps.modules.users import schemas as user_schemas
from apps.modules.recipients import schemas as recipient_schemas, models as recipient_models
from apps.modules.recipients.services import RecipientServices
from apps.modules.users.services import UserServices

router = APIRouter()


@router.get("/recipients", response_model=List[recipient_models.RecipientOutput])
async def get_recipients(
    current_user: user_schemas.User = Depends(auth.get_current_user),
    page_no: int = 1,
    records_per_page:int=100,
):
    recipients = []
    if current_user.role == 1:
        recipient_instances = await RecipientServices.get_all_recipients(
            page_no=page_no, records_per_page=records_per_page
        )
    else:
        admin_id = current_user.id
        application_ids = await UserServices.get_application_ids_by_admin_id(admin_id)
        recipient_instances = await RecipientServices.get_recipients_by_application_ids(
            application_ids
        )
    for recipient_instance in recipient_instances:
        recipients.append(
            {
                "id": recipient_instance.id,
                "email": recipient_instance.email,
                "name": recipient_instance.application.name,
                "created_at": recipient_instance.created_at,
            }
        )
    return recipients


@router.post("/upload/recipients", dependencies=[Depends(auth.is_system_admin)])
async def upload_recipients(csv_file: UploadFile = File(..., media_type="text/csv")):
    records = await CommonServices.get_records_from_csv(csv_file=csv_file)
    recipient_instances = []
    try:
        for record in records:
            application_id, email, token, token_type = (
                int(record[0]),
                record[1],
                record[2],
                record[3],
            )
            recipient_instance = (
                await RecipientServices.get_recipient_by_application_id_and_email(
                    application_id, email
                )
            )
            if recipient_instance is None:
                recipient_instance = await recipient_schemas.Recipient.create(
                    application_id=application_id, email=email
                )
            recipient_instances.append(recipient_instance)
        await recipient_schemas.Device.bulk_create(
            [
                recipient_schemas.Device(
                    **dict(
                        zip(
                            ["recipient_id", "token", "token_type"],
                            [
                                recipient_instances[i].id,
                                token,
                                int(token_type),
                            ],
                        )
                    )
                )
                for i in range(len(records))
            ]
        )
        return {"File uploaded Successfully"}
    except:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Unprocessable Entity",
        )
