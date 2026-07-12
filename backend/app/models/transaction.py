from sqlalchemy import Column, Integer, Float, String, ForeignKey
from app.database.base import Base

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)

    sender = Column(String(100), nullable=False)

    receiver = Column(String(100), nullable=False)

    amount = Column(Float, nullable=False)

    transaction_type = Column(String(50))

    status = Column(String(20), default="Pending")

    user_id = Column(Integer, ForeignKey("users.id"))