import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Database
    DB_PATH = os.getenv("DB_PATH", "data/support_calls.db")
    
    # File uploads
    MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", 50 * 1024 * 1024))
    UPLOAD_DIR = os.getenv("UPLOAD_DIR", "data/uploads")
    
    # CORS
    ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173").split(",")
    
    # Environment
    ENV = os.getenv("ENV", "development")
    DEBUG = ENV == "development"