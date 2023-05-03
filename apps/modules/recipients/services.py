from typing import List

from fastapi import HTTPException, status
from apps.modules.recipients import (
    schemas as recipient_schemas,
)
from apps.modules.applications import schemas as application_schemas, constants as application_constants
from apps.modules.users import schemas as user_schemas

from apps.modules.notifications import constants as notification_constants


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

    async def get_recipients_by_emails(
        emails: List[str], application_id: int
    ) -> List[recipient_schemas.Recipient]:
        """
        Fetches all recepient instances with given emails of a particular application

        Args:
        emails: List of emails of recipients to be fetched
        application_id: Application id of recipients

        Returns:
        Returns list of recipient instances of all emails 

        Raises:
        Raises HTTP Exception 404 if any of the email is not found and returns all the emails that were not found
        """
        recipient_instances = []
        emails_not_found = []
        for email in emails:
            recipient_instance = await recipient_schemas.Recipient.filter(email=email, application_id=application_id).first().prefetch_related('devices')
            if recipient_instance:
                recipient_instances.append(recipient_instance)
            else:
                emails_not_found.append(email)
        if emails_not_found != []:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{', '.join(emails_not_found)} not found")
        return recipient_instances

        

    async def get_devices_by_recipient_instances_and_priority(
        recipient_instances, priority
    ) -> List[recipient_schemas.Device]:
        """
        returns all devices of all the recipient instances according to the priority

        Args: recipient instances whose devices are needed
        priority: priority can be HIGH(EMAIL, PUSH and WEB), MEDIUM(EMAIL and PUSH), LOW(EMAIL)

        Returns: list of device instances of recipients according to the priority
        """
        devices = []
        if priority == notification_constants.HIGH_PRIORITY:
            for recipient_instance in recipient_instances:
                devices.extend(await recipient_instance.devices)
        elif priority == notification_constants.MEDIUM_PRIORITY:
            for recipient_instance in recipient_instances:
                recipient_devices = await recipient_instance.devices
                for recipient_device in recipient_devices:
                    if recipient_device.token_type == 1:
                        devices.append(recipient_device)
        return devices

    async def count_recipients(
            current_user: user_schemas.User, application_id: int = None
        ):
            """
            function to return count of recipients in perticular application
            """
            if application_id == 0 and current_user.role == 1:
                count = await recipient_schemas.Recipient.all().count()
                return count

            elif application_id == 0 and current_user.role == 2:
                application_list = (
                    await user_schemas.Admin.filter(user_id=current_user.id, status=2)
                    .all()
                    .prefetch_related("user", "application")
                    .all()
                )
                count = await recipient_schemas.Recipient.filter(
                    application=application_list[0].id
                ).count()
                return count

            application_count = await application_schemas.Application.filter(
                id=application_id
            ).count()

            if application_count == 0:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=application_constants.ERROR_MESSAGES["EMPTY_LIST"],
                )

            count = await recipient_schemas.Recipient.filter(
                application=application_id
            ).count()
            return count

