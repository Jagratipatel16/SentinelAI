import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    APP_NAME = os.getenv("APP_NAME")
    APP_VERSION = os.getenv("APP_VERSION")

    DB_HOST = os.getenv("DB_HOST")
    DB_PORT = os.getenv("DB_PORT")
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_NAME = os.getenv("DB_NAME")
    SECRET_KEY = os.getenv("SECRET_KEY")
    ALGORITHM = os.getenv("ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")

    GROQ_MODEL = os.getenv(
        "GROQ_MODEL",
        "llama-3.3-70b-versatile"
    )
settings = Settings()

