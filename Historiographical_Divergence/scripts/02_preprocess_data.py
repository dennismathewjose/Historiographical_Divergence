# scripts/02_preprocess_data.py

import json
from pathlib import Path
from src.scraping.cleaner import clean_loc_content
from src.utils.logger import get_logger

logger = get_logger("preprocessor")

def main():
    base_dir = Path("data")
    input_path = base_dir / "processed" / "loc_dataset.json"
    output_path = base_dir / "processed" / "loc_dataset_clean.json"
    
    if not input_path.exists():
        logger.error(f"Input file not found: {input_path}")
        return

    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    logger.info(f"Preprocessing {len(data)} documents...")
    
    cleaned_data = []
    for doc in data:
        original_len = len(doc.get('content', ''))
        
        # Apply cleaning
        clean_text = clean_loc_content(
            doc_type=doc.get('document_type', 'Text'),
            content=doc.get('content', ''),
            title=doc.get('title', '')
        )
        
        doc['content'] = clean_text
        cleaned_data.append(doc)
        
        new_len = len(clean_text)
        reduction = original_len - new_len
        logger.info(f"Cleaned '{doc['title']}': {original_len} -> {new_len} chars (Removed {reduction})")

    # Save
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(cleaned_data, f, indent=2, ensure_ascii=False)
        
    logger.info(f"✓ Saved clean dataset to {output_path}")

if __name__ == "__main__":
    main()