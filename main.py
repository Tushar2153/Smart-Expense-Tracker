
from datetime import date
from typing import Optional

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field


from expense_service import (
    initialize_database,
    add_transaction,
    get_transactions,
    predict_category,
    save_budget,
    get_budget_status,
    delete_budget,
)

app = FastAPI(
    title="Smart Expense Tracker API",
    description="API for expense categorization and transaction management.",
    version="1.0.0",
)

# Initialize the SQLite database when the application starts.
initialize_database()


# ---------- Request schemas ----------

class TransactionInput(BaseModel):
    description: str = Field(
        min_length=1,
        max_length=500,
        description="Transaction or merchant description",
    )
    amount: float = Field(
        ge=0,
        description="Transaction amount in rupees",
    )
    transaction_date: Optional[date] = None


class PredictionInput(BaseModel):
    description: str = Field(
        min_length=1,
        max_length=500,
    )

class BudgetInput(BaseModel):
    month: str = Field(
        min_length=7,
        max_length=7,
        description="Budget month in YYYY-MM format",
    )
    category: str = Field(
        min_length=1,
        max_length=100,
        description="Use Overall for the monthly total budget",
    )
    amount: float = Field(
        gt=0,
        description="Budget limit in rupees",
    )


# ---------- API endpoints ----------

@app.get("/")
def home():
    return {
        "message": "Smart Expense Tracker API is running",
        "docs": "/docs",
    }


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.post("/predict")
def predict_expense(data: PredictionInput):
    description = data.description.strip()

    if not description:
        raise HTTPException(
            status_code=422,
            detail="Description cannot be empty.",
        )

    category, confidence, review_required = predict_category(
        description
    )

    return {
        "description": description,
        "category": category,
        "confidence_percent": round(confidence * 100, 1),
        "review_required": review_required,
    }


@app.post("/transactions", status_code=201)
def create_transaction(data: TransactionInput):
    description = data.description.strip()

    if not description:
        raise HTTPException(
            status_code=422,
            detail="Description cannot be empty.",
        )

    try:
        result = add_transaction(
            description=description,
            amount=data.amount,
            transaction_date=(
                data.transaction_date.isoformat()
                if data.transaction_date
                else None
            ),
        )
        return result

    except ValueError as error:
        raise HTTPException(
            status_code=422,
            detail=str(error),
        )


@app.get("/transactions")
def list_transactions(
    limit: int = Query(default=100, ge=1, le=500),
):
    transactions = get_transactions()
    return {
        "count": min(len(transactions), limit),
        "transactions": transactions[:limit],
    }


@app.get("/budgets")
def list_budgets(month: Optional[str] = None):
    selected_month = month or date.today().strftime("%Y-%m")

    try:
        budgets = get_budget_status(selected_month)
        return {
            "month": selected_month,
            "budgets": budgets,
        }
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error))


@app.put("/budgets", status_code=200)
def create_or_update_budget(data: BudgetInput):
    try:
        return save_budget(
            month=data.month,
            category=data.category,
            amount=data.amount,
        )
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error))


@app.delete("/budgets")
def remove_budget(month: str, category: str):
    try:
        deleted = delete_budget(month, category)

        if not deleted:
            raise HTTPException(
                status_code=404,
                detail="Budget not found.",
            )

        return {
            "message": "Budget deleted successfully.",
            "month": month,
            "category": category,
        }
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error))

