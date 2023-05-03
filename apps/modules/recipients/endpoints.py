from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from apps.modules.common import auth, constants as common_constants
from apps.modules.common.services import CommonServices
from apps.modules.users import schemas as user_schemas
from apps.modules.recipients import (
    schemas as recipient_schemas,
    models as recipient_models,
)
from apps.modules.recipients.services import RecipientServices
from apps.modules.users.services import UserServices
import uuid

router = APIRouter(tags=["recipients"])


@router.get("/recipients")
async def get_recipients(
    current_user: user_schemas.User = Depends(auth.get_current_user),
    page_no: int = 1,
    records_per_page: int = 100,
):
    recipients = []
    if current_user.role == common_constants.SYSTEM_ADMIN_ROLE:
        response = await RecipientServices.get_limited_recipients(
            page_no=page_no, records_per_page=records_per_page
        )
        recipient_instances = response["recipients"]
        total_recipients = response["total_recipients"]
    else:
        admin_id = current_user.id
        application_ids = await UserServices.get_active_application_ids_by_admin_id(admin_id)
        response = await RecipientServices.get_limited_recipients(
            page_no=page_no,
            records_per_page=records_per_page,
            application_ids=application_ids,
        )
        recipient_instances = response["recipients"]
        total_recipients = response["total_recipients"]
    for recipient_instance in recipient_instances:
        recipients.append(
            {
                "id": recipient_instance.id,
                "email": recipient_instance.email,
                "application_name": recipient_instance.application.name,
                "created_at": recipient_instance.created_at.strftime("%d %B %Y, %I:%M:%S %p"),
            }
        )
    return {"total_recipients": total_recipients, "recipients": recipients}


@router.post("/upload/recipients", dependencies=[Depends(auth.is_system_admin)])
async def upload_recipients(csv_file: UploadFile = File(..., media_type="text/csv")):
    failed_count = 0
    records = await CommonServices.get_records_from_csv(csv_file=csv_file)
    existing_recipients = await RecipientServices.get_all_recipients()
    recipients_to_be_created = []
    devices_to_be_created = []
    recipients_map = {}
    # recipients_map =
    # {
    #   "jai@example.com": {
    #     "1": "4f283cc9-39dc-44d4-9ea2-09048df82b29"
    #   },
    #   "mrityuanjaya.gupta@joshtechnologygroup.com": {
    #     "1": "9c228f98-0125-4df0-b551-c198e96560b7"
    #   },
    # }
    #     token_map =
    #     {
    #       "recipient_id": [
    #       {
    #           "token": "token_3",
    #           "token_type": 2
    #       },
    #       {
    #           "token": "token_4",
    #           "token_type": 1
    #       }
    #       ],
    #       "recipient_id": [
    #       {
    #           "token": "token_5",
    #           "token_type": 2
    #       }
    #       ]
    #   }
    token_map = {}
    for existing_recipient in existing_recipients:
        recipients_map[existing_recipient.email] = {
            existing_recipient.application.id: existing_recipient.id
        }
    for record in records:
        record_dict = {
            "application_id": record[0],
            "email": record[1].lower(),
            "token": record[2],
            "token_type": record[3],
        }
        try:
            recipient = recipient_models.RecipientRecordInput(**record_dict)
            application_id, email, token, token_type = (
                recipient.application_id,
                recipient.email,
                recipient.token,
                recipient.token_type,
            )
            if (
                recipients_map.get(email) == None
                or recipients_map.get(email).get(application_id) == None
            ):
                recipient_id = uuid.uuid4()
                recipients_to_be_created.append(
                    recipient_schemas.Recipient(
                        **{
                            "id": recipient_id,
                            "application_id": application_id,
                            "email": email,
                        }
                    )
                )
                token_map[recipient_id] = [{"token": token, "token_type": token_type}]
                recipients_map[email] = {application_id: recipient_id}
            else:
                recipient_id = recipients_map.get(email).get(application_id)
                if token_map.get(recipient_id) is None:
                    token_map[recipient_id] = []
                token_map[recipient_id].append(
                    {"token": token, "token_type": token_type}
                )
        except:
            failed_count += 1

    await recipient_schemas.Recipient.bulk_create(recipients_to_be_created)
    for recipient_id, tokens in token_map.items():
        for t in tokens:
            devices_to_be_created.append(
                recipient_schemas.Device(
                    **{
                        "recipient_id": recipient_id,
                        "token": t["token"],
                        "token_type": t["token_type"],
                    }
                )
            )
    await recipient_schemas.Device.bulk_create(devices_to_be_created)
    if failed_count > 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="File Uploaded was Unsuccessful. {} record(s) failed".format(
                failed_count
            ),
        )
    else:
        return "File Uploaded Successfully"
    


@router.get("/total_recipients")
async def count_recipients(
    current_user: user_schemas.User = Depends(auth.get_current_user),
    application_id: int = None,
):
    return await RecipientServices.count_recipients(
        current_user, application_id
    )
