from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel
from backend.utils.db_utils import (
    fetch_issues,
    get_issue_by_id,
    update_issue_status,
    get_connection
)
import bcrypt
import uuid

router = APIRouter(prefix="/api/department", tags=["Department"])

# In-memory token store
DEPT_TOKENS = {}

# ---------------- Models ----------------
class DeptLoginRequest(BaseModel):
    username: str
    password: str

# ---------------- Login ----------------
@router.post("/login")
def dept_login(data: DeptLoginRequest):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        "SELECT * FROM departments WHERE username=%s",
        (data.username,)
    )
    dept = cursor.fetchone()

    cursor.close()
    conn.close()

    if not dept:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not bcrypt.checkpw(
        data.password.encode(),
        dept["password_hash"].encode()
    ):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = f"dept-token-{uuid.uuid4()}"
    DEPT_TOKENS[token] = dept

    return {
        "status": "success",
        "token": token,
        "department_name": dept["department_name"],
        "department_id": dept["username"]
    }

# ---------------- Auth Guard ----------------
def verify_dept_token(authorization: str | None):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Unauthorized")

    token = authorization.replace("Bearer ", "")
    if token not in DEPT_TOKENS:
        raise HTTPException(status_code=401, detail="Invalid Token")

    return DEPT_TOKENS[token]

# ---------------- Get Issues ----------------
@router.get("/issues")
def dept_get_issues(authorization: str | None = Header(None)):
    dept = verify_dept_token(authorization)

    all_issues = fetch_issues()

    filtered = []
    for i in all_issues:
        assigned = i.get("assigned_department")
        if not assigned:
            continue
            
        # Flexible Matching: "Sanitation" == "Sanitation Department"
        # Check if one string is contained in the other
        is_match = (
            assigned == dept["department_name"] or 
            assigned in dept["department_name"] or 
            dept["department_name"] in assigned
        )
        
        if is_match and i["approved_by_admin"] == 1:
            filtered.append(i)

    return {"status": "success", "issues": filtered}

# ---------------- Update Status ----------------
class UpdateStatusRequest(BaseModel):
    status: str
    note: str | None = None

@router.post("/issues/{issue_id}/update")
def dept_update_issue(
    issue_id: int,
    data: UpdateStatusRequest,
    authorization: str | None = Header(None)
):
    dept = verify_dept_token(authorization)

    issue = get_issue_by_id(issue_id)
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")

    if issue["assigned_department"] != dept["department_name"]:
        raise HTTPException(status_code=403, detail="Not your department issue")

    update_issue_status(issue_id, data.status)

    return {"status": "success", "message": "Status updated"}

# ---------------- Debug ----------------
@router.get("/debug")
def debug_issues():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM departments")
    depts = cursor.fetchall()
    
    issues = fetch_issues()
    conn.close()
    
    return {
        "status": "success",
        "departments": depts,
        "issues": [
            {
                "id": i["id"],
                "assigned_department": i["assigned_department"],
                "approved_by_admin": i["approved_by_admin"],
                "status": i["status"]
            } for i in issues
        ]
    }
