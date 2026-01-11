import mysql.connector
from datetime import datetime

# ---------------- DATABASE CONFIG ----------------
db_config = {
    "host": "localhost",
    "user": "hackathon",
    "password": "hackpass",
    "database": "issue_mapper"
}

# ---------------- CONNECTION HELPER ----------------
def get_connection():
    return mysql.connector.connect(**db_config)

# ---------------- ISSUES ----------------
def fetch_issues(user_id=None):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    
    if user_id:
        cursor.execute("SELECT * FROM issues WHERE user_id = %s ORDER BY timestamp DESC", (user_id,))
    else:
        cursor.execute("SELECT * FROM issues ORDER BY timestamp DESC")
        
    rows = cursor.fetchall()
    conn.close()

    data = []
    for row in rows:
        data.append({
            "id": row["id"],
            "title": row["title"],
            "description": row["description"],
            "category": row["category"],
            "latitude": row["latitude"],
            "longitude": row["longitude"],
            "address": row.get("address") or "",
            "severity": row.get("severity") or 1,
            "status": row.get("status") or "Pending",
            "timestamp": str(row.get("timestamp")),
            "user_id": row.get("user_id") or None,
            "ai_category": row.get("ai_category") or "",
            "ai_severity": row.get("ai_severity") or 1,
            "assigned_department": row.get("assigned_department") or None,
            "approved_by_admin": row.get("approved_by_admin") or 0,
            "admin_comment": row.get("admin_comment") or ""
        })
    return data

def get_issue_by_id(issue_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM issues WHERE id=%s", (issue_id,))
    row = cursor.fetchone()
    conn.close()
    return row

def add_issue(title, category, description, latitude, longitude, user_id,
              severity=1, status="Pending", ai_category=None, ai_severity=None):
    conn = get_connection()
    cursor = conn.cursor()
    query = """
        INSERT INTO issues
        (title, description, category, latitude, longitude, severity, status, timestamp, user_id, ai_category, ai_severity)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    cursor.execute(query, (
        title,
        description,
        category,
        latitude,
        longitude,
        severity,
        status,
        datetime.now(),
        user_id,
        ai_category,
        ai_severity
    ))
    conn.commit()
    issue_id = cursor.lastrowid
    cursor.close()
    conn.close()
    return issue_id

def update_ai_fields(issue_id, ai_category, ai_severity):
    conn = get_connection()
    cursor = conn.cursor()
    query = "UPDATE issues SET ai_category=%s, ai_severity=%s WHERE id=%s"
    cursor.execute(query, (ai_category, ai_severity, issue_id))
    conn.commit()
    cursor.close()
    conn.close()

def fetch_nearby_issues(lat, lng, radius_km=0.5):
    """
    Find issues within a roughly square bounding box of radius_km.
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    
    # 1 degree lat ~ 111km
    # Simple formatting: +/- offset
    offset = (radius_km / 111.0) * 1.5 
    
    query = """
        SELECT id, title, timestamp, category FROM issues 
        WHERE latitude BETWEEN %s AND %s 
        AND longitude BETWEEN %s AND %s
        ORDER BY timestamp DESC
        LIMIT 5
    """
    cursor.execute(query, (lat - offset, lat + offset, lng - offset, lng + offset))
    rows = cursor.fetchall()
    conn.close()
    return rows
