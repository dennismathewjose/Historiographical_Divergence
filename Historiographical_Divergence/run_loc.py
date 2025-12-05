# run_loc.py
from src.scraping.loc_scraper import main

if __name__ == "__main__":
    try:
        main()
    except ImportError:
        # Fallback if main() isn't importable (older version of file)
        from src.scraping.loc_scraper import LoCScraper
        import json
        from pathlib import Path
        
        print("Fallback: Running manual execution...")
        base_dir = Path("data")
        scraper = LoCScraper(output_dir=base_dir / "raw" / "loc")
        docs = scraper.scrape_all()
        
        out_path = base_dir / "processed" / "loc_dataset.json"
        out_path.parent.mkdir(exist_ok=True, parents=True)
        
        with open(out_path, "w") as f:
            json.dump(docs, f, indent=2)
            
        print(f"Saved to {out_path}")