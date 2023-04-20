from fastapi import APIRouter
from apps.modules.recipients.schemas import Recipient
import csv
router = APIRouter()



@router.get("/upload")
async def upload_recipients():
    with open('data.csv', 'r', encoding='utf-8-sig') as csvfile:
        reader = csv.DictReader(csvfile)
        recipient_instances = [Recipient(**record) for record in reader]
        await Recipient.bulk_create(recipient_instances)

# Insert data into database