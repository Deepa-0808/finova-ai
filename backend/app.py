from flask import Flask, request, jsonify, session
from flask_cors import CORS

from database import init_db, get_db
from datetime import datetime
from agent import ask_finova
from finance import get_financial_context
from market_data import get_stock_price
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)

app.secret_key = "finova-ai-secret-key-change-this-later"

CORS(app, supports_credentials=True)

# Initialize database
init_db()


# =====================================================
# HELPER
# =====================================================

def get_current_user_id():
    return session.get("user_id")


def require_login():

    user_id = get_current_user_id()

    if not user_id:
        return None, jsonify({
            "error": "Please login first"
        }), 401

    return user_id, None, None


# =====================================================
# AUTHENTICATION
# =====================================================

@app.route("/api/register", methods=["POST"])
def register():

    data = request.json or {}

    name = data.get("name", "").strip()
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    if not name or not email or not password:
        return jsonify({
            "error": "Name, email and password are required"
        }), 400

    if len(password) < 6:
        return jsonify({
            "error": "Password must be at least 6 characters"
        }), 400

    conn = get_db()

    existing_user = conn.execute(
        "SELECT id FROM users WHERE email = ?",
        (email,)
    ).fetchone()

    if existing_user:
        conn.close()

        return jsonify({
            "error": "An account with this email already exists"
        }), 409

    password_hash = generate_password_hash(password)

    cursor = conn.execute("""
        INSERT INTO users
        (
            name,
            email,
            password_hash,
            income,
            savings,
            risk_level,
            emergency_fund
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        name,
        email,
        password_hash,
        0,
        0,
        "moderate",
        0
    ))

    user_id = cursor.lastrowid

    conn.commit()
    conn.close()

    session["user_id"] = user_id

    return jsonify({
        "success": True,
        "message": "Account created successfully",
        "user": {
            "id": user_id,
            "name": name,
            "email": email
        }
    })


@app.route("/api/login", methods=["POST"])
def login():

    data = request.json or {}

    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    if not email or not password:
        return jsonify({
            "error": "Email and password are required"
        }), 400

    conn = get_db()

    user = conn.execute("""
        SELECT *
        FROM users
        WHERE email = ?
    """, (email,)).fetchone()

    conn.close()

    if user is None:
        return jsonify({
            "error": "Invalid email or password"
        }), 401

    if not user["password_hash"]:
        return jsonify({
            "error": "This account does not have a password yet"
        }), 401

    if not check_password_hash(
        user["password_hash"],
        password
    ):
        return jsonify({
            "error": "Invalid email or password"
        }), 401

    session["user_id"] = user["id"]

    return jsonify({
        "success": True,
        "message": "Login successful",
        "user": {
            "id": user["id"],
            "name": user["name"],
            "email": user["email"]
        }
    })


@app.route("/api/logout", methods=["POST"])
def logout():

    session.clear()

    return jsonify({
        "success": True,
        "message": "Logged out successfully"
    })


@app.route("/api/me", methods=["GET"])
def current_user():

    user_id = get_current_user_id()

    if not user_id:
        return jsonify({
            "logged_in": False
        })

    conn = get_db()

    user = conn.execute("""
        SELECT id, name, email
        FROM users
        WHERE id = ?
    """, (user_id,)).fetchone()

    conn.close()

    if user is None:

        session.clear()

        return jsonify({
            "logged_in": False
        })

    return jsonify({
        "logged_in": True,
        "user": dict(user)
    })


# =====================================================
# HOME
# =====================================================

@app.route("/")
def home():

    return jsonify({
        "message": "Intelligent Financial Decision Agent API",
        "status": "running"
    })


# =====================================================
# EXPENSES
# =====================================================

@app.route("/api/expenses", methods=["POST"])
def add_expense():

    user_id, error_response, status = require_login()

    if not user_id:
        return error_response, status

    data = request.json or {}

    amount = data.get("amount")
    category = data.get("category")
    description = data.get("description", "")

    if not amount or not category:
        return jsonify({
            "error": "Amount and category are required"
        }), 400

    conn = get_db()

    conn.execute("""
        INSERT INTO expenses
        (
            user_id,
            amount,
            category,
            description,
            date
        )
        VALUES (?, ?, ?, ?, ?)
    """, (
        user_id,
        amount,
        category,
        description,
        datetime.now().isoformat()
    ))

    conn.commit()
    conn.close()

    return jsonify({
        "message": "Expense added successfully"
    })


@app.route("/api/expenses", methods=["GET"])
def get_expenses():

    user_id, error_response, status = require_login()

    if not user_id:
        return error_response, status

    conn = get_db()

    expenses = conn.execute("""
        SELECT *
        FROM expenses
        WHERE user_id = ?
        ORDER BY date DESC
    """, (user_id,)).fetchall()

    conn.close()

    return jsonify([
        dict(expense)
        for expense in expenses
    ])


# =====================================================
# DASHBOARD
# =====================================================

@app.route("/api/dashboard", methods=["GET"])
def dashboard():

    user_id, error_response, status = require_login()

    if not user_id:
        return error_response, status

    conn = get_db()

    total_expenses = conn.execute("""
        SELECT COALESCE(SUM(amount), 0)
        FROM expenses
        WHERE user_id = ?
    """, (user_id,)).fetchone()[0]

    user = conn.execute("""
        SELECT *
        FROM users
        WHERE id = ?
    """, (user_id,)).fetchone()

    conn.close()

    return jsonify({
        "total_expenses": total_expenses,
        "income": user["income"] if user else 0,
        "savings": user["savings"] if user else 0,
        "emergency_fund": (
            user["emergency_fund"]
            if user else 0
        )
    })


# =====================================================
# ALERTS
# =====================================================

@app.route("/api/alerts", methods=["GET"])
def get_alerts():

    user_id, error_response, status = require_login()

    if not user_id:
        return error_response, status

    conn = get_db()

    alerts = conn.execute("""
        SELECT *
        FROM alerts
        WHERE user_id = ?
        ORDER BY created_at DESC
    """, (user_id,)).fetchall()

    conn.close()

    return jsonify([
        dict(alert)
        for alert in alerts
    ])


@app.route("/api/alerts", methods=["POST"])
def create_alert_api():

    user_id, error_response, status = require_login()

    if not user_id:
        return error_response, status

    data = request.json or {}

    title = data.get("title")
    message = data.get("message")
    alert_type = data.get("type", "general")

    if not title or not message:
        return jsonify({
            "error": "Title and message are required"
        }), 400

    conn = get_db()

    conn.execute("""
        INSERT INTO alerts
        (
            user_id,
            title,
            message,
            type,
            created_at,
            is_read
        )
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        user_id,
        title,
        message,
        alert_type,
        datetime.now().isoformat(),
        0
    ))

    conn.commit()
    conn.close()

    return jsonify({
        "success": True,
        "message": "Alert created successfully"
    })


