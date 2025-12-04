"""
Configuration and settings for the historiographical divergence project.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Project Root
PROJECT_ROOT = Path(__file__).parent.parent

# Data Directories
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
EXTRACTED_DATA_DIR = DATA_DIR / "extracted"
EVALUATION_DATA_DIR = DATA_DIR / "evaluation"
VALIDATION_DATA_DIR = DATA_DIR / "validation"

# Raw Data Subdirectories
GUTENBERG_RAW_DIR = RAW_DATA_DIR / "gutenberg"
LOC_RAW_DIR = RAW_DATA_DIR / "loc"

# Results Directories
RESULTS_DIR = PROJECT_ROOT / "results"
FIGURES_DIR = RESULTS_DIR / "figures"
TABLES_DIR = RESULTS_DIR / "tables"

# API Keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Project Configuration
EVENTS = [
    "election_night_1860",
    "fort_sumter_decision",
    "gettysburg_address",
    "second_inaugural_address",
    "fords_theatre_assassination"
]

EVENT_DESCRIPTIONS = {
    "election_night_1860": "Abraham Lincoln's election as President on November 6, 1860",
    "fort_sumter_decision": "Lincoln's decision to resupply Fort Sumter in April 1861",
    "gettysburg_address": "Lincoln's speech at Gettysburg on November 19, 1863",
    "second_inaugural_address": "Lincoln's second inaugural address on March 4, 1865",
    "fords_theatre_assassination": "Lincoln's assassination at Ford's Theatre on April 14, 1865"
}

# Gutenberg Book IDs
GUTENBERG_BOOK_IDS = [6812, 6811, 12801, 14004, 18379]

# Rate Limiting
SCRAPING_RATE_LIMIT = 1.0  # seconds between requests

# LLM Configuration
DEFAULT_EXTRACTION_PROVIDER = "google"
DEFAULT_EXTRACTION_MODEL = "gemini-1.5-flash"
DEFAULT_EXTRACTION_TEMPERATURE = 0.3

DEFAULT_JUDGE_PROVIDER = "openai"
DEFAULT_JUDGE_MODEL = "gpt-4o-2024-11-20"
DEFAULT_JUDGE_TEMPERATURE = 0