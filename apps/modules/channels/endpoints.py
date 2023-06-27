from tortoise import timezone
from pydantic import ValidationError
from fastapi import APIRouter, Depends, HTTPException, status

from apps.modules.channels.services import ChannelServices
from apps.modules.common import auth, constants as common_constants
from apps.modules.applications.services import ApplicationServices
from apps.modules.channels import (
    schemas as channel_schemas,
    models as channel_models,
    constants as channel_constants,
)
from apps.modules.users import constants as user_constants, schemas as user_schemas
from apps.modules.users.services import UserServices

router = APIRouter(tags=["channels"])


@router.post("/channel", dependencies=[Depends(auth.is_system_admin)], status_code=status.HTTP_201_CREATED)
async def create_channel(channel_data: channel_models.ChannelInput):
    
    channel_data.alias = (channel_data.alias).lower()
    channel = await ChannelServices.get_channel_by_alias(channel_data.alias)
    if channel is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=channel_constants.CHANNEL_ALREADY_EXIST,
        )
    application = await ApplicationServices.get_active_application_by_id(
        channel_data.application_id
    )
    if application is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=user_constants.ERROR_MESSAGES["APPLICATION_NOT_EXIST"],
        )
    await channel_schemas.Channel.create(**(channel_data.dict()))
    return "Channel {} has been created successfully".format(channel_data.alias)


@router.get("/channels", response_model=channel_models.channelPageOutput)
async def get_channels(
    current_user: user_schemas.User = Depends(auth.get_current_user),
    page_no: int = 1,
    records_per_page: int = 100,
) -> channel_models.channelPageOutput:
    channels = []
    if current_user.role == common_constants.SYSTEM_ADMIN_ROLE:
        response = await ChannelServices.get_limited_channels(
            page_no=page_no, records_per_page=records_per_page
        )
    else:
        application_ids = await UserServices.get_active_application_ids_by_admin_id(
            current_user.id
        )
        response = await ChannelServices.get_limited_channels(
            page_no=page_no,
            records_per_page=records_per_page,
            application_ids=application_ids,
        )
    channel_instances = response["channels"]
    total_channels = response["total_channels"]
    for channel_instance in channel_instances:
        channels.append(
            {
                "alias": channel_instance.alias,
                "application_name": channel_instance.application.name,
                "description": channel_instance.description,
                "type": str(channel_instance.type).rsplit(".", 1)[1],
                "is_active": "True" if channel_instance.deleted_at == None else "False",
                "created_at": channel_instance.created_at.strftime(
                    "%d %B %Y, %I:%M:%S %p"
                ),
            }
        )
    return {"total_channels": total_channels, "channels": channels}


@router.get("/channel/{channel_alias}")
async def get_channel(
    channel_alias: str, current_user: user_schemas.User = Depends(auth.get_current_user)
):
    channel = await ChannelServices.get_channel_by_alias(channel_alias)
    if channel is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=channel_constants.CHANNEL_DOES_NOT_EXIST,
        )
    if current_user.role == common_constants.ADMIN_ROLE:
        user_id = current_user.id
        application_id = channel.application_id
        admin = UserServices.get_admin(user_id=user_id, application_id=application_id)
        if admin is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not allowed to view this channel",
            )
    return {
        "alias": channel.alias,
        "name": channel.name,
        "application_name": channel.application.name,
        "description": channel.description,
        "type": str(channel.type).rsplit(".", 1)[1],
        "configuration": channel.configuration,
    }


@router.patch("/channel/{channel_alias}", dependencies=[Depends(auth.is_system_admin)])
async def update_channel(
    channel_alias: str, channel_data: channel_models.ChannelUpdateInput
):
    channel_alias = channel_alias.lower()
    channel = await ChannelServices.get_active_channel_by_alias(channel_alias)
    if channel is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=channel_constants.CHANNEL_DOES_NOT_EXIST,
        )
    try:
        if channel.type == channel_constants.EMAIL_CHANNEL_TYPE:
            channel_models.EmailChannelUpdateInput(**(channel_data.dict()))
        else:
            channel_models.PushWebChannelUpdateInput(**(channel_data.dict()))
    except ValidationError as e:
        error_field = e.errors()[0]["loc"][0]
        error_msg = e.errors()[0]["msg"]
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"{error_field}:{error_msg}",
        )
    await channel.update_from_dict(channel_data.dict())
    await channel.save()
    return "Channel {} has been updated successfully".format(channel_alias)


@router.delete("/channel/{channel_alias}", dependencies=[Depends(auth.is_system_admin)])
async def delete_channel(channel_alias: str):
    channel_alias = channel_alias.lower()
    channel = await ChannelServices.get_active_channel_by_alias(channel_alias)
    if channel is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=channel_constants.CHANNEL_DOES_NOT_EXIST,
        )
    channel.deleted_at = timezone.now()
    await channel.save()
    return "Channel {} has been deleted successfully".format(channel_alias)
