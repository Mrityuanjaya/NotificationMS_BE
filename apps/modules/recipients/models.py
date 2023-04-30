from typing import List
from pydantic import BaseModel, EmailStr, Field
from uuid import UUID
from datetime import datetime

class RecipientRecordInput(BaseModel):
    application_id: int
    email: EmailStr
    token: str
    token_type: int
class Recipient(BaseModel):
    id: UUID
    email: EmailStr
    application_name: str = Field(min_length=2) or Field(max_length=20)
    created_at: datetime

class RecipientOutput(BaseModel):
    total_recipients: int
    recipients: List[Recipient]


