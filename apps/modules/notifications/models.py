import datetime
from typing import List, Dict, Any

from pydantic import BaseModel, EmailStr


class NotificationData(BaseModel):
    recepients: List[EmailStr]
    subject: str
    description: str
    template: str = None
    template_data: Dict[str, Any] = None


class SuccessFailure(BaseModel):
    success: int
    failure: int


class RequestOutput(BaseModel):
    application_id: int
    total_recipients: int
    response: SuccessFailure
    created_at: datetime.datetime


class RequestReport(BaseModel):
    total_success: int
    total_failure: int
    request_list: List[RequestOutput]
