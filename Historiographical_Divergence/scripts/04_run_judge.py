"""
Phase 3 Execution: The LLM Judge.
Reads extracted events -> Runs Comparison Logic -> Saves Scores.
"""
import json
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

from src.evaluation.llm_judge import LLMJudge
from src.utils.logger import get_logger

logger = get_logger("pipeline_phase3")

def main():
    logger.info("PHASE 3: STARTING LLM JUDGE")
    
    # Paths
    extracted_path = PROJECT_ROOT / "data" / "extracted" / "extracted_events.json"
    evaluation_dir = PROJECT_ROOT / "data" / "evaluation"
    evaluation_dir.mkdir(parents=True, exist_ok=True)
    
    if not extracted_path.exists():
        logger.error("Extracted events file not found. Run Phase 2 first.")
        return

    # Load Data
    with open(extracted_path, 'r', encoding='utf-8') as f:
        extractions = json.load(f)
    
    logger.info(f"Loaded {len(extractions)} extracted claims.")
    
    # Run Judge
    judge = LLMJudge()
    judgments = judge.judge_all(extractions)
    
    # Save Results
    output_path = evaluation_dir / "judge_results.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(judgments, f, indent=2, ensure_ascii=False)
        
    logger.info(f"✓ Judging Complete. Generated {len(judgments)} evaluations.")
    logger.info(f"Results saved to: {output_path}")

if __name__ == "__main__":
    main()