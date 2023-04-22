from fastapi import File, HTTPException, UploadFile, status


class RecipientServices:
    async def get_records_from_csv(
        csv_file: UploadFile = File(..., media_type="text/csv")
    ):
        """
        function to return records from a csv file
        """

        if csv_file.content_type != "text/csv":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This file format is not supported",
            )
        csv_data = await csv_file.read()
        csv_data = csv_data.decode("utf-8-sig").splitlines()
        records = csv_data[1:]
        records = [line.split(",") for line in records]
        return records
