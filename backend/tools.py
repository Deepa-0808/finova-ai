from database import get_db
from datetime import datetime


def add_expense(
    amount,
    category,
    description=""
):

    conn = get_db()

    conn.execute("""
        INSERT INTO expenses
        (user_id, amount, category, description, date)
        VALUES (?, ?, ?, ?, ?)
    """, (
        1,
        amount,
        category,
        description,
        datetime.now().isoformat()
    ))

    conn.commit()

    conn.close()

    return {
        "success": True,
        "message": "Expense recorded"
    }