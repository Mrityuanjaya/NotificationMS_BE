import datetime
from typing import List
from pydantic import BaseModel


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


class Notifications(BaseModel):
    id: int
    recipient_id: int
    status: bool
    type: int
    created_at: datetime.datetime