# =====================================================
# INVESTMENTS
# =====================================================

@app.route("/api/investments", methods=["POST"])
def create_investment():

    user_id, error_response, status = require_login()

    if not user_id:
        return error_response, status

    data = request.json or {}

    asset = data.get("asset")
    asset_type = data.get("asset_type")
    amount = data.get("amount")

    purchase_price = data.get(
        "purchase_price",
        0
    )

    current_price = data.get(
        "current_price",
        0
    )

    symbol = data.get(
        "symbol",
        ""
    )

    quantity = data.get(
        "quantity",
        0
    )

    exchange = data.get(
        "exchange",
        ""
    )

    data_source = data.get(
        "data_source",
        "Manual"
    )

    last_updated = data.get(
        "last_updated",
        ""
    )

    if not asset or not asset_type or not amount:

        return jsonify({
            "error": "Asset, type and amount are required"
        }), 400

    try:

        conn = get_db()

        conn.execute("""
            INSERT INTO investments
            (
                user_id,
                asset,
                asset_type,
                amount,
                purchase_price,
                current_price,
                symbol,
                quantity,
                exchange,
                data_source,
                last_updated
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            user_id,
            asset,
            asset_type,
            float(amount),
            float(purchase_price),
            float(current_price),
            symbol,
            float(quantity),
            exchange,
            data_source,
            last_updated
        ))

        conn.commit()
        conn.close()

        return jsonify({
            "success": True,
            "message": "Investment added successfully"
        })

    except Exception as e:

        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route("/api/investments", methods=["GET"])
def get_investments():

    user_id, error_response, status = require_login()

    if not user_id:
        return error_response, status

    conn = get_db()

    investments = conn.execute("""
        SELECT *
        FROM investments
        WHERE user_id = ?
        ORDER BY id DESC
    """, (user_id,)).fetchall()

    conn.close()

    return jsonify([
        dict(investment)
        for investment in investments
    ])


# =====================================================
# GOALS
# =====================================================

@app.route("/api/goals", methods=["POST"])
def create_goal():

    user_id, error_response, status = require_login()

    if not user_id:
        return error_response, status

    data = request.json or {}

    name = data.get("name")
    target = data.get("target")
    deadline = data.get("deadline")

    if not name or not target:
        return jsonify({
            "error": "Goal name and target are required"
        }), 400

    conn = get_db()

    conn.execute("""
        INSERT INTO goals
        (
            user_id,
            name,
            target,
            saved,
            deadline
        )
        VALUES (?, ?, ?, ?, ?)
    """, (
        user_id,
        name,
        float(target),
        0,
        deadline
    ))

    conn.commit()
    conn.close()

    return jsonify({
        "success": True,
        "message": "Goal created successfully"
    })


@app.route("/api/goals", methods=["GET"])
def get_goals():

    user_id, error_response, status = require_login()

    if not user_id:
        return error_response, status

    conn = get_db()

    goals = conn.execute("""
        SELECT *
        FROM goals
        WHERE user_id = ?
        ORDER BY id DESC
    """, (user_id,)).fetchall()

    conn.close()

    return jsonify([
        dict(goal)
        for goal in goals
    ])


# =====================================================
# AI ADVISOR
# =====================================================

@app.route("/api/advisor", methods=["POST"])
def advisor():

    user_id, error_response, status = require_login()

    if not user_id:
        return error_response, status

    data = request.json or {}

    question = data.get("question")

    if not question:
        return jsonify({
            "error": "Question is required"
        }), 400

    try:

        financial_context = get_financial_context()

        question_upper = question.upper()

        investment_keywords = [
            "INVEST",
            "INVESTMENT",
            "STOCK",
            "SHARE",
            "BUY STOCK",
            "BUY SHARES",
            "STOCK PRICE",
            "STOCK MARKET"
        ]

        is_market_question = any(
            keyword in question_upper
            for keyword in investment_keywords
        )

        stock_symbols = {

            "TCS": "TCS.NS",

            "TATA CONSULTANCY": "TCS.NS",

            "INFOSYS": "INFY.NS",

            "INFY": "INFY.NS",

            "RELIANCE": "RELIANCE.NS",

            "ITC": "ITC.NS",

            "SBI": "SBIN.NS",

            "STATE BANK OF INDIA": "SBIN.NS",

            "ICICI": "ICICIBANK.NS",

            "ICICI BANK": "ICICIBANK.NS",

            "HDFC BANK": "HDFCBANK.NS",

            "BHARTI AIRTEL": "BHARTIARTL.NS",

            "AIRTEL": "BHARTIARTL.NS"
        }

        market_context = {
            "available": False,
            "message": "No current market data was retrieved."
        }

        if is_market_question:

            detected_symbol = None

            for company_name, symbol in stock_symbols.items():

                if company_name in question_upper:

                    detected_symbol = symbol

                    break

            if detected_symbol:

                market_context = get_stock_price(
                    detected_symbol
                )

            else:

                market_context = {
                    "available": False,
                    "message": (
                        "This appears to be an investment "
                        "question, but Finova could not "
                        "identify the stock symbol."
                    )
                }

        answer = ask_finova(
            question,
            financial_context,
            market_context
        )

        return jsonify({

            "success": True,

            "question": question,

            "answer": answer,

            "market_data": market_context

        })

    except Exception as e:

        print(
            "Advisor error:",
            e
        )

        return jsonify({
            "error": str(e)
        }), 500


# =====================================================
# PROFILE API
# =====================================================

@app.route("/api/profile", methods=["GET"])
def get_profile():

    user_id, error_response, status = require_login()

    if not user_id:
        return error_response, status

    conn = get_db()

    profile = conn.execute("""
        SELECT
            id,
            name,
            email,
            income,
            savings,
            risk_level,
            emergency_fund
        FROM users
        WHERE id = ?
    """, (user_id,)).fetchone()

    conn.close()

    if profile is None:

        return jsonify({
            "error": "User profile not found"
        }), 404

    return jsonify(
        dict(profile)
    )


@app.route("/api/profile", methods=["PUT"])
def update_profile():

    user_id, error_response, status = require_login()

    if not user_id:
        return error_response, status

    data = request.json or {}

    income = float(
        data.get("income", 0)
    )

    savings = float(
        data.get("savings", 0)
    )

    emergency_fund = float(
        data.get("emergency_fund", 0)
    )

    risk_level = data.get(
        "risk_level",
        "moderate"
    )

    conn = get_db()

    conn.execute("""
        UPDATE users
        SET
            income = ?,
            savings = ?,
            risk_level = ?,
            emergency_fund = ?
        WHERE id = ?
    """, (
        income,
        savings,
        risk_level,
        emergency_fund,
        user_id
    ))

    conn.commit()
    conn.close()

    return jsonify({
        "success": True,
        "message": "Financial profile updated successfully"
    })


# =====================================================
# RUN SERVER
# =====================================================

if __name__ == "__main__":

    app.run(debug=True)