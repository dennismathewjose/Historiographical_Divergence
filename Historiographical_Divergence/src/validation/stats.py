"""
Statistical Utilities for Validation.
Calculates Cohen's Kappa, Variance, and Standard Deviation.
"""
import numpy as np
from sklearn.metrics import cohen_kappa_score

def calculate_consistency_stats(scores: list) -> dict:
    """Calculates mean and standard deviation for a list of scores."""
    if not scores:
        return {"mean": 0, "std_dev": 0}
    return {
        "mean": np.mean(scores),
        "std_dev": np.std(scores),
        "variance": np.var(scores)
    }

def calculate_kappa(human_labels: list, llm_labels: list) -> float:
    """Calculates Cohen's Kappa between human and LLM labels."""
    # Ensure labels are aligned
    min_len = min(len(human_labels), len(llm_labels))
    return cohen_kappa_score(human_labels[:min_len], llm_labels[:min_len])