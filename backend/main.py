from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from backend.routes import auth, issues, admin

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

# ---------- STATIC FILE SERVING ----------
# Main frontend (index, login, user dashboard)
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")

# Admin frontend
app.mount("/admin", StaticFiles(directory="frontend/admin", html=True), name="admin")

@app.get("/health")
def health():
    return {"status": "ok"}
from fastapi import APIRouter
from pydantic import BaseModel
import random, time
from backend.utils.db_utils import get_connection

router = APIRouter(prefix="/api/auth", tags=["Auth"])

# Temporary in-memory OTP store
otp_storage = {}

# ----- Request Models -----
class SendOtpRequest(BaseModel):
    mobile: str

class VerifyOtpRequest(BaseModel):
    mobile: str
    otp: int

# ----- Send OTP -----
@router.post("/send-otp")
def send_otp(data: SendOtpRequest):
    # Generate 6-digit OTP
    otp = random.randint(100000, 999999)

    # Store OTP in memory with 5 min expiry
    otp_storage[data.mobile] = {
        "otp": otp,
        "expiry": time.time() + 300
    }

    # Return OTP for DEV/testing (remove alert in production)
    return {"status": "success", "otp": otp, "message": "OTP generated. Use this OTP to verify."}

# ----- Verify OTP -----
@router.post("/verify-otp")
def verify_otp(data: VerifyOtpRequest):
    record = otp_storage.get(data.mobile)

    if not record:
        return {"status": "error", "message": "OTP not sent for this number"}

    if time.time() > record["expiry"]:
        otp_storage.pop(data.mobile, None)
        return {"status": "error", "message": "OTP expired"}

    if data.otp != record["otp"]:
        return {"status": "error", "message": "Invalid OTP"}

    # OTP is valid; check user in DB
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT id FROM users WHERE mobile=%s", (data.mobile,))
    user = cur.fetchone()

    if not user:
        # Create user if not exists
        cur.execute("INSERT INTO users (mobile) VALUES (%s)", (data.mobile,))
        conn.commit()
        user_id = cur.lastrowid
    else:
        user_id = user["id"]

    cur.close()
    conn.close()

    # Remove OTP after successful verification
    otp_storage.pop(data.mobile, None)

    return {"status": "success", "user_id": user_id, "message": "OTP verified successfully"}
