from typing import List
from apps.modules.recipients import schemas as recipient_schemas


class RecipientServices:
    async def get_recipient_by_application_id_and_email(application_id, email):
        """
        function to get a recipient by its application_id and email
        """
        return await recipient_schemas.Recipient.get_or_none(
            application_id=application_id, email=email
        )

    async def get_all_recipients(page_no: int = 1, records_per_page: int = 100):
        """
        function to get all recipients (at max 100)
        """
        return (
            await recipient_schemas.Recipient.all()
            .select_related("application")
            .limit(records_per_page)
            .offset(records_per_page * (page_no - 1))
        )

    async def get_recipients_by_application_ids(
        application_ids: List[int], page_no: int = 1, records_per_page: int = 100
    ):
        """
        function to get all recipients by their application_ids
        """
        return (
            await recipient_schemas.Recipient.filter(application_id__in=application_ids)
            .select_related("application")
            .limit(records_per_page)
            .offset(records_per_page * (page_no - 1))
        )
