# ai/fraud.py
import os
import joblib
import re

ART_DIR = "ai/artifacts"
MODEL_PATH = os.path.join(ART_DIR, "fraud_model.pkl")
VECT_PATH = os.path.join(ART_DIR, "fraud_vectorizer.pkl")

SPAM_PATTERNS = [
    r"\bfree\s+money\b",
    r"\bclick\s+now\b",
    r"\bwin\s+\$?\d+\b",
    r"\bclaim\b",
    r"\bpromo\b",
    r"\bbonus\b",
    r"http[s]?://",
    r"\bwhatsapp\b",
    r"\btelegram\b",
    r"\bcall\s+now\b",
]

def _looks_like_gibberish(text: str) -> bool:
    """
    Flags random junk like: fsdhgfsdeh, asdfghjkl, qwertyuiop
    BUT won't flag real sentences.
    """
    t = (text or "").strip().lower()
    if not t:
        return True

    # If it's basically one "word" and long -> likely junk
    tokens = re.findall(r"[a-zA-Z]+", t)
    if len(tokens) == 1:
        w = tokens[0]
        if len(w) >= 9:
            vowels = sum(1 for c in w if c in "aeiou")
            vowel_ratio = vowels / max(len(w), 1)

            # very low vowels = common in random strings
            if vowel_ratio < 0.22:
                return True

            # long consonant run like "fsdhgfsd"
            if re.search(r"[bcdfghjklmnpqrstvwxyz]{6,}", w):
                return True

    # Too many non-letter symbols compared to letters
    letters = sum(ch.isalpha() for ch in t)
    nonspace = sum(not ch.isspace() for ch in t)
    if nonspace > 0 and letters / nonspace < 0.55:
        return True

    return False

def _basic_spam_heuristic(text: str) -> bool:
    t = (text or "").lower().strip()

    # 0) Empty or whitespace-only text
    if not t:
        return True

    # 1) Explicit spam keywords / links
    for pat in SPAM_PATTERNS:
        if re.search(pat, t):
            return True

    # 2) Repeated characters like "aaaaaaa" or "!!!!!!"
    if re.search(r"(.)\1{5,}", t):
        return True

    # 3) Gibberish detection (consonant soup)
    letters = re.sub(r"[^a-z]", "", t)

    if len(letters) >= 10:
        vowels = sum(1 for c in letters if c in "aeiou")
        vowel_ratio = vowels / len(letters)

        # very low vowel ratio → random mash
        if vowel_ratio < 0.25:
            return True

        # long consonant streak
        if re.search(r"[bcdfghjklmnpqrstvwxyz]{7,}", letters):
            return True

    # 4) Single long meaningless word
    words = re.findall(r"[a-z]+", t)
    if len(words) == 1 and len(words[0]) >= 10:
        return True

    # 5) Very short + no structure
    if len(t) < 12 and len(words) <= 1:
        return True

    return False


def predict_fraud(title: str, description: str, threshold: float = 0.65):
    """
    Returns: (is_spam: bool, spam_prob: float)
    - Uses ML if available
    - Falls back to heuristic if not
    """
    text = f"{title or ''} {description or ''}".strip()

    heuristic_hit = _basic_spam_heuristic(text)

    # if model not available, trust heuristic
    if not (os.path.exists(MODEL_PATH) and os.path.exists(VECT_PATH)):
        return (heuristic_hit, 1.0 if heuristic_hit else 0.0)

    try:
        model = joblib.load(MODEL_PATH)
        vectorizer = joblib.load(VECT_PATH)

        X_vec = vectorizer.transform([text])

        # prob(class=1) for spam
        prob_spam = float(model.predict_proba(X_vec)[0][1])

        is_spam = heuristic_hit or (prob_spam >= threshold)
        return (is_spam, prob_spam)

    except Exception:
        return (heuristic_hit, 1.0 if heuristic_hit else 0.0)
