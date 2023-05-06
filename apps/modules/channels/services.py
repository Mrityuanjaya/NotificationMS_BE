from typing import List
from apps.modules.channels import (
    schemas as channel_schemas,
    constants as channel_constants,
)


class ChannelServices:
    async def get_limited_channels(
        page_no: int = 1, records_per_page: int = 100, application_ids: List[int] = None
    ) -> dict[str, any]:
        """
        function to get limited channels (at max 100)

        Args:
        page_no: page_no for offset
        records_per_page: number of records displayed per page
        application_ids: IDs of applications whose channels are needed

        Returns:
        A dictionary with total number of channels as well as channel instances
        according to the page_no and records_per_page
        {"total_channel": , "channels": }
        """
        if application_ids is not None:
            return {
                "total_channels": await channel_schemas.Channel.filter(
                    application_id__in=application_ids,
                    deleted_at = None
                ).count(),
                "channels": await channel_schemas.Channel.filter(
                    application_id__in=application_ids,
                    deleted_at = None
                )
                .select_related("application")
                .limit(records_per_page)
                .offset(records_per_page * (page_no - 1))
                .order_by('-created_at')
            }
        else:
            return {
                "total_channels": await channel_schemas.Channel.filter(deleted_at = None).count(),
                "channels": await channel_schemas.Channel.filter(deleted_at = None)
                .select_related("application")
                .limit(records_per_page)
                .offset(records_per_page * (page_no - 1))
                .order_by('-created_at'),
            }

    async def get_channel_by_alias(alias: str):
        """
        function to get channel by its alias
        """
        return await channel_schemas.Channel.get_or_none(alias=alias)

    async def get_active_channel_by_alias(alias: str) -> channel_schemas.Channel:
        """
        function to get active channel by its alias
        """
        return await channel_schemas.Channel.get_or_none(
            alias=alias, deleted_at__isnull=True
        )

    async def get_channel_by_alias(alias: str):
        """
        function to get channel along with application name
        """
        return await channel_schemas.Channel.get_or_none(
            alias=alias, deleted_at__isnull=True
        ).select_related("application")

    async def get_email_channel(
        application_id: int,
    ) -> dict:
        """
        function to get active email channel of a particular application
        """
        return (
            await channel_schemas.Channel.filter(
                application_id=application_id, type=channel_constants.EMAIL_CHANNEL_TYPE,deleted_at=None
            )
            .first()
            .values("configuration")
        )
