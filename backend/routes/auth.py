from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
import random, time
from backend.utils.db_utils import (
    get_connection, set_user_password, verify_user_password, delete_user, get_user_by_id
)

router = APIRouter(prefix="/api/auth", tags=["Auth"])

# Temporary OTP storage
otp_storage = {}

# ---------------- REQUEST MODELS ----------------
class SendOtpRequest(BaseModel):
    mobile: str
    name: str | None = None
    email: EmailStr | None = None

class VerifyOtpRequest(BaseModel):
    mobile: str
    otp: int
    name: str | None = None
    email: EmailStr | None = None

class SetPasswordRequest(BaseModel):
    user_id: int
    password: str

class LoginRequest(BaseModel):
    mobile_or_email: str
    password: str

class DeleteUserRequest(BaseModel):
    user_id: int

# ---------------- SEND OTP ----------------
@router.post("/send-otp")
def send_otp(data: SendOtpRequest):
    otp = random.randint(100000, 999999)
    otp_storage[data.mobile] = {"otp": otp, "expiry": time.time() + 300}

    # Create user if first-time
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT id FROM users WHERE mobile=%s", (data.mobile,))
    user = cur.fetchone()
    if not user:
        cur.execute(
            "INSERT INTO users (mobile, name, email) VALUES (%s, %s, %s)",
            (data.mobile, data.name, data.email)
        )
        conn.commit()
        user_id = cur.lastrowid
    else:
        user_id = user["id"]
    cur.close()
    conn.close()

    return {"status": "success", "otp": otp, "user_id": user_id}

# ---------------- VERIFY OTP ----------------
@router.post("/verify-otp")
def verify_otp(data: VerifyOtpRequest):
    record = otp_storage.get(data.mobile)
    if not record:
        raise HTTPException(status_code=400, detail="OTP not sent")
    if time.time() > record["expiry"]:
        raise HTTPException(status_code=400, detail="OTP expired")
    if data.otp != record["otp"]:
        raise HTTPException(status_code=400, detail="Invalid OTP")

    # Fetch user
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT id, name, email FROM users WHERE mobile=%s", (data.mobile,))
    user = cur.fetchone()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Update missing name/email
    updates, values = [], []
    if data.name and not user.get("name"):
        updates.append("name=%s")
        values.append(data.name)
    if data.email and not user.get("email"):
        updates.append("email=%s")
        values.append(data.email)
    if updates:
        values.append(user["id"])
        cur.execute(f"UPDATE users SET {', '.join(updates)} WHERE id=%s", tuple(values))
        conn.commit()

    cur.close()
    conn.close()
    otp_storage.pop(data.mobile)
    return {"status": "success", "user_id": user["id"], "message": "OTP verified, now set your password"}

# ---------------- SET PASSWORD ----------------
@router.post("/set-password")
def set_password_endpoint(data: SetPasswordRequest):
    user = get_user_by_id(data.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    # Store password in user_auth table
    set_user_password(user_id=data.user_id, password=data.password)
    return {"status": "success", "message": "Password set successfully, you can now login"}

# ---------------- LOGIN ----------------
@router.post("/login")
def login(data: LoginRequest):
    user = verify_user_password(data.mobile_or_email, data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"status": "success", "user_id": user["id"], "name": user.get("name"), "email": user.get("email")}
    
# ---------------- PROFILE ----------------
@router.get("/profile/{user_id}")
def get_user_profile(user_id: int):
    user = get_user_by_id(user_id)
    if user:
        return {"status": "success", "data": user}
    raise HTTPException(status_code=404, detail="User not found")

# ---------------- DELETE ----------------
@router.delete("/delete")
def delete_account(data: DeleteUserRequest):
    user = get_user_by_id(data.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    delete_user(data.user_id)
    return {"status": "success", "message": "User account deleted successfully"}
