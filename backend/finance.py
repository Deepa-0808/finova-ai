from database import get_db


def get_financial_context():

    conn = get_db()

    user = conn.execute("""
        SELECT *
        FROM users
        WHERE id = 1
    """).fetchone()

    expenses = conn.execute("""
        SELECT
            category,
            SUM(amount) AS total
        FROM expenses
        WHERE user_id = 1
        GROUP BY category
    """).fetchall()

    goals = conn.execute("""
        SELECT *
        FROM goals
        WHERE user_id = 1
    """).fetchall()

    investments = conn.execute("""
        SELECT *
        FROM investments
        WHERE user_id = 1
    """).fetchall()

    conn.close()

    return {
        "income": user["income"] if user else 0,
        "savings": user["savings"] if user else 0,
        "risk_level": user["risk_level"] if user else "moderate",
        "emergency_fund": user["emergency_fund"] if user else 0,

        "expenses": [
            dict(expense)
            for expense in expenses
        ],

        "goals": [
            dict(goal)
            for goal in goals
        ],

        "investments": [
            dict(investment)
            for investment in investments
        ]
    }