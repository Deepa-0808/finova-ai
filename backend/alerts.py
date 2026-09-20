from database import get_db
from datetime import datetime


def create_alert(
    title,
    message,
    alert_type="general"
):

    conn = get_db()

    conn.execute("""
        INSERT INTO alerts
        (
            user_id,
            title,
            message,
            type,
            created_at
        )

        VALUES (?, ?, ?, ?, ?)
    """, (
        1,
        title,
        message,
        alert_type,
        datetime.now().isoformat()
    ))

    conn.commit()

    conn.close()