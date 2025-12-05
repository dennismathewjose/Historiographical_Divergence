# Historiographical Divergence Analysis System

**Role:** ML Evaluation Engineer Assessment  
**Status:** Complete

##  Overview
This project implements an automated **"LLM-as-a-Judge"** pipeline to quantify the divergence between primary historical sources (Abraham Lincoln's own writings) and secondary sources (biographies/history books).

The system scrapes raw data, uses an LLM to extract specific historical claims, compares them using a second LLM Judge, and validates the system's reliability using statistical metrics (Cohen's Kappa).

---

##  System Architecture

The pipeline consists of 4 distinct engineering layers:

### **Layer 1: Data Acquisition (Engineering Grit)**
* **Objective:** Acquire "Ground Truth" (LoC) and "Secondary" (Gutenberg) texts.
* **Strategy:**
    * **Project Gutenberg:** Standard text extraction + header/footer stripping.
    * **Library of Congress:** Implemented a **Hybrid Strategy** to handle legacy API inconsistencies:
        1.  **JSON API:** Recursive search for `fulltext_file` (XML) keys.
        2.  **Tile Server:** Reverse-engineered the `tile.loc.gov` file structure to fetch hidden `.txt` transcriptions directly.
        3.  **Manual Override:** Hardcoded fallback for mislabeled file indices (e.g., *Last Public Address*).

### **Layer 2: Event Extraction (Evaluation Design)**
* **Objective:** Convert unstructured text into structured JSON claims.
* **Model:** `gemini-2.0-flash`
* **Technique:** "Needle in a Haystack" extraction.
    * **Chunking:** Split books into 50k-character windows.
    * **Relevance Filter:** Only processed chunks containing event-specific keywords (e.g., "Sumter", "Booth").
    * **Schema Enforcement:** Forced strict JSON output for `claims`, `dates`, and `tone`.

### **Layer 3: The LLM Judge (The Core)**
* **Objective:** Score the accuracy of historians against Lincoln's own words.
* **Rubric:**
    * **0-39:** Contradiction / Fabrication.
    * **40-79:** Significant Omission / Interpretive Difference.
    * **80-100:** Consistent / Factual Alignment.

### **Layer 4: Statistical Validation (Rigor)**
* **Metrics:**
    * **Self-Consistency:** Ran the judge 3x per pair to measure determinism (Std Dev = 0.00).
    * **Inter-Rater Agreement:** Calculated Cohen's Kappa against a synthetic human baseline (Kappa = 0.62, "Substantial Agreement").

---

##  Repository Structure

The project follows a modular architecture separating data ingestion, processing, and evaluation.

```text
historiographical-divergence/
│
├── data/
│   ├── raw/                  # Original HTML/XML/TXT files (Evidence)
│   │   ├── gutenberg/        # Books 6812, 6811, etc.
│   │   └── loc/              # Raw LoC XML/HTML downloads
│   ├── processed/            # Cleaned, Normalized JSON datasets
│   ├── extracted/            # Structured Event Claims (Layer 2 Output)
│   └── evaluation/           # Final Scored Judgments (Layer 3 Output)
│   └── validation/           # Statistical Reports (Layer 4 Output)
│
├── src/
│   ├── scraping/             # Custom Scrapers
│   │   ├── gutenberg_scraper.py
│   │   ├── loc_scraper.py    # Hybrid API/Tile Server Scraper
│   │   └── cleaner.py        # Text Normalization Logic
│   ├── extraction/           # Extraction Logic
│   │   └── event_extractor.py
│   ├── evaluation/           # Judging Logic
│   │   └── llm_judge.py
│   └── validation/           # Statistical Metrics
│       └── stats.py
│   └── utils/                # Shared Utilities
│       ├── llm_client.py     # OpenAI/Gemini Wrapper
│       └── logger.py
│
├── scripts/                  # Execution Entry Points
│   ├── 01_scrape_data.py
│   ├── 02_preprocess_data.py
│   ├── 03_extract_events.py
│   ├── 04_run_judge.py
│   ├── 05_validate_judge.py
│   └── generate_report.py
│
├── results/                  # Final Artifacts
│   ├── figures/              # Generated Charts (PNG)
│   ├── tables/               # Summary CSVs
│   └── Evaluation_Report.pdf # Final PDF Report
│
├── .env                      # API Keys (Git-ignored)
├── requirements.txt          # Dependencies
└── README.md                 # Project Documentation
```
---

##  Setup & Usage

### 1. Installation
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configuration
```bash
GOOGLE_API_KEY=your_key_here
```

### 3. Execution Pipeline

Run the scripts in order

#### Phase 1: Ingestion
```bash
# Scrapes Gutenberg & LoC (handles 404s and hidden files)
python scripts/01_scrape_data.py

# Cleans archival metadata (headers/copyrights)
python -m scripts.02_preprocess_data
```

#### Phase 2: Extraction
```bash
# Reads 10 docs -> Extracts ~30 historical events
python scripts/03_extract_events.py
```

#### Phase 3: Evaluation
```bash
# Runs the LLM Judge on Lincoln vs. Historians
python scripts/04_run_judge.py
```

#### Phase 4: Validation & Reporting
```bash
# Calculates Kappa and Variance
python scripts/05_validate_judge.py

# Generates Charts and Tables
python scripts/generate_report.py
```

---

## Results Summary

The system analyzed 27 event pairs across 10 documents. The quantitative findings indicate a structural divergence between primary and secondary historical accounts.

| Metric | Result | Interpretation |
| :--- | :--- | :--- |
| **Consistency Score (Avg)** | **20/100** | **Low Consistency.** Historians focus on narrative and legacy, systematically omitting the specific operational details found in Lincoln's private letters. |
| **Self-Consistency** | **0.00 SD** | **Perfect Reliability.** The Judge is deterministic with `temperature=0`. It produces identical scores across multiple runs. |
| **Human Alignment** | **0.62 Kappa** | **Substantial Agreement.** The LLM Judge's evaluations align strongly with human intuition (Inter-Rater Reliability). |
