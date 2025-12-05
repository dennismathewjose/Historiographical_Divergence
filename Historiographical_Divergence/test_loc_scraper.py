#!/usr/bin/env python3
"""
Test the Library of Congress scraper.
"""
from pathlib import Path
from src.scraping.loc_scraper import LoCScraper
from src.utils.logger import get_logger

logger = get_logger(__name__)

def test_item_format():
    """Test scraping ITEM format (Election Night letter)."""
    print("=" * 60)
    print("TEST 1: ITEM FORMAT (Election Night)")
    print("=" * 60)
    
    output_dir = Path("data/raw/loc")
    scraper = LoCScraper(output_dir=output_dir)
    
    # CORRECTED URL
    doc_info = {
        "url": "https://www.loc.gov/item/mal0440500/", 
        "title": "Letter about Election Night 1860",
        "doc_type": "Letter",
        "recipient": "George Ashmun",
        "date": "1860-11-20"
    }
    
    print(f"Scraping: {doc_info['url']}")
    
    try:
        doc = scraper.scrape_document(doc_info)
        print("✓ Document scraped successfully!")
        print(f"  ID: {doc['id']}")
        print(f"  Content length: {len(doc['content'])}")
        
        # Validation
        assert len(doc['content']) > 50, "Content too short"
        assert "Ashmun" in doc['content'] or "Ashmun" in doc['to'], "Recipient context missing"
        return True
    except Exception as e:
        print(f"✗ Test failed: {e}")
        return False

def test_resource_format():
    """Test scraping RESOURCE format (Fort Sumter)."""
    print("\n" + "=" * 60)
    print("TEST 2: RESOURCE FORMAT (Fort Sumter)")
    print("=" * 60)
    
    output_dir = Path("data/raw/loc")
    scraper = LoCScraper(output_dir=output_dir)
    
    doc_info = {
        "url": "https://www.loc.gov/resource/mal.0882800",
        "title": "Fort Sumter Decision Letter",
        "doc_type": "Letter",
        "recipient": "Gustavus Fox",
        "date": "1861-05-01"
    }
    
    print(f"Scraping: {doc_info['url']}")
    
    try:
        doc = scraper.scrape_document(doc_info)
        print("✓ Document scraped successfully!")
        print(f"  ID: {doc['id']}")
        print(f"  Content length: {len(doc['content'])}")
        
        # Validation
        assert len(doc['content']) > 50, "Content too short"
        # Ensure we didn't get the snowmen
        assert "snowmen" not in doc['content'].lower(), "Scraped footer garbage instead of content"
        return True
    except Exception as e:
        print(f"✗ Test failed: {e}")
        return False

def test_exhibit_format():
    """Test scraping EXHIBIT format (Gettysburg)."""
    print("\n" + "=" * 60)
    print("TEST 3: EXHIBIT FORMAT (Gettysburg)")
    print("=" * 60)
    
    output_dir = Path("data/raw/loc")
    scraper = LoCScraper(output_dir=output_dir)
    
    doc_info = {
        "url": "https://www.loc.gov/exhibits/gettysburg-address/ext/trans-nicolay-copy.html",
        "title": "Gettysburg Address",
        "doc_type": "Speech",
        "recipient": None,
        "date": "1863-11-19"
    }
    
    try:
        doc = scraper.scrape_document(doc_info)
        print("✓ Document scraped successfully!")
        print(f"  ID: {doc['id']}")
        assert "Four score" in doc['content']
        return True
    except Exception as e:
        print(f"✗ Test failed: {e}")
        return False

def test_all_documents():
    output_dir = Path("data/raw/loc")
    scraper = LoCScraper(output_dir=output_dir)
    docs = scraper.scrape_all()
    assert len(docs) == 5
    print(f"\n✓ Scraped {len(docs)} documents successfully.")
    return True

def main():
    results = [
        test_item_format(),
        test_resource_format(),
        test_exhibit_format()
    ]
    
    if all(results):
        print("\nAll unit tests passed. Running full scrape...")
        test_all_documents()
    else:
        print("\nSome tests failed. Check logs.")

if __name__ == "__main__":
    main()