import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    API_ID = int(os.getenv("API_ID", 12345678))
    API_HASH = os.getenv("API_HASH", "your_api_hash")
    BOT_TOKEN = os.getenv("BOT_TOKEN", "your_bot_token")
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    DATABASE_NAME = os.getenv("DATABASE_NAME", "telegram_accounts_bot")
    OWNER_ID = int(os.getenv("OWNER_ID", 123456789))
    SECOND_OWNER_ID = int(os.getenv("SECOND_OWNER_ID", 0))
