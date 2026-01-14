# ai/veracity.py
import os
import re
import joblib

ART_DIR = "ai/artifacts"
MODEL_PATH = os.path.join(ART_DIR, "veracity_model.pkl")
VECT_PATH  = os.path.join(ART_DIR, "veracity_vectorizer.pkl")

# cache in memory (fast, prevents reloading every request)
_MODEL = None
_VECT = None

LABEL_INV = {0: "legit", 1: "fake", 2: "spam"}

def _load():
    global _MODEL, _VECT
    if _MODEL is not None and _VECT is not None:
        return _MODEL, _VECT

    if not (os.path.exists(MODEL_PATH) and os.path.exists(VECT_PATH)):
        raise FileNotFoundError(
            f"Veracity model not found. Expected:\n- {MODEL_PATH}\n- {VECT_PATH}"
        )

    _MODEL = joblib.load(MODEL_PATH)
    _VECT  = joblib.load(VECT_PATH)
    return _MODEL, _VECT

def _is_gibberish(text: str) -> bool:
    t = (text or "").strip().lower()
    if len(t) < 8:
        return True
    # repeated same char like "aaaaaaa" "!!!!!"
    if re.search(r"(.)\1{5,}", t):
        return True
    # mostly non-letters
    letters = sum(ch.isalpha() for ch in t)
    if letters / max(len(t), 1) < 0.35:
        return True
    return False

def predict_veracity_score(title: str, description: str) -> float:
    """
    Returns probability of "fake" (0..1).
    """
    model, vect = _load()
    text = f"{title or ''} {description or ''}".strip()
    X = vect.transform([text])

    # Predict probabilities across 3 classes [legit, fake, spam]
    proba = model.predict_proba(X)[0]

    # fake class index = 1
    return float(proba[1])

def predict_veracity(title: str, description: str, min_conf: float = 0.55):
    """
    Returns: (verdict, score_false, is_suspicious)

    verdict: legit | fake | spam | unknown
    score_false: probability of fake (0..1)
    is_suspicious: 0/1 for admin attention
    """
    model, vect = _load()
    text = f"{title or ''} {description or ''}".strip()

    X = vect.transform([text])
    proba = model.predict_proba(X)[0]  # [p_legit, p_fake, p_spam]

    best_idx = int(proba.argmax())
    best_prob = float(proba[best_idx])

    # base label
    label = LABEL_INV.get(best_idx, "unknown")

    # if low confidence, mark unknown
    if best_prob < min_conf:
        label = "unknown"

    score_false = float(proba[1])

    # suspicious logic (admin review)
    is_susp = 0
    if label in ("fake", "spam"):
        is_susp = 1
    if _is_gibberish(text):
        # junk report -> suspicious even if unknown
        is_susp = 1
        if label == "legit":
            label = "unknown"

    return label, score_false, is_susp
