
import mysql.connector

db_config = {
    "host": "localhost",
    "user": "hackathon",
    "password": "hackpass",
    "database": "issue_mapper"
}

conn = mysql.connector.connect(**db_config)
cursor = conn.cursor(dictionary=True)

print("--- DEPARTMENTS ---")
cursor.execute("SELECT id, department_name, username FROM departments")
for row in cursor.fetchall():
    print(row)

print("\n--- ISSUES ASSIGNED ---")
cursor.execute("SELECT id, title, category, assigned_department, status FROM issues WHERE assigned_department IS NOT NULL LIMIT 10")
for row in cursor.fetchall():
    print(row)

conn.close()
