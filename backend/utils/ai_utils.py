from ai.preprocess import build_risk_score
from ai.model import classify_zone

def apply_ai_zoning(issue: dict) -> dict:
    score = build_risk_score(issue)
    zone = classify_zone(score)

    issue["risk_score"] = round(score, 2)
    issue["zone"] = zone

    return issue
