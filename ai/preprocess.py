def build_risk_score(issue: dict) -> float:
    score = 0.0

    # Severity weight
    severity_map = {
        "Low": 1,
        "Medium": 2,
        "High": 3
    }
    score += severity_map.get(issue.get("severity", "Low"), 1)

    # Category weight
    category_map = {
        "Road": 1.5,
        "Water": 2.0,
        "Electricity": 2.5
    }
    score += category_map.get(issue.get("category"), 1)

    # Recent issue boost (optional)
    if issue.get("recent_reports", 0) > 3:
        score += 1

    return score
# ai/preprocess.py

import re
import string

def clean_text(text: str) -> str:
    """
    Basic cleaning: lowercase, remove punctuation, extra spaces.
    """
    text = text.lower()
    text = re.sub(f"[{re.escape(string.punctuation)}]", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()
