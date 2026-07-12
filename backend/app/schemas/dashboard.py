from pydantic import BaseModel

class DashboardResponse(BaseModel):
    total_transactions: int
    fraud_transactions: int
    suspicious_transactions: int
    safe_transactions: int
    pending_transactions: int

    total_amount: float
    fraud_amount: float