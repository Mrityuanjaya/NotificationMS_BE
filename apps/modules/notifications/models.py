import datetime
from typing import List
from pydantic import BaseModel, EmailStr, validator
from pydantic import Json
from apps.modules.notifications import constants as notification_constants


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


class NotificationRequest(BaseModel):
    emails : List[EmailStr]
    priority : int

    @validator("priority")
    def validate_priority(cls, value):
        if value not in (notification_constants.HIGH_PRIORITY, notification_constants.MEDIUM_PRIORITY, notification_constants.LOW_PRIORITY):
            raise ValueError("Invalid Notification Priority")
        return value
