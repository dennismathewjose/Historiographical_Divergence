"""
Scraper for Project Gutenberg books about Abraham Lincoln.
"""
import re
import time
import requests
from pathlib import Path
from typing import Dict, List, Optional
from src.utils.logger import get_logger

logger = get_logger(__name__)


class GutenbergScraper:
    """Scrape books from Project Gutenberg."""
    
    BASE_URL = "https://www.gutenberg.org"
    BOOK_IDS = [6812, 6811, 12801, 14004, 18379]
    
    def __init__(self, output_dir: Path, rate_limit: float = 1.0):
        """
        Initialize scraper.
        
        Args:
            output_dir: Directory to save raw text files
            rate_limit: Seconds to wait between requests
        """
        self.output_dir = output_dir
        self.rate_limit = rate_limit
        self.output_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"GutenbergScraper initialized: {output_dir}")
    
    def scrape_all(self) -> List[Dict]:
        """
        Scrape all books and return normalized JSON.
        
        Returns:
            List of book dictionaries
        """
        books = []
        
        for book_id in self.BOOK_IDS:
            logger.info(f"Scraping book {book_id}...")
            try:
                book_data = self.scrape_book(book_id)
                books.append(book_data)
                logger.info(f"✓ Successfully scraped book {book_id}")
                time.sleep(self.rate_limit)
            except Exception as e:
                logger.error(f"✗ Error scraping book {book_id}: {e}")
                continue
        
        return books
    
    def scrape_book(self, book_id: int) -> Dict:
        """
        Scrape a single book.
        
        Args:
            book_id: Project Gutenberg book ID
            
        Returns:
            Book dictionary with normalized schema
        """
        # Try different URL formats
        urls = [
            f"{self.BASE_URL}/files/{book_id}/{book_id}-0.txt",
            f"{self.BASE_URL}/files/{book_id}/{book_id}.txt",
            f"{self.BASE_URL}/cache/epub/{book_id}/pg{book_id}.txt"
        ]
        
        text = None
        for url in urls:
            try:
                response = requests.get(url, timeout=10)
                response.raise_for_status()
                text = response.text
                logger.debug(f"Successfully fetched from {url}")
                break
            except requests.RequestException:
                continue
        
        if text is None:
            raise ValueError(f"Could not fetch book {book_id} from any URL")
        
        # Extract metadata using regex
        metadata = self.extract_metadata(text)
        
        # Clean content (remove Gutenberg headers/footers)
        content = self.clean_content(text)
        
        # Save raw file
        raw_path = self.output_dir / f"book_{book_id}.txt"
        raw_path.write_text(text, encoding='utf-8')
        logger.debug(f"Saved raw text to {raw_path}")
        
        return {
            "id": f"gutenberg_{book_id}",
            "title": metadata.get("title", f"Gutenberg Book {book_id}"),
            "reference": f"{self.BASE_URL}/ebooks/{book_id}",
            "document_type": "Book",
            "date": metadata.get("release_date", "Unknown"),
            "author": metadata.get("author", "Unknown"),
            "place": None,
            "from": None,
            "to": None,
            "content": content
        }
    
    def extract_metadata(self, text: str) -> Dict:
        """
        Extract metadata using regex patterns.
        
        Args:
            text: Full text of the book
            
        Returns:
            Dictionary with title, author, release_date
        """
        metadata = {}
        
        # Title - look for "Title:" pattern
        title_patterns = [
            r'Title:\s*(.+?)(?:\n|Author:)',
            r'Title:\s*(.+?)$'
        ]
        for pattern in title_patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if match:
                metadata["title"] = match.group(1).strip()
                break
        
        # Author - look for "Author:" pattern
        author_patterns = [
            r'Author:\s*(.+?)(?:\n|$)',
            r'by\s+(.+?)(?:\n|$)'
        ]
        for pattern in author_patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if match:
                author = match.group(1).strip()
                # Clean common suffixes
                author = re.sub(r'\[.*?\]', '', author).strip()
                metadata["author"] = author
                break
        
        # Release Date - look for "Release Date:" pattern
        date_patterns = [
            r'Release Date:\s*(.+?)(?:\[|$)',
            r'Posting Date:\s*(.+?)(?:\[|$)'
        ]
        for pattern in date_patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if match:
                metadata["release_date"] = match.group(1).strip()
                break
        
        return metadata
    
    def clean_content(self, text: str) -> str:
        """
        Remove Gutenberg headers and footers.
        
        Args:
            text: Full text including headers/footers
            
        Returns:
            Cleaned text content
        """
        # Find start marker
        start_markers = [
            "*** START OF THIS PROJECT GUTENBERG",
            "*** START OF THE PROJECT GUTENBERG",
            "*END*THE SMALL PRINT"
        ]
        
        start_pos = 0
        for marker in start_markers:
            pos = text.find(marker)
            if pos != -1:
                # Find end of this line
                start_pos = text.find('\n', pos) + 1
                break
        
        # Find end marker
        end_markers = [
            "*** END OF THIS PROJECT GUTENBERG",
            "*** END OF THE PROJECT GUTENBERG",
            "End of the Project Gutenberg"
        ]
        
        end_pos = len(text)
        for marker in end_markers:
            pos = text.find(marker)
            if pos != -1:
                end_pos = pos
                break
        
        # Extract content
        if start_pos > 0 and end_pos > start_pos:
            content = text[start_pos:end_pos].strip()
        else:
            # Fallback: just remove first 500 and last 500 chars
            logger.warning("Could not find markers, using fallback cleaning")
            content = text[500:-500].strip()
        
        # Additional cleaning
        content = re.sub(r'\r\n', '\n', content)  # Normalize line endings
        content = re.sub(r'\n{3,}', '\n\n', content)  # Remove excessive newlines
        
        return content