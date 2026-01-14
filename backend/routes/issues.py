# backend/routes/issues.py
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional
from backend.utils import db_utils

from ai.model import predict_issue
from ai.fraud import predict_fraud
from ai.veracity import predict_veracity

import re

router = APIRouter(prefix="/api")


# ---------------------- MODELS ----------------------
class IssueCreate(BaseModel):
    title: str
    category: str
    description: str
    latitude: float
    longitude: float
    user_id: int


# ---------------------- HELPERS ----------------------
def safe_predict_veracity(title: str, description: str):
    """
    Never crash the API if veracity model is missing/not trained.
    Returns: (verdict, score_false, is_suspicious)
    """
    try:
        verdict, score_false, is_susp = predict_veracity(title, description)
        verdict = verdict or "unknown"
        score_false = float(score_false or 0.0)
        is_susp = int(is_susp or 0)
        return verdict, score_false, is_susp
    except FileNotFoundError:
        return "unknown", 0.0, 0
    except Exception:
        return "unknown", 0.0, 0


def safe_predict_spam(title: str, description: str):
    """
    Always returns (is_spam: bool, spam_prob: float)
    Never crashes.
    """
    try:
        is_spam, prob = predict_fraud(title, description)
        return bool(is_spam), float(prob or 0.0)
    except Exception:
        return False, 0.0


# ---------------------- MISMATCH / GIBBERISH GUARD ----------------------
CATEGORY_KEYWORDS = {
    "Road": {"road", "pothole", "bridge", "traffic", "accident", "highway", "street", "lane", "damaged"},
    "Water": {"water", "pipe", "leak", "leakage", "supply", "tap", "drain", "drainage", "sewage"},
    "Electricity": {"power", "electric", "electricity", "voltage", "transformer", "wire", "outage", "cut"},
    "Sanitation": {"garbage", "waste", "dirty", "smell", "toilet", "sanitation", "drain", "cleanup"},
    "Law": {"theft", "fight", "violence", "crime", "police", "assault", "harassment", "illegal"},
}


def _normalize_tokens(text: str):
    text = (text or "").lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    toks = [t for t in text.split() if len(t) >= 3]
    return toks


def _is_gibberish(text: str) -> bool:
    t = (text or "").strip()
    if not t:
        return True
    if len(t) < 8:
        return True

    toks = _normalize_tokens(t)
    if len(toks) == 0:
        return True

    vowel = set("aeiou")

    def token_vowel_ratio(tok: str):
        v = sum(1 for c in tok if c in vowel)
        return v / max(len(tok), 1)

    bad = 0
    for tok in toks[:20]:
        if token_vowel_ratio(tok) < 0.20:  # like "fsdhgfsdeh"
            bad += 1

    if bad / max(len(toks[:20]), 1) >= 0.60:
        return True

    if re.search(r"(.)\1{5,}", t.lower()):
        return True

    return False


def _title_desc_mismatch(title: str, desc: str) -> bool:
    t_tokens = set(_normalize_tokens(title))
    d_tokens = set(_normalize_tokens(desc))

    # Title looks normal but desc is gibberish/empty
    if (not _is_gibberish(title)) and _is_gibberish(desc):
        return True

    # Low overlap between title and desc
    if len(t_tokens) >= 2 and len(d_tokens) >= 4:
        overlap = len(t_tokens.intersection(d_tokens))
        if overlap / max(len(t_tokens), 1) < 0.15:
            return True

    return False


def _category_mismatch(category: str, title: str, desc: str) -> bool:
    cat = (category or "").strip()
    if not cat or cat not in CATEGORY_KEYWORDS:
        return False

    tokens = set(_normalize_tokens(f"{title} {desc}"))
    kws = CATEGORY_KEYWORDS[cat]

    hit = len(tokens.intersection(kws))
    if hit >= 1:
        return False

    other_hits = {
        c: len(tokens.intersection(kw))
        for c, kw in CATEGORY_KEYWORDS.items()
        if c != cat
    }
    best_other = max(other_hits.values()) if other_hits else 0

    if best_other >= 2:
        return True

    return False


def mismatch_guard(title: str, desc: str, category: str):
    """
    Returns: (is_mismatch: bool, reasons: list[str], force_spam: bool)

    force_spam triggers only in high-confidence bot patterns:
    - gibberish title + meaningful description
    """
    reasons = []
    force_spam = False

    title_gib = _is_gibberish(title)
    desc_gib = _is_gibberish(desc)

    # ✅ NEW RULE: title gibberish + description real => spam
    if title_gib and not desc_gib:
        reasons.append("gibberish_title_real_description")
        force_spam = True
        return True, reasons, force_spam

    if _title_desc_mismatch(title, desc):
        reasons.append("title_desc_mismatch")

    if _category_mismatch(category, title, desc):
        reasons.append("category_mismatch")

    if not title_gib and (desc or "").strip() and len((desc or "").strip()) < 12:
        reasons.append("description_too_short")

    return (len(reasons) > 0), reasons, force_spam


