"""
Main pipeline script for Phase 1: Data Acquisition.
Runs both Gutenberg and Library of Congress scrapers and saves normalized datasets.
"""
import json
import time
from pathlib import Path
from src.scraping.gutenberg_scraper import GutenbergScraper
from src.scraping.loc_scraper import LoCScraper
from src.utils.logger import get_logger

logger = get_logger("pipeline")

def main():
    # 1. Setup Directories
    base_dir = Path("data")
    raw_gut_dir = base_dir / "raw" / "gutenberg"
    raw_loc_dir = base_dir / "raw" / "loc"
    processed_dir = base_dir / "processed"
    
    # Ensure all directories exist
    for d in [raw_gut_dir, raw_loc_dir, processed_dir]:
        d.mkdir(parents=True, exist_ok=True)
    
    print("\n" + "="*60)
    print("PHASE 1: DATA ACQUISITION PIPELINE")
    print("="*60)

    # ---------------------------------------------------------
    # PART A: Project Gutenberg (Secondary Sources)
    # ---------------------------------------------------------
    print("\n[1/2] Starting Project Gutenberg Scraper...")
    try:
        gut_scraper = GutenbergScraper(output_dir=raw_gut_dir)
        gut_books = gut_scraper.scrape_all()
        
        # Save Normalized JSON
        gut_output = processed_dir / "gutenberg_dataset.json"
        with open(gut_output, "w", encoding="utf-8") as f:
            json.dump(gut_books, f, indent=2, ensure_ascii=False)
            
        logger.info(f"✓ Saved {len(gut_books)} Gutenberg books to {gut_output}")
        
    except Exception as e:
        logger.error(f"✗ Gutenberg Pipeline Failed: {e}")

    # ---------------------------------------------------------
    # PART B: Library of Congress (Primary Sources)
    # ---------------------------------------------------------
    print("\n[2/2] Starting Library of Congress Scraper...")
    try:
        # Rate limit of 1.0s to be polite to LoC servers
        loc_scraper = LoCScraper(output_dir=raw_loc_dir, rate_limit=1.0)
        loc_docs = loc_scraper.scrape_all()
        
        # Save Normalized JSON
        loc_output = processed_dir / "loc_dataset.json"
        with open(loc_output, "w", encoding="utf-8") as f:
            json.dump(loc_docs, f, indent=2, ensure_ascii=False)
            
        logger.info(f"✓ Saved {len(loc_docs)} LoC documents to {loc_output}")
        
    except Exception as e:
        logger.error(f"✗ LoC Pipeline Failed: {e}")

    # ---------------------------------------------------------
    # Summary
    # ---------------------------------------------------------
    print("\n" + "="*60)
    print("PIPELINE COMPLETE")
    print(f"Processed data saved to: {processed_dir.absolute()}")
    print("="*60)

if __name__ == "__main__":
    main()