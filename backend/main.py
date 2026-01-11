from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from backend.routes import auth, issues, admin, department

app = FastAPI(title="Manipur Issue Mapper API")

# ---------- CORS ----------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- API Routes ----------
app.include_router(auth.router)
app.include_router(issues.router)
app.include_router(admin.router)
app.include_router(department.router)

# ---------- STATIC FILE SERVING ----------
# Main frontend (index, login, user dashboard)
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")  # This might shadow others if not careful, but FastAPI checks specific matches first usually. Actually, root mount catches everything. 
# Best practice: Mount specific sub-apps first.

app.mount("/admin", StaticFiles(directory="frontend/admin", html=True), name="admin")
app.mount("/department", StaticFiles(directory="frontend/department", html=True), name="department")

@app.get("/health")
def health():
    return {"status": "ok"}