# ---------------------- CREATE ISSUE ----------------------
@router.post("/issues/")
def create_issue(issue: IssueCreate):
    """
    Creates a new issue.
    We DO NOT reject automatically.
    We only tag it as suspicious/legit/unknown/spam for admin review.
    """

    # 1) Veracity model
    verdict, score_false, is_susp = safe_predict_veracity(issue.title, issue.description)

    # 2) Spam detector (optional override)
    is_spam, spam_prob = safe_predict_spam(issue.title, issue.description)
    if is_spam:
        verdict = "spam"
        is_susp = 1

    # 3) Title/Description/Category mismatch guard
    is_mismatch, reasons, force_spam = mismatch_guard(issue.title, issue.description, issue.category)

    # ✅ force_spam has priority (but still NO auto-reject, only tag)
    if force_spam:
        verdict = "spam"
        is_susp = 1
    elif is_mismatch:
        if verdict != "spam":
            if verdict == "legit":
                verdict = "fake"
            else:
                verdict = verdict or "unknown"
        is_susp = 1

    issue_id = db_utils.add_issue(
        title=issue.title,
        category=issue.category,
        description=issue.description,
        latitude=issue.latitude,
        longitude=issue.longitude,
        user_id=issue.user_id,
        ai_category=None,
        ai_severity=None,
        ai_veracity=verdict,
        is_suspicious=int(is_susp),
    )

    return {
        "status": "success",
        "issue_id": issue_id,
        "ai_veracity": verdict,
        "is_suspicious": int(is_susp),
        "score_false": float(score_false),
        "spam_prob": float(spam_prob),
        "mismatch_reasons": reasons,
    }


# ---------------------- GET ALL ISSUES ----------------------
@router.get("/issues/")
def get_issues(user_id: Optional[int] = None):
    return {"status": "success", "data": db_utils.fetch_issues(user_id)}


# ---------------------- GET NEARBY ISSUES ----------------------
@router.get("/issues/nearby")
def get_nearby_issues(
    lat: float = Query(..., description="Latitude of user"),
    lng: float = Query(..., description="Longitude of user"),
    radius: float = Query(0.5, description="Radius in km"),
):
    nearby = db_utils.fetch_nearby_issues(lat, lng, radius)
    return {
        "status": "success",
        "count": len(nearby),
        "data": nearby,
        "issues": nearby,
    }


# ---------------------- GET SINGLE ISSUE ----------------------
@router.get("/issues/{issue_id}")
def get_issue(issue_id: int):
    row = db_utils.get_issue_by_id(issue_id)
    if not row:
        raise HTTPException(status_code=404, detail="Issue not found")

    return {
        "status": "success",
        "data": {
            "id": row["id"],
            "title": row["title"],
            "description": row.get("description") or "",
            "category": row.get("category") or "",
            "status": row.get("status") or "Pending",
            "approved_by_admin": row.get("approved_by_admin") or 0,
            "assigned_department": row.get("assigned_department") or "",
            "admin_comment": row.get("admin_comment") or "",
            "ai_category": row.get("ai_category") or "",
            "ai_severity": row.get("ai_severity") or 1,
            "ai_veracity": row.get("ai_veracity") or "unknown",
            "is_suspicious": int(row.get("is_suspicious") or 0),
            "timestamp": row.get("timestamp"),
            "location": row.get("location") or "",
            "user_id": row.get("user_id"),
            "user_name": row.get("user_name"),
            "user_mobile": row.get("user_mobile"),
            "user_email": row.get("user_email"),
            "latitude": row.get("latitude"),
            "longitude": row.get("longitude"),
        }
    }


# ---------------------- AI PREDICT CATEGORY + SEVERITY ----------------------
@router.post("/issues/{issue_id}/predict")
def predict_issue_api(issue_id: int):
    issue = db_utils.get_issue_by_id(issue_id)
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")

    ai_category, ai_severity = predict_issue(issue["title"], issue["description"])
    db_utils.update_ai_fields(issue_id, ai_category, ai_severity)

    return {"ai_category": ai_category, "ai_severity": ai_severity}


# ---------------------- SUBMIT ISSUE (NO AUTO-REJECT) ----------------------
@router.post("/submit")
async def submit_issue(issue: IssueCreate):
    """
    Same as create_issue but kept for compatibility.
    IMPORTANT: no auto-reject. Admin will reject if suspicious.
    """

    verdict, score_false, is_susp = safe_predict_veracity(issue.title, issue.description)

    is_spam, spam_prob = safe_predict_spam(issue.title, issue.description)
    if is_spam:
        verdict = "spam"
        is_susp = 1

    is_mismatch, reasons, force_spam = mismatch_guard(issue.title, issue.description, issue.category)

    if force_spam:
        verdict = "spam"
        is_susp = 1
    elif is_mismatch:
        if verdict != "spam":
            if verdict == "legit":
                verdict = "fake"
        is_susp = 1

    issue_id = db_utils.add_issue(
        title=issue.title,
        category=issue.category,
        description=issue.description,
        latitude=issue.latitude,
        longitude=issue.longitude,
        user_id=issue.user_id,
        ai_category=None,
        ai_severity=None,
        ai_veracity=verdict,
        is_suspicious=int(is_susp),
    )

    return {
        "status": "success",
        "message": "Issue submitted successfully",
        "issue_id": issue_id,
        "ai_veracity": verdict,
        "is_suspicious": int(is_susp),
        "score_false": float(score_false),
        "spam_prob": float(spam_prob),
        "mismatch_reasons": reasons,
    }
