from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database.session import get_db
from app.models.transaction import Transaction
from app.schemas.dashboard import DashboardResponse

router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"]
)
#Count Total Transactions
@router.get("/", response_model=DashboardResponse)
def dashboard(db: Session = Depends(get_db)):

    total_transactions = db.query(Transaction).count()

#Count Fraud Transactions
    fraud_transactions = db.query(Transaction).filter(
        Transaction.status == "Fraud"
    ).count()

#Count Suspicious
    suspicious_transactions = db.query(Transaction).filter(
        Transaction.status == "Suspicious"
    ).count()

#Count Safe
    safe_transactions = db.query(Transaction).filter(
        Transaction.status == "Safe"
    ).count()

#Count Pending
    pending_transactions = db.query(Transaction).filter(
        Transaction.status == "Pending"
    ).count()

#Total Amount
    total_amount = db.query(
        func.sum(Transaction.amount)
    ).scalar() or 0

#Fraud Amount
    fraud_amount = db.query(
        func.sum(Transaction.amount)
    ).filter(
        Transaction.status == "Fraud"
    ).scalar() or 0

#Return Response
    return {
        "total_transactions": total_transactions,
        "fraud_transactions": fraud_transactions,
        "suspicious_transactions": suspicious_transactions,
        "safe_transactions": safe_transactions,
        "pending_transactions": pending_transactions,
        "total_amount": total_amount,
        "fraud_amount": fraud_amount
    }