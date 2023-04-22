from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from apps.modules.common import auth
from apps.modules.users import schemas as user_schemas
from apps.modules.recipients import (
    services as recipient_services,
    schemas as recipient_schemas,
)

router = APIRouter()




@router.post("/upload/recipients", dependencies=[Depends(auth.is_system_admin)])
async def upload_recipients(csv_file: UploadFile = File(..., media_type="text/csv")):
    records = await recipient_services.RecipientServices.get_records_from_csv(csv_file)
    try:
        recipient_instances = await recipient_schemas.Recipient.bulk_create(
            [
                recipient_schemas.Recipient(
                    **dict(zip(["application_id", "email"], line))
                )
                for line in records
            ]
        )
        await recipient_schemas.Device.bulk_create(
            [
                recipient_schemas.Device(
                    **dict(
                        zip(
                            ["recipient_id", "token", "token_type"],
                            [
                                recipient_instances[i].id,
                                records[i][2],
                                int(records[i][3]),
                            ],
                        )
                    )
                )
                for i in range(len(records))
            ]
        )
    except:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Unprocessable Entity",
        )
