import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Base Paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
EXTRACTED_DIR = DATA_DIR / "extracted"

# API Keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")