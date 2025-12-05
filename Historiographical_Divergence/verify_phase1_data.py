#!/usr/bin/env python3
"""
Verify Phase 1 (1A + 1B) data quality before proceeding to Phase 2.
"""
import json
from pathlib import Path

def verify_gutenberg():
    """Check Gutenberg dataset."""
    print("="*60)
    print("VERIFYING GUTENBERG DATASET")
    print("="*60)
    
    path = Path("data/processed/gutenberg_dataset.json")
    if not path.exists():
        print("✗ gutenberg_dataset.json not found!")
        return False
    
    with open(path) as f:
        books = json.load(f)
    
    print(f"\nFound {len(books)} books")
    
    for book in books:
        print(f"\n{book['id']}:")
        print(f"  Title: {book['title']}")
        print(f"  Author: {book['author']}")
        print(f"  Content: {len(book['content']):,} chars")
        
        # Validation
        if len(book['content']) < 50000:
            print(f"  ⚠️  Warning: Book seems short")
        else:
            print(f"  ✓ Good length")
    
    print(f"\n✓ Gutenberg dataset valid: {len(books)} books")
    return True

def verify_loc():
    """Check LoC dataset."""
    print("\n" + "="*60)
    print("VERIFYING LOC DATASET")
    print("="*60)
    
    path = Path("data/processed/loc_dataset.json")
    if not path.exists():
        print("✗ loc_dataset.json not found!")
        return False
    
    with open(path) as f:
        docs = json.load(f)
    
    print(f"\nFound {len(docs)} documents")
    
    issues = []
    
    for doc in docs:
        print(f"\n{doc['id']}:")
        print(f"  Title: {doc['title']}")
        print(f"  Type: {doc['document_type']}")
        print(f"  Date: {doc['date']}")
        print(f"  Content: {len(doc['content']):,} chars")
        
        # Check for issues
        if len(doc['content']) < 200:
            print(f"  ✗ ISSUE: Content too short!")
            issues.append((doc['id'], "Content too short"))
        elif "could not be extracted" in doc['content']:
            print(f"  ✗ ISSUE: Extraction failed!")
            issues.append((doc['id'], "Extraction failed"))
        elif "Four score" in doc['content']:
            print(f"  ✓ Gettysburg Address found!")
        else:
            print(f"  ✓ Content present")
        
        # Show preview
        preview = doc['content'][:150].replace('\n', ' ')
        print(f"  Preview: {preview}...")
    
    if issues:
        print(f"\n✗ {len(issues)} issues found:")
        for doc_id, issue in issues:
            print(f"  - {doc_id}: {issue}")
        return False
    else:
        print(f"\n✓ LoC dataset valid: {len(docs)} documents")
        return True

def check_raw_files():
    """Check raw files were saved."""
    print("\n" + "="*60)
    print("CHECKING RAW FILES")
    print("="*60)
    
    gutenberg_dir = Path("data/raw/gutenberg")
    loc_dir = Path("data/raw/loc")
    
    gutenberg_files = list(gutenberg_dir.glob("*.txt"))
    loc_files = list(loc_dir.glob("*.html"))
    
    print(f"\nGutenberg raw files: {len(gutenberg_files)}")
    print(f"LoC raw files: {len(loc_files)}")
    
    if len(gutenberg_files) >= 5:
        print("✓ Gutenberg raw files saved")
    else:
        print("⚠️  Some Gutenberg raw files missing")
    
    if len(loc_files) >= 5:
        print("✓ LoC raw files saved")
    else:
        print("⚠️  Some LoC raw files missing")

def main():
    """Run all verifications."""
    print("\n" + "="*60)
    print("PHASE 1 DATA VERIFICATION")
    print("="*60)
    
    gutenberg_ok = verify_gutenberg()
    loc_ok = verify_loc()
    check_raw_files()
    
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    
    if gutenberg_ok and loc_ok:
        print("✓ PHASE 1 COMPLETE!")
        print("\nReady for Phase 2: Event Extraction")
        print("\nNext steps:")
        print("1. Create LLM client (Phase 2A)")
        print("2. Build event extractor (Phase 2B)")
        print("3. Run extraction pipeline (Phase 2C)")
        return 0
    else:
        print("✗ Issues found - fix before proceeding")
        return 1

if __name__ == "__main__":
    exit(main())