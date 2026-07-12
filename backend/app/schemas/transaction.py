from pydantic import BaseModel

class TransactionCreate(BaseModel):
    sender: str
    receiver: str
    amount: float
    transaction_type: str
    user_id: int


class TransactionResponse(BaseModel):
    id: int
    sender: str
    receiver: str
    amount: float
    transaction_type: str
    status: str
    user_id: int

    class Config:
        from_attributes = True