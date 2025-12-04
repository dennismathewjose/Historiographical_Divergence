#!/usr/bin/env python3
"""
Test the Gutenberg scraper on a single book before running full pipeline.
"""
from pathlib import Path
from src.scraping.gutenberg_scraper import GutenbergScraper
from src.utils.logger import get_logger

logger = get_logger(__name__)


def test_single_book():
    """Test scraping a single book."""
    print("=" * 60)
    print("TESTING GUTENBERG SCRAPER - SINGLE BOOK")
    print("=" * 60)
    print()
    
    # Initialize scraper
    output_dir = Path("data/raw/gutenberg")
    scraper = GutenbergScraper(output_dir=output_dir)
    
    # Test on book 6812 (The Life of Abraham Lincoln by Henry Ketcham)
    print("Testing book 6812...")
    try:
        book = scraper.scrape_book(6812)
        
        print("\n✓ Book scraped successfully!")
        print(f"  ID: {book['id']}")
        print(f"  Title: {book['title']}")
        print(f"  Author: {book['author']}")
        print(f"  Date: {book['date']}")
        print(f"  Content length: {len(book['content']):,} characters")
        print(f"  First 100 chars: {book['content'][:100]}...")
        
        # Validation checks
        assert len(book['content']) > 10000, "Content too short"
        assert '***' not in book['content'][:1000], "Gutenberg markers not removed"
        assert book['title'] != f"Gutenberg Book 6812", "Title not extracted"
        
        print("\n✓ All validation checks passed!")
        return True
        
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_all_books():
    """Test scraping all 5 books."""
    print("\n" + "=" * 60)
    print("TESTING GUTENBERG SCRAPER - ALL BOOKS")
    print("=" * 60)
    print()
    
    output_dir = Path("data/raw/gutenberg")
    scraper = GutenbergScraper(output_dir=output_dir)
    
    print("This will take ~5 minutes (1 second rate limit between books)")
    print()
    
    try:
        books = scraper.scrape_all()
        
        print("\n" + "=" * 60)
        print(f"✓ Scraped {len(books)}/5 books")
        print("=" * 60)
        
        # Summary
        for book in books:
            print(f"\n{book['id']}:")
            print(f"  Title: {book['title']}")
            print(f"  Author: {book['author']}")
            print(f"  Length: {len(book['content']):,} chars")
        
        # Validation
        assert len(books) == 5, f"Expected 5 books, got {len(books)}"
        for book in books:
            assert 'id' in book
            assert 'content' in book
            assert len(book['content']) > 5000, f"Book {book['id']} too short"
        
        print("\n✓ All books validated!")
        return True
        
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run tests."""
    # First test single book
    if not test_single_book():
        print("\nSingle book test failed. Fix before proceeding.")
        return 1
    
    # Ask user if they want to proceed with all books
    print("\n" + "=" * 60)
    response = input("Test passed! Scrape all 5 books? (y/n): ")
    
    if response.lower() != 'y':
        print("\nSkipping full scrape. Run again when ready.")
        return 0
    
    if test_all_books():
        print("\n✓ ALL TESTS PASSED!")
        print("\nNext step: Phase 1B - Library of Congress scraper")
        return 0
    else:
        print("\n✗ Full scrape failed")
        return 1


if __name__ == "__main__":
    exit(main())