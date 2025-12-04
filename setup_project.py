import os
from pathlib import Path

def create_project_structure():
    # Root directory name
    root_name = "Historiographical_Divergence"
    base_path = Path(root_name)

    # Define the directory structure
    directories = [
        "config",
        "src/scraping",
        "src/extraction",
        "src/evaluation",
        "src/validation",
        "src/utils",
        "scripts",
        "notebooks",
        "tests",
        "docs",
        "data/raw/gutenberg",
        "data/raw/loc",
        "data/processed",
        "data/extracted",
        "data/evaluation",
        "data/validation",
        "results/figures",
        "results/tables",
        "video"
    ]

    # Define initial files and their content
    files = {
        # Root files
        ".gitignore": """
# Python
__pycache__/
*.py[cod]
*$py.class
venv/
.env
.ipynb_checkpoints/
.pytest_cache/

# Data (Ignore raw large files, keep structure)
data/raw/*
!data/raw/.gitkeep
data/processed/*
!data/processed/.gitkeep
data/extracted/*
!data/extracted/.gitkeep
data/evaluation/*
!data/evaluation/.gitkeep

# IDE
.vscode/
.idea/
""",
        ".env.example": """
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_API_KEY=AIza...
""",
        "requirements.txt": """
# Core Logic
openai>=1.0.0
anthropic>=0.18.0
google-generativeai>=0.3.0
langchain>=0.1.0

# Scraping & Data
requests>=2.31.0
beautifulsoup4>=4.12.0
lxml>=4.9.0
pandas>=2.0.0
numpy>=1.24.0
pydantic>=2.0.0

# Statistical Analysis
scipy>=1.11.0
scikit-learn>=1.3.0

# Utilities
python-dotenv>=1.0.0
pyyaml>=6.0
tqdm>=4.65.0
jupyter>=1.0.0
pytest>=7.4.0
matplotlib>=3.7.0
seaborn>=0.12.0
""",
        "README.md": f"""
# Historiographical Divergence Analysis

An ML-based evaluation system to quantify inconsistencies between primary historical sources (Lincoln) and secondary accounts (Historians).

## Setup
1. `pip install -r requirements.txt`
2. Copy `.env.example` to `.env` and add API keys.
3. Run `python scripts/01_scrape_data.py` to begin.
""",
        
        # Config
        "config/__init__.py": "",
        "config/settings.py": """
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
""",
        
        # Src modules (Init files)
        "src/__init__.py": "",
        "src/scraping/__init__.py": "",
        "src/extraction/__init__.py": "",
        "src/evaluation/__init__.py": "",
        "src/validation/__init__.py": "",
        "src/utils/__init__.py": "",
        
        # Initial Placeholder Scripts
        "src/utils/logger.py": """
import logging
import sys

def get_logger(name: str):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
    return logger
""",
        "scripts/01_scrape_data.py": """
# Entry point for Phase 1: Data Acquisition
from src.utils.logger import get_logger

logger = get_logger("scraper")

def main():
    logger.info("Starting scraping pipeline...")
    # TODO: Initialize GutenbergScraper and LoCScraper here

if __name__ == "__main__":
    main()
"""
    }

    # Create directories
    print(f"Creating project root: {base_path}")
    base_path.mkdir(exist_ok=True)

    for dir_path in directories:
        full_path = base_path / dir_path
        full_path.mkdir(parents=True, exist_ok=True)
        # Add .gitkeep to ensure empty folders are tracked
        (full_path / ".gitkeep").touch()

    # Create files
    for file_path, content in files.items():
        full_path = base_path / file_path
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content.strip())
        print(f"Created: {file_path}")

    print("\n✅ Project structure created successfully!")
    print(f"cd {root_name} && pip install -r requirements.txt")

if __name__ == "__main__":
    create_project_structure()