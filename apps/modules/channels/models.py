from typing import Dict, Union
from pydantic import BaseModel, EmailStr, constr, validator
from apps.modules.channels import constants as channel_constants

class EmailConfig(BaseModel):
    email: EmailStr
    password: constr(min_length=8)
    mail_from: str 
    mail_port: int 
    mail_server: str
    use_credentials: bool
    mail_starttls: bool
    mail_ssl_tls: bool
    @validator('email')
    def validate_email(cls, v):
        if len(v) > 320:
            raise ValueError("Email Length is too Long")

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
    configuration: Dict[str, Union[str, int]]

    @validator("type")
    def validate_type(cls, value):
        if value not in (channel_constants.EMAIL_CHANNEL_TYPE, channel_constants.PUSH_CHANNEL_TYPE, channel_constants.WEB_CHANNEL_TYPE):
            raise ValueError('Invalid Channel Type')
        return value
        
    
    @validator("configuration")
    def validate_configuration(cls, value, values):
        if values["type"] == channel_constants.EMAIL_CHANNEL_TYPE:
            EmailConfig(**value)
        else:
            FireBaseConfig(**value)
        return value

    

class ChannelUpdateInput(BaseModel):
    name: constr(max_length=255)
    description: constr(max_length=255)
    configuration: Dict[str, Union[str, int]]

class EmailChannelUpdateInput(ChannelUpdateInput):
    
    @validator('configuration')
    def validate_config(cls, value):
        EmailConfig(**value)

class PushWebChannelUpdateInput(ChannelUpdateInput):
    configuration: FireBaseConfig
