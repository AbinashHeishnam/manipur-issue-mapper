from fastapi import APIRouter
from pydantic import BaseModel
import random, time
from backend.utils.db_utils import get_connection

router = APIRouter(prefix="/api/auth", tags=["Auth"])

# Temporary OTP store
otp_storage = {}

# Request payloads
class SendOtpRequest(BaseModel):
    mobile: str

class VerifyOtpRequest(BaseModel):
    mobile: str
    otp: int

# Send OTP
@router.post("/send-otp")
def send_otp(data: SendOtpRequest):
    otp = random.randint(100000, 999999)
    otp_storage[data.mobile] = {
        "otp": otp,
        "expiry": time.time() + 300  # 5 min
    }
    # For dev, we return OTP; in prod, you would send via SMS
    return {"status": "success", "otp": otp}

# Verify OTP
@router.post("/verify-otp")
def verify_otp(data: VerifyOtpRequest):
    record = otp_storage.get(data.mobile)

    if not record:
        return {"status": "error", "message": "OTP not sent"}

    if time.time() > record["expiry"]:
        return {"status": "error", "message": "OTP expired"}

    if data.otp != record["otp"]:
        return {"status": "error", "message": "Invalid OTP"}

    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT id FROM users WHERE mobile=%s", (data.mobile,))
    user = cur.fetchone()

    if not user:
        cur.execute("INSERT INTO users (mobile) VALUES (%s)", (data.mobile,))
        conn.commit()
        user_id = cur.lastrowid
    else:
        user_id = user["id"]

    cur.close()
    conn.close()
    otp_storage.pop(data.mobile)

    return {"status": "success", "user_id": user_id}
