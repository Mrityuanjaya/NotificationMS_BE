from typing import List
from apps.modules.recipients import (
    schemas as recipient_schemas,
)


class RecipientServices:

    async def get_limited_recipients(
        page_no: int = 1, records_per_page: int = 100, application_ids: List[int] = None
    ) -> dict[str, any]:
        """
        function to get limited recipients (at max 100)
        """
        if application_ids is not None:
            return {
                "total_recipients": await recipient_schemas.Recipient.filter(
                    application_id__in=application_ids
                ).count(),
                "recipients": await recipient_schemas.Recipient.filter(
                    application_id__in=application_ids
                )
                .select_related("application")
                .limit(records_per_page)
                .offset(records_per_page * (page_no - 1)),
            }
        else:
            return {
                "total_recipients": await recipient_schemas.Recipient.all().count(),
                "recipients": await recipient_schemas.Recipient.all()
                .select_related("application")
                .limit(records_per_page)
                .offset(records_per_page * (page_no - 1)),
            }

    async def get_all_recipients() -> List[recipient_schemas.Recipient]:
        """
        function to get all recipients
        """
        return await recipient_schemas.Recipient.all().select_related("application")

    async def get_recipients_by_application_ids(
        application_ids: List[int], page_no: int = 1, records_per_page: int = 100
    ) -> List[recipient_schemas.Recipient]:
        """
        function to get all recipients by their application_ids
        """
        return (
            await recipient_schemas.Recipient.filter(application_id__in=application_ids)
            .select_related("application")
            .limit(records_per_page)
            .offset(records_per_page * (page_no - 1))
        )
