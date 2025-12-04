# Entry point for Phase 1: Data Acquisition
from src.utils.logger import get_logger

logger = get_logger("scraper")

def main():
    logger.info("Starting scraping pipeline...")
    # TODO: Initialize GutenbergScraper and LoCScraper here

if __name__ == "__main__":
    main()