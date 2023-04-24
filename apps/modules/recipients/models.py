from pydantic import BaseModel, EmailStr, Field
from uuid import UUID
from datetime import datetime
class RecipientOutput(BaseModel):
    id: UUID
    email: EmailStr
    name: str = Field(min_length=2) or Field(max_length=20)
    created_at: datetime

