from fastapi import FastAPI
from sqlalchemy import text

from app.core.config import settings
from app.database.connection import engine
from app.database.base import Base
from app.models.user import User
from app.api.user import router
from app.api.auth import router as auth_router
from app.models.transaction import Transaction
from app.api.transaction import router as transaction_router


# Create tables
Base.metadata.create_all(bind=engine)

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION
)

# Include routes
app.include_router(router)
app.include_router(auth_router)
app.include_router(transaction_router)

@app.get("/")
def home():
    return {"message": "Welcome to SentinelAI 🚀"}

@app.get("/db-test")
def db_test():
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return {"status": "Database Connected Successfully ✅"}
    except Exception as e:
        return {"status": "Connection Failed ❌", "error": str(e)}