from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel
from backend.utils.db_utils import fetch_issues, get_issue_by_id, get_connection

router = APIRouter(prefix="/api/admin", tags=["Admin"])

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"
ADMIN_TOKEN = "hackathon-token-123456"

# ---- Admin Login ----
class AdminLoginRequest(BaseModel):
    username: str
    password: str

@router.post("/login")
def admin_login(data: AdminLoginRequest):
    if data.username == ADMIN_USERNAME and data.password == ADMIN_PASSWORD:
        return {"status": "success", "token": ADMIN_TOKEN}
    raise HTTPException(status_code=401, detail="Invalid credentials")

# ---- Get All Issues ----
@router.get("/issues")
def admin_get_all_issues(authorization: str | None = Header(None)):
    if authorization != f"Bearer {ADMIN_TOKEN}":
        raise HTTPException(status_code=401, detail="Unauthorized")
    return {"status": "success", "issues": fetch_issues()}

# ---- Approve/Reject Issue ----
class ApproveIssueRequest(BaseModel):
    approved: bool | None = None        # True=Approve, False=Reject, None=No action
    department: str | None = None
    admin_comment: str | None = None

@router.post("/issues/{issue_id}/approve")
def admin_approve_issue(issue_id: int, data: ApproveIssueRequest, authorization: str | None = Header(None)):
    if authorization != f"Bearer {ADMIN_TOKEN}":
        raise HTTPException(status_code=401, detail="Unauthorized")

    issue = get_issue_by_id(issue_id)
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")

    # ---------------- ENUM-SAFE STATUS ----------------
    new_status = issue["status"]  # keep current if nothing changes

    if data.approved is True:
        new_status = "In Progress"      # approved
    elif data.approved is False:
        new_status = "Rejected"         # permanent rejection

    # Debug log
    print("ADMIN UPDATE →", issue_id, data.approved, new_status, data.department)

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE issues
        SET
            approved_by_admin=%s,
            assigned_department=%s,
            admin_comment=%s,
            status=%s
        WHERE id=%s
    """, (
        1 if data.approved else 0 if data.approved is not None else issue["approved_by_admin"],
        data.department if data.department is not None else issue["assigned_department"],
        data.admin_comment if data.admin_comment is not None else issue["admin_comment"],
        new_status,
        issue_id
    ))
    conn.commit()
    cursor.close()
    conn.close()

    return {"status": "success", "message": "Issue updated successfully"}
