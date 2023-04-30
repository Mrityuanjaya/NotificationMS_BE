from typing import List
from apps.modules.channels import schemas as channel_schemas


class ChannelServices:
    async def get_limited_channels(
        page_no: int = 1, records_per_page: int = 100, application_ids: List[int] = None
    ) -> dict[str, any]:
        """
        function to get limited channels (at max 100)
        """
        if application_ids is not None:
            return {
                "total_channels": await channel_schemas.Channel.filter(
                    application_id__in=application_ids,
                ).count(),
                "channels": await channel_schemas.Channel.filter(
                    application_id__in=application_ids,
                )
                .select_related("application")
                .limit(records_per_page)
                .offset(records_per_page * (page_no - 1)),
            }
        else:
            return {
                "total_channels": await channel_schemas.Channel.all().count(),
                "channels": await channel_schemas.Channel.all()
                .select_related("application")
                .limit(records_per_page)
                .offset(records_per_page * (page_no - 1)),
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

    async def get_email_channel(
        application_id: int,
    ) -> dict:
        """
        function to get active email channel of a particular application
        """
        return (
            await channel_schemas.Channel.filter(application_id=application_id)
            .first()
            .values("configuration")
        )
