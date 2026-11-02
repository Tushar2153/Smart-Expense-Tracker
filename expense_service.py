
from pathlib import Path
import sqlite3
from datetime import date, datetime
import joblib

# Project paths
BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "models" / "expense_classifier.joblib"
DB_PATH = BASE_DIR / "expenses.db"

CONFIDENCE_THRESHOLD = 0.40

# Load the trained model
model = joblib.load(MODEL_PATH)



def initialize_database():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                description TEXT NOT NULL,
                amount REAL NOT NULL CHECK(amount >= 0),
                transaction_date TEXT NOT NULL,
                category TEXT NOT NULL,
                confidence REAL NOT NULL,
                review_required INTEGER NOT NULL,
                created_at TEXT NOT NULL
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS budgets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                month TEXT NOT NULL,
                category TEXT NOT NULL,
                amount REAL NOT NULL CHECK(amount > 0),
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                UNIQUE(month, category)
            )
        """)



def predict_category(description):
    probabilities = model.predict_proba([description])[0]
    best_index = probabilities.argmax()

    category = str(model.classes_[best_index])
    confidence = float(probabilities[best_index])

    review_required = confidence < CONFIDENCE_THRESHOLD

    if review_required:
        category = "Needs Review"

    return category, confidence, review_required


def add_transaction(description, amount, transaction_date=None):
    description = description.strip()

    if not description:
        raise ValueError("Description cannot be empty.")

    if amount < 0:
        raise ValueError("Amount cannot be negative.")

    if transaction_date is None:
        transaction_date = date.today().isoformat()

    # Validate the date format
    datetime.strptime(transaction_date, "%Y-%m-%d")

    category, confidence, review_required = predict_category(
        description
    )

    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.execute("""
            INSERT INTO transactions (
                description, amount, transaction_date,
                category, confidence, review_required, created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            description,
            amount,
            transaction_date,
            category,
            confidence,
            int(review_required),
            datetime.now().isoformat(timespec="seconds")
        ))

        transaction_id = cursor.lastrowid

    return {
        "id": transaction_id,
        "description": description,
        "amount": amount,
        "date": transaction_date,
        "category": category,
        "confidence": round(confidence * 100, 1),
        "review_required": review_required
    }


def get_transactions():
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute("""
            SELECT *
            FROM transactions
            ORDER BY transaction_date DESC, id DESC
        """).fetchall()

    return [dict(row) for row in rows]


def _validate_budget_month(month):
    try:
        datetime.strptime(month, "%Y-%m")
    except (ValueError, TypeError):
        raise ValueError("Month must use YYYY-MM format, e.g. 2026-10.")


def save_budget(month, category, amount):
    _validate_budget_month(month)

    category = category.strip()
    if not category:
        raise ValueError("Category cannot be empty.")

    if amount <= 0:
        raise ValueError("Budget amount must be greater than zero.")

    now = datetime.now().isoformat(timespec="seconds")

    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            INSERT INTO budgets (
                month, category, amount, created_at, updated_at
            )
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(month, category)
            DO UPDATE SET
                amount = excluded.amount,
                updated_at = excluded.updated_at
        """, (month, category, amount, now, now))

    return {
        "month": month,
        "category": category,
        "amount": amount,
    }


def get_budget_status(month):
    _validate_budget_month(month)

    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row

        budgets = conn.execute("""
            SELECT month, category, amount
            FROM budgets
            WHERE month = ?
            ORDER BY
                CASE WHEN category = 'Overall' THEN 0 ELSE 1 END,
                category
        """, (month,)).fetchall()

        transactions = conn.execute("""
            SELECT category, COALESCE(SUM(amount), 0) AS spent
            FROM transactions
            WHERE substr(transaction_date, 1, 7) = ?
            GROUP BY category
        """, (month,)).fetchall()

    category_spending = {
        row["category"]: float(row["spent"])
        for row in transactions
    }
    total_spending = sum(category_spending.values())

    results = []

    for budget in budgets:
        category = budget["category"]
        limit = float(budget["amount"])

        spent = (
            total_spending
            if category == "Overall"
            else category_spending.get(category, 0.0)
        )

        remaining = limit - spent

        results.append({
            "month": month,
            "category": category,
            "budget": limit,
            "spent": round(spent, 2),
            "remaining": round(remaining, 2),
            "percent_used": round((spent / limit) * 100, 1),
            "exceeded": spent > limit,
        })

    return results


def delete_budget(month, category):
    _validate_budget_month(month)

    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.execute("""
            DELETE FROM budgets
            WHERE month = ? AND category = ?
        """, (month, category.strip()))

        return cursor.rowcount > 0


if __name__ == "__main__":
    initialize_database()

    print("Smart Expense Tracker")
    print("Enter 'exit' as the description to stop.")

    while True:
        description = input("\nTransaction description: ").strip()

        if description.lower() == "exit":
            break

        try:
            amount = float(input("Amount (₹): "))
            result = add_transaction(description, amount)

            print("\nTransaction saved!")
            print("ID:", result["id"])
            print("Category:", result["category"])
            print("Model score:", f'{result["confidence"]}%')
            print("Needs review:", result["review_required"])

        except (ValueError, sqlite3.Error) as error:
            print("Could not save transaction:", error)

    print("\nSaved transactions:")
    for transaction in get_transactions():
        print(
            transaction["id"],
            transaction["description"],
            transaction["amount"],
            transaction["category"]
        )
