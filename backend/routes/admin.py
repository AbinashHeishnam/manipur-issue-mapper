from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel
from backend.utils.db_utils import (
    fetch_issues,
    get_issue_by_id,
    get_connection
)
import bcrypt
import uuid

router = APIRouter(prefix="/api/admin", tags=["Admin"])

# In-memory token store (MVP-safe)
ADMIN_TOKENS = {}

# ---------------- Models ----------------
class AdminLoginRequest(BaseModel):
    username: str
    password: str

# ---------------- Admin Login ----------------
@router.post("/login")
def admin_login(data: AdminLoginRequest):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        "SELECT * FROM admins WHERE username=%s",
        (data.username,)
    )
    admin = cursor.fetchone()

    cursor.close()
    conn.close()

    if not admin:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not bcrypt.checkpw(
        data.password.encode(),
        admin["password_hash"].encode()
    ):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = f"admin-token-{uuid.uuid4()}"
    ADMIN_TOKENS[token] = admin["username"]

    return {"status": "success", "token": token}

# ---------------- Auth Guard ----------------
def verify_admin_token(authorization: str | None):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Unauthorized")

    token = authorization.replace("Bearer ", "")
    if token not in ADMIN_TOKENS:
        raise HTTPException(status_code=401, detail="Invalid Token")

# ---------------- Get All Issues ----------------
@router.get("/issues")
def admin_get_all_issues(authorization: str | None = Header(None)):
    verify_admin_token(authorization)
    return {"status": "success", "issues": fetch_issues()}

# ---------------- Approve / Reject Issue ----------------
class ApproveIssueRequest(BaseModel):
    approved: bool | None = None
    department: str | None = None
    admin_comment: str | None = None

@router.post("/issues/{issue_id}/approve")
def admin_approve_issue(
    issue_id: int,
    data: ApproveIssueRequest,
    authorization: str | None = Header(None)
):
    verify_admin_token(authorization)

    issue = get_issue_by_id(issue_id)
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")

    new_status = issue["status"]

    if data.approved is True:
        new_status = "In Progress"
    elif data.approved is False:
        new_status = "Rejected"

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
        data.department if data.department else issue["assigned_department"],
        data.admin_comment if data.admin_comment else issue["admin_comment"],
        new_status,
        issue_id
    ))

    conn.commit()
    cursor.close()
    conn.close()

    return {"status": "success", "message": "Issue updated successfully"}

# ---------------- Cleanup Duplicates ----------------
@router.delete("/duplicates")
def delete_duplicates():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT id, title, description, category, user_id
        FROM issues ORDER BY id ASC
    """)
    rows = cursor.fetchall()

    seen = {}
    duplicates = []

    for row in rows:
        key = (row["title"], row["description"], row["category"], row["user_id"])
        if key in seen:
            duplicates.append(row["id"])
        else:
            seen[key] = row["id"]

    if duplicates:
        cursor.execute(
            f"DELETE FROM issues WHERE id IN ({','.join(['%s']*len(duplicates))})",
            tuple(duplicates)
        )
        conn.commit()

    cursor.close()
    conn.close()

    return {"status": "success", "deleted_count": len(duplicates)}
