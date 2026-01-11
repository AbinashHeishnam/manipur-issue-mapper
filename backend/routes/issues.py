from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from backend.utils import db_utils
from ai.model import predict_issue

router = APIRouter(prefix="/api")

class IssueCreate(BaseModel):
    title: str
    category: str
    description: str
    latitude: float
    longitude: float
    user_id: int

# ---------- CREATE ISSUE ----------
@router.post("/issues/")
def create_issue(issue: IssueCreate):
    issue_id = db_utils.add_issue(
        title=issue.title,
        category=issue.category,
        description=issue.description,
        latitude=issue.latitude,
        longitude=issue.longitude,
        user_id=issue.user_id,
        ai_category=None,
        ai_severity=None
    )

    return {"status": "success", "issue_id": issue_id}

from typing import Optional

# ---------- GET ALL ISSUES ----------
@router.get("/issues/")
def get_issues(user_id: Optional[int] = None):
    return {"status": "success", "data": db_utils.fetch_issues(user_id)}

# ---------- GET SINGLE ISSUE ----------
@router.get("/issues/{issue_id}")
def get_issue(issue_id: int):
    row = db_utils.get_issue_by_id(issue_id)
    if not row:
        return {"status": "error", "message": "Issue not found"}

    return {
        "status": "success",
        "data": {
            "id": row["id"],
            "title": row["title"],
            "description": row["description"],
            "category": row["category"],
            "status": row.get("status") or "Pending",
            "approved_by_admin": row.get("approved_by_admin") or 0,
            "assigned_department": row.get("assigned_department") or "",
            "admin_comment": row.get("admin_comment") or "",
            "ai_category": row.get("ai_category") or "",
            "ai_severity": row.get("ai_severity") or 1,
            "timestamp": row.get("timestamp"),        # Must exist in DB
            "location": row.get("location") or "",   # Optional, if you store address
            "user_id": row.get("user_id"), # Added user_id
            "latitude": row.get("latitude"),
            "longitude": row.get("longitude")
        }
    }


# ---------- AI PREDICT ----------
@router.post("/issues/{issue_id}/predict")
def predict_issue_api(issue_id: int):
    issue = db_utils.get_issue_by_id(issue_id)
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")

    ai_category, ai_severity = predict_issue(
        issue["title"], issue["description"]
    )

    db_utils.update_ai_fields(issue_id, ai_category, ai_severity)

    return {
        "ai_category": ai_category,
        "ai_severity": ai_severity
    }
