from typing import Dict, Union, List
from fastapi import HTTPException, status
from pydantic import BaseModel, EmailStr, ValidationError, constr, validator
from apps.modules.channels import constants as channel_constants


class EmailConfig(BaseModel):
    MAIL_USERNAME: EmailStr
    MAIL_PASSWORD: constr(min_length=8)
    MAIL_FROM: str
    MAIL_PORT: int
    MAIL_SERVER: str
    USE_CREDENTIALS: bool
    MAIL_STARTTLS: bool
    MAIL_SSL_TLS: bool

    @validator("MAIL_USERNAME")
    def validate_email(cls, v):
        if len(v) > 320:
            raise ValueError("Email Length is too Long")
        return v


class FireBaseConfig(BaseModel):
    api_key: str
    auth_domain: str
    project_id: str
    storage_bucket: str
    messaging_sender_id: str
    app_id: str
    measurement_id: str


class ChannelInput(BaseModel):
    application_id: int
    name: constr(max_length=255)
    alias: constr(max_length=255)
    description: constr(max_length=255)
    type: int
    configuration: dict

    @validator("configuration")
    def validate_configuration(cls, value, values):
        try: 
            if values["type"] == channel_constants.EMAIL_CHANNEL_TYPE:
                EmailConfig(**value)
            else:
                FireBaseConfig(**value)
        except ValidationError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid Configuration")
        return value


class ChannelUpdateInput(BaseModel):
    name: constr(max_length=255)
    description: constr(max_length=255)
    configuration: Dict[str, Union[str, int]]


class EmailChannelUpdateInput(ChannelUpdateInput):
    @validator("configuration")
    def validate_config(cls, value):
        EmailConfig(**value)


class PushWebChannelUpdateInput(ChannelUpdateInput):
    configuration: FireBaseConfig


class channelOutput(BaseModel):
    alias: str
    application_name: str
    description: str
    is_active: str
    type: str
    created_at: str


class channelPageOutput(BaseModel):
    total_channels: int
    channels: List[channelOutput]
