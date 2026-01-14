# ai/export_admin_labels.py
import os
import pandas as pd
from backend.utils.db_utils import get_connection

OUT_PATH = "ai/data/veracity_training.csv"

def export_labels():
    """
    Creates/updates a dataset:
    label = 1 => rejected (false)
    label = 0 => approved_by_admin=1 (legit)
    """
    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    cur.execute("""
        SELECT
            id, title, description,
            approved_by_admin,
            status
        FROM issues
        WHERE title IS NOT NULL
    """)
    rows = cur.fetchall()

    cur.close()
    conn.close()

    data = []
    for r in rows:
        title = (r.get("title") or "").strip()
        desc  = (r.get("description") or "").strip()
        status = (r.get("status") or "").lower()
        approved = int(r.get("approved_by_admin") or 0)

        if not title and not desc:
            continue

        # Only take items where admin made a decision
        # Approved => legit (0)
        if approved == 1:
            label = 0
        # Rejected => false (1)
        elif status == "rejected":
            label = 1
        else:
            continue

        data.append({"title": title, "description": desc, "label": label})

    os.makedirs("ai/data", exist_ok=True)
    df = pd.DataFrame(data).drop_duplicates()

    df.to_csv(OUT_PATH, index=False)
    print(f"✅ Exported {len(df)} labeled samples to {OUT_PATH}")

if __name__ == "__main__":
    export_labels()
