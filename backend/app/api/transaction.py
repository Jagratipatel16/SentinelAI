from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.transaction import Transaction
from app.models.user import User
from app.schemas.transaction import TransactionCreate, TransactionResponse
from app.services.fraud_detector import detect_fraud

router = APIRouter(
    prefix="/transactions",
    tags=["Transactions"]
)


@router.post("/", response_model=TransactionResponse)
def create_transaction(
    transaction: TransactionCreate,
    db: Session = Depends(get_db)
):

    user = db.query(User).filter(User.id == transaction.user_id).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    status = detect_fraud(transaction.amount)

    db_transaction = Transaction(
        sender=transaction.sender,
        receiver=transaction.receiver,
        amount=transaction.amount,
        transaction_type=transaction.transaction_type,
        status=status,
        user_id=transaction.user_id
    )

    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)

    return db_transaction


@router.get("/", response_model=list[TransactionResponse])
def get_transactions(db: Session = Depends(get_db)):
    return db.query(Transaction).all()


@router.get("/{transaction_id}", response_model=TransactionResponse)
def get_transaction(transaction_id: int, db: Session = Depends(get_db)):

    transaction = db.query(Transaction).filter(
        Transaction.id == transaction_id
    ).first()

    if not transaction:
        raise HTTPException(
            status_code=404,
            detail="Transaction not found"
        )

    return transaction