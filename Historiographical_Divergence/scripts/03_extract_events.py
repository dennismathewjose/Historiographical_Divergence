"""
Phase 2 Execution: Event Extraction.
Reads clean datasets -> Runs LLM Extractor -> Saves structured claims.
"""
import json
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

from src.extraction.event_extractor import EventExtractor
from src.utils.logger import get_logger

logger = get_logger("pipeline_phase2")

def main():
    logger.info("PHASE 2: STARTING EVENT EXTRACTION")
    
    # Paths
    processed_dir = PROJECT_ROOT / "data" / "processed"
    extracted_dir = PROJECT_ROOT / "data" / "extracted"
    extracted_dir.mkdir(parents=True, exist_ok=True)
    
    # Load Datasets
    files = [
        processed_dir / "loc_dataset_clean.json",
        processed_dir / "gutenberg_dataset.json"
    ]
    
    all_documents = []
    for f in files:
        if f.exists():
            with open(f, 'r', encoding='utf-8') as file:
                all_documents.extend(json.load(file))
        else:
            logger.warning(f"File not found: {f}")

    logger.info(f"Loaded {len(all_documents)} documents to process.")
    
    # Run Extraction
    extractor = EventExtractor()
    all_extractions = []
    
    for i, doc in enumerate(all_documents, 1):
        logger.info(f"Processing {i}/{len(all_documents)}: {doc.get('title')}")
        events = extractor.process_document(doc)
        all_extractions.extend(events)
        
    # Save Results
    output_path = extracted_dir / "extracted_events.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(all_extractions, f, indent=2, ensure_ascii=False)
        
    logger.info(f"✓ Extraction Complete. Saved {len(all_extractions)} event records to {output_path}")

if __name__ == "__main__":
    main()