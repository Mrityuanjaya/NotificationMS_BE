import datetime
from typing import List, Dict, Any
from apps.modules.notifications import constants as notification_constants
from pydantic import BaseModel, EmailStr, validator


class NotificationData(BaseModel):
    recipients: List[EmailStr]
    priority: int
    subject: str
    description: str
    template: str = None
    template_data: Dict[str, Any] = None

    @validator("priority")
    def validate_priority(cls, value):
        if value not in (notification_constants.HIGH_PRIORITY, notification_constants.LOW_PRIORITY, notification_constants.MEDIUM_PRIORITY):
            raise ValueError("Invalid Priority")
        return value


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


