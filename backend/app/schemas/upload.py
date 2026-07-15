from pydantic import BaseModel


class UploadResponse(BaseModel):

    total_records: int

    fraud_transactions: int

    safe_transactions: int

    download_file: str