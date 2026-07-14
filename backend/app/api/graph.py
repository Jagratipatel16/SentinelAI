from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import get_db

from app.services.graph_service import (
    get_graph_summary,
    get_highly_connected_accounts,
    get_mule_accounts,
    get_fraud_rings,
    get_circular_transfers
)

router = APIRouter(
    prefix="/graph",
    tags=["Graph Analytics"]
)


# --------------------------------------------------
# Graph Summary
# --------------------------------------------------

@router.get("/summary")
def graph_summary(db: Session = Depends(get_db)):

    return get_graph_summary(db)


# --------------------------------------------------
# Highly Connected Accounts
# --------------------------------------------------

@router.get("/highly-connected")
def highly_connected(db: Session = Depends(get_db)):

    return get_highly_connected_accounts(db)


# --------------------------------------------------
# Mule Accounts
# --------------------------------------------------

@router.get("/mule-accounts")
def mule_accounts(db: Session = Depends(get_db)):

    return get_mule_accounts(db)


# --------------------------------------------------
# Fraud Rings
# --------------------------------------------------

@router.get("/fraud-rings")
def fraud_rings(db: Session = Depends(get_db)):

    return get_fraud_rings(db)


# --------------------------------------------------
# Circular Transfers
# --------------------------------------------------

@router.get("/circular-transfers")
def circular_transfers(db: Session = Depends(get_db)):

    return get_circular_transfers(db)