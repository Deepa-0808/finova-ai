import sqlite3
import os


# =====================================================
# DATABASE PATH
# =====================================================

DATABASE = os.path.join(
    os.path.dirname(__file__),
    "..",
    "database",
    "finance.db"
)

DATABASE = os.path.abspath(DATABASE)


# =====================================================
# DATABASE CONNECTION
# =====================================================

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


# =====================================================
# INITIALIZE DATABASE
# =====================================================

def init_db():

    # Create database folder if it does not exist
    os.makedirs(
        os.path.dirname(DATABASE),
        exist_ok=True
    )

    conn = get_db()
    cursor = conn.cursor()


    # =================================================
    # USERS TABLE
    # =================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT,
            password_hash TEXT,
            income REAL DEFAULT 0,
            savings REAL DEFAULT 0,
            risk_level TEXT DEFAULT 'moderate',
            emergency_fund REAL DEFAULT 0
        )
    """)
    # Add missing columns to older users table
    user_columns = [
        row["name"]
        for row in cursor.execute(
            "PRAGMA table_info(users)"
        ).fetchall()
    ]

    if "email" not in user_columns:
        cursor.execute(
            "ALTER TABLE users ADD COLUMN email TEXT"
        )

    if "password_hash" not in user_columns:
        cursor.execute(
            "ALTER TABLE users ADD COLUMN password_hash TEXT"
        )

    # =================================================
    # EXPENSES TABLE
    # =================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            amount REAL,
            category TEXT,
            description TEXT,
            date TEXT
        )
    """)


    # =================================================
    # BUDGETS TABLE
    # =================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS budgets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            category TEXT,
            amount REAL
        )
    """)


    # =================================================
    # GOALS TABLE
    # =================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS goals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            name TEXT,
            target REAL,
            saved REAL DEFAULT 0,
            deadline TEXT
        )
    """)


    # =================================================
    # INVESTMENTS TABLE
    # =================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS investments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            asset TEXT,
            asset_type TEXT,
            amount REAL,
            purchase_price REAL,
            current_price REAL
        )
    """)


    # =================================================
    # ADDITIONAL INVESTMENT FIELDS
    # =================================================

    investment_columns = [
        ("symbol", "TEXT"),
        ("quantity", "REAL DEFAULT 0"),
        ("exchange", "TEXT"),
        ("data_source", "TEXT"),
        ("last_updated", "TEXT")
    ]

    # Get existing investment columns
    existing_columns = [
        row["name"]
        for row in cursor.execute(
            "PRAGMA table_info(investments)"
        ).fetchall()
    ]

    # Add missing columns
    for column_name, column_type in investment_columns:

        if column_name not in existing_columns:

            cursor.execute(
                f"ALTER TABLE investments ADD COLUMN "
                f"{column_name} {column_type}"
            )


    # =================================================
    # ALERTS TABLE
    # =================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            title TEXT,
            message TEXT,
            type TEXT,
            created_at TEXT,
            is_read INTEGER DEFAULT 0
        )
    """)


    # =================================================
    # AI DECISION HISTORY
    # =================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS decisions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            question TEXT,
            response TEXT,
            confidence REAL,
            created_at TEXT
        )
    """)


    # =================================================
    # SAVE DATABASE CHANGES
    # =================================================

    conn.commit()
    conn.close()