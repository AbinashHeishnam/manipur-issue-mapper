from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel
from backend.utils.db_utils import fetch_issues

router = APIRouter(prefix="/api/department", tags=["Department"])

# Hardcoded departments and credentials (simplification for prototype)
DEPARTMENTS = {
    "water": {"password": "water", "name": "Water Department"},
    "electricity": {"password": "electricity", "name": "Electricity Department"},
    "road": {"password": "road", "name": "Roads & Infrastructure"},
    "sanitation": {"password": "sanitation", "name": "Sanitation"},
    "health": {"password": "health", "name": "Health Department"},
    "police": {"password": "police", "name": "Police"},
    "municipality": {"password": "municipality", "name": "Municipality"}
}

class DeptLoginRequest(BaseModel):
    username: str
    password: str

@router.post("/login")
def dept_login(data: DeptLoginRequest):
    username = data.username.lower().strip()
    if username in DEPARTMENTS and DEPARTMENTS[username]["password"] == data.password:
        return {
            "status": "success", 
            "token": f"dept-token-{username}", 
            "department_name": DEPARTMENTS[username]["name"],
            "department_id": username
        }
    raise HTTPException(status_code=401, detail="Invalid department credentials")

@router.get("/issues")
def dept_get_issues(authorization: str | None = Header(None)):
    if not authorization or not authorization.startswith("Bearer dept-token-"):
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    # Extract department id from fake token
    dept_id = authorization.split("-token-")[1]
    
    if dept_id not in DEPARTMENTS:
        raise HTTPException(status_code=401, detail="Invalid Token")
        
    target_dept_name = DEPARTMENTS[dept_id]["name"]
    
    all_issues = fetch_issues()
    
    # Filter issues: 
    # 1. Assigned to this department
    # 2. Approved by admin (usually departments only see valid jobs)
    filtered = [
        i for i in all_issues 
        if i["assigned_department"] == target_dept_name and i["approved_by_admin"] == 1
    ]
    
    return {"status": "success", "issues": filtered}
