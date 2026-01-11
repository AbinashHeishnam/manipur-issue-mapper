from ai.preprocessor import build_risk_score
from ai.model import classify_zone

def predict_zone(issue: dict) -> dict:
    score = build_risk_score(issue)
    zone = classify_zone(score)

    return {
        "zone": zone,
        "risk_score": round(score, 2)
    }
