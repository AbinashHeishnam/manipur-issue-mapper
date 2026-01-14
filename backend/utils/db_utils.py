# backend/utils/db_utils.py
import mysql.connector
from datetime import datetime
import bcrypt

db_config = {
    "host": "localhost",
    "user": "hackathon",
    "password": "hackpass",
    "database": "issue_mapper"
}

def get_connection():
    return mysql.connector.connect(**db_config)

# ---------- PASSWORD UTILS ----------
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())

# ---------- USER AUTH ----------
def set_user_password(user_id: int, password: str):
    hashed = hash_password(password)
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        REPLACE INTO user_auth (user_id, password_hash, created_at)
        VALUES (%s, %s, %s)
        """,
        (user_id, hashed, datetime.now())
    )
    conn.commit()
    cursor.close()
    conn.close()

def verify_user_password(mobile_or_email: str, password: str) -> dict | None:
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        """
        SELECT u.id, u.name, u.email, u.mobile, a.password_hash
        FROM users u
        JOIN user_auth a ON u.id = a.user_id
        WHERE u.mobile=%s OR u.email=%s
        LIMIT 1
        """,
        (mobile_or_email, mobile_or_email)
    )
    user = cursor.fetchone()
    cursor.close()
    conn.close()

    if user and verify_password(password, user["password_hash"]):
        return {
            "id": user["id"],
            "name": user.get("name"),
            "email": user.get("email"),
            "mobile": user.get("mobile"),
        }
    return None

def delete_user(user_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM user_auth WHERE user_id=%s", (user_id,))
    cursor.execute("DELETE FROM issues WHERE user_id=%s", (user_id,))
    cursor.execute("DELETE FROM users WHERE id=%s", (user_id,))
    conn.commit()
    cursor.close()
    conn.close()

def get_user_by_id(user_id: int) -> dict | None:
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, name, email, mobile FROM users WHERE id=%s", (user_id,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    return user

# ---------- ISSUES ----------
def fetch_issues(user_id=None):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    if user_id:
        cursor.execute("SELECT * FROM issues WHERE user_id=%s ORDER BY timestamp DESC", (user_id,))
    else:
        cursor.execute("SELECT * FROM issues ORDER BY timestamp DESC")

    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    data = []
    for row in rows:
        data.append({
            "id": row["id"],
            "title": row["title"],
            "description": row.get("description") or "",
            "category": row.get("category") or "",
            "latitude": row.get("latitude"),
            "longitude": row.get("longitude"),
            "address": row.get("address") or "",
            "severity": row.get("severity") or 1,
            "status": row.get("status") or "Pending",
            "timestamp": str(row.get("timestamp")),
            "user_id": row.get("user_id"),
            "ai_category": row.get("ai_category") or "",
            "ai_severity": row.get("ai_severity") or 1,
            "assigned_department": row.get("assigned_department") or None,
            "approved_by_admin": row.get("approved_by_admin") or 0,
            "admin_comment": row.get("admin_comment") or "",
            "ai_veracity": row.get("ai_veracity") or "unknown",
            "is_suspicious": int(row.get("is_suspicious") or 0),
        })

    return data

def get_issue_by_id(issue_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    query = """
        SELECT i.*, u.name as user_name, u.mobile as user_mobile, u.email as user_email 
        FROM issues i 
        LEFT JOIN users u ON i.user_id = u.id 
        WHERE i.id=%s
    """
    cursor.execute(query, (issue_id,))
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    return row

def add_issue(
    title, category, description, latitude, longitude, user_id,
    severity=1, status="Pending", ai_category=None, ai_severity=None,
    ai_veracity=None, is_suspicious=0
):
    conn = get_connection()
    cursor = conn.cursor()
    query = """
        INSERT INTO issues
        (title, description, category, latitude, longitude, severity, status, timestamp, user_id,
         ai_category, ai_severity, ai_veracity, is_suspicious)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    cursor.execute(query, (
        title, description, category, latitude, longitude,
        severity, status, datetime.now(), user_id,
        ai_category, ai_severity, ai_veracity, int(is_suspicious or 0)
    ))
    conn.commit()
    issue_id = cursor.lastrowid
    cursor.close()
    conn.close()
    return issue_id

def update_ai_fields(issue_id, ai_category, ai_severity):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE issues SET ai_category=%s, ai_severity=%s WHERE id=%s",
        (ai_category, ai_severity, issue_id)
    )
    conn.commit()
    cursor.close()
    conn.close()

def fetch_nearby_issues(lat, lng, radius_km=0.5):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    offset = (radius_km / 111.0) * 1.5
    cursor.execute(
        """
        SELECT id, title, timestamp, category FROM issues 
        WHERE latitude BETWEEN %s AND %s 
        AND longitude BETWEEN %s AND %s
        ORDER BY timestamp DESC
        LIMIT 5
        """,
        (lat - offset, lat + offset, lng - offset, lng + offset)
    )
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows

def update_issue_status(issue_id, status):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE issues SET status=%s WHERE id=%s", (status, issue_id))
    conn.commit()
    cursor.close()
    conn.close()

# ---------- DEPARTMENTS ----------
def get_department_by_username(username):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM departments WHERE username=%s", (username,))
    dept = cursor.fetchone()
    cursor.close()
    conn.close()
    return dept

def add_department(department_name, username, password_hash):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO departments (department_name, username, password_hash, created_at) VALUES (%s,%s,%s,%s)",
        (department_name, username, password_hash, datetime.now())
    )
    conn.commit()
    dept_id = cursor.lastrowid
    cursor.close()
    conn.close()
    return dept_id

def update_department_password(dept_id, new_password_hash):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE departments SET password_hash=%s WHERE id=%s", (new_password_hash, dept_id))
    conn.commit()
    cursor.close()
    conn.close()

# ---------- ADMINS ----------
def get_admin_by_username(username):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM admins WHERE username=%s", (username,))
    admin = cursor.fetchone()
    cursor.close()
    conn.close()
    return admin

def add_admin(username, password_hash, email=None):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO admins (username, password_hash, email, created_at) VALUES (%s,%s,%s,%s)",
        (username, password_hash, email, datetime.now())
    )
    conn.commit()
    admin_id = cursor.lastrowid
    cursor.close()
    conn.close()
    return admin_id
