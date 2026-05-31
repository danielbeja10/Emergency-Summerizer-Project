import os
from dotenv import load_dotenv

load_dotenv(override=True)               # loads .env
load_dotenv(".env.example", override=False)  # fallback if .env is missing

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
DATABASE_PATH  = os.getenv("DATABASE_PATH", "summaries.db")
UPLOAD_FOLDER  = os.getenv("UPLOAD_FOLDER", "uploads")
MAX_FILE_MB    = int(os.getenv("MAX_FILE_MB", 10))
FLASK_SECRET   = os.getenv("FLASK_SECRET", "dev-secret-change-in-prod")
