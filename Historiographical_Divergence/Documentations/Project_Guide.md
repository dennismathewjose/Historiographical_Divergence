# Historiographical Divergence Analysis System - Project Documentation

## 1. Overview
This project builds an automated pipeline to analyze how historical events are described differently in primary sources (Abraham Lincoln's writings) versus secondary sources (biographies). It uses Large Language Models (LLMs) to extract claims and judge their consistency.

**Core Tech Stack:** Python 3.9+, Google Gemini 2.0 Flash, scikit-learn, Pandas, Matplotlib.

## 2. Phase-by-Phase Implementation

### **Phase 1: Data Acquisition (Engineering Grit)**
**Goal:** Acquire clean text from difficult sources without manual downloading.

* **Scrapers Built:**
    * `GutenbergScraper`: Handles dynamic URL patterns for Project Gutenberg books.
    * `LoCScraper`: A robust, multi-strategy scraper for the Library of Congress.
* **Key Innovation:** The LoC scraper implements a **Hybrid Strategy**:
    1.  **JSON API:** Recursively searches metadata for `fulltext_file` keys.
    2.  **Tile Server Hack:** Reverse-engineers the `tile.loc.gov` URL pattern to find hidden `.txt` files.
    3.  **Manual Fallback:** Includes a "Golden Record" text for documents with broken digital paths.
* **Outcome:** 100% success rate in acquiring the 5 required Lincoln documents and 5 history books.

### **Phase 2: Event Extraction (Evaluation Design)**
**Goal:** Convert unstructured text into structured data.

* **Model:** `gemini-2.0-flash` (Chosen for its massive 1M+ token context window).
* **Architecture:**
    * **Chunking:** Splits books into 50,000-character overlapping windows.
    * **Filtering:** Only processes chunks containing event-specific keywords (e.g., "Sumter", "Booth").
    * **Schema:** Forces the LLM to output strict JSON:
        ```json
        {
          "claims": ["claim 1", "claim 2"],
          "temporal_details": {"date": "YYYY-MM-DD"},
          "tone": "objective"
        }
        ```
* **Outcome:** Extracted ~30 relevant event records from over 1 million tokens of raw text.

### **Phase 3: The LLM Judge (The Core)**
**Goal:** Quantify the agreement between sources.

* **Logic:**
    1.  Groups extractions by Event (e.g., "Gettysburg Address").
    2.  Identifies "Source Zero" (Lincoln's account).
    3.  Pairs every Historian against Lincoln.
* **Prompt Engineering:** Uses a specific rubric to guide the LLM:
    * **Consistency Score (0-100):** Quantitative measure of agreement.
    * **Classification:** Labels differences as *Factual Error*, *Interpretive Difference*, or *Omission*.
* **Outcome:** Generated detailed judgment reports for all valid pairs.

### **Phase 4: Statistical Validation (Rigor)**
**Goal:** Prove the system is trustworthy.

* **Experiment 1: Self-Consistency**
    * *Method:* Ran the judge 3 times on the same data with `temperature=0`.
    * *Result:* **Standard Deviation = 0.00**. The system is deterministic.
* **Experiment 2: Inter-Rater Agreement**
    * *Method:* Compared LLM scores against human labels using Cohen's Kappa.
    * *Result:* **Kappa = 0.62** (Substantial Agreement).

## 3. Repository Structure
```text
project/
├── data/
│   ├── raw/            # Original HTML/XML/TXT files
│   ├── processed/      # Normalized JSON datasets
│   ├── extracted/      # LLM-extracted claims
│   └── evaluation/     # Final scores and judgments
├── src/
│   ├── scraping/       # Scraper logic
│   ├── extraction/     # LLM extraction logic
│   ├── evaluation/     # Judge logic
│   └── validation/     # Statistical tests
├── scripts/            # Execution entry points
└── results/            # Final charts and tables