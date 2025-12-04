"""
Utilities for loading and saving JSON data.
"""
import json
from pathlib import Path
from typing import Any, List, Dict
from src.utils.logger import get_logger

logger = get_logger(__name__)


def load_json(filepath: Path) -> Any:
    """Load JSON data from file."""
    logger.info(f"Loading JSON from {filepath}")
    
    if not filepath.exists():
        raise FileNotFoundError(f"File not found: {filepath}")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    logger.info(f"Successfully loaded {len(data) if isinstance(data, list) else 'JSON'} from {filepath}")
    return data


def save_json(data: Any, filepath: Path, indent: int = 2) -> None:
    """Save data to JSON file."""
    logger.info(f"Saving JSON to {filepath}")
    filepath.parent.mkdir(parents=True, exist_ok=True)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=indent, ensure_ascii=False)
    
    logger.info(f"Successfully saved to {filepath}")


def validate_document_schema(document: Dict) -> bool:
    """Validate document has required fields."""
    required = ["id", "title", "reference", "document_type", "content"]
    for field in required:
        if field not in document or not document[field]:
            logger.warning(f"Document missing/empty field: {field}")
            return False
    return True