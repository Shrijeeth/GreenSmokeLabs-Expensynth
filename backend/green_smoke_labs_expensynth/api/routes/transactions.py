from datetime import datetime
from typing import Any, Dict, List

from fastapi import APIRouter, HTTPException
from sqlalchemy import and_, case, extract, func, select

from green_smoke_labs_expensynth.api.schemas.db_schemas import transactions
from green_smoke_labs_expensynth.api.schemas.transaction_schemas import (
    YearlyCategoryDistributionResponse,
    YearlyTransactionSummaryResponse,
)
from green_smoke_labs_expensynth.configs.database import use_db_session
from green_smoke_labs_expensynth.utils.types import TransactionCategory

router = APIRouter()


@router.get(
    "/transactions/category-distribution/{year}",
    response_model=YearlyCategoryDistributionResponse,
)
@use_db_session
async def get_category_distribution(
    year: int = datetime.now().year,
    user_id: int = 606,  # Default user_id, can be changed based on auth
    db=None,
):
    """
    Get financial distribution by category for a specific year, and return all categories.
    """
    try:
        categories = TransactionCategory.get_all()
        # Query to get sum(amount) grouped by category for the year
        query = (
            select(
                transactions.c.category,
                func.coalesce(func.sum(transactions.c.amount), 0).label("total"),
            )
            .where(
                and_(
                    transactions.c.user_id == user_id,
                    extract("year", transactions.c.created_at) == year,
                )
            )
            .group_by(transactions.c.category)
        )
        result = await db.execute(query)
        data = dict(result.all())
        # Ensure all categories are present in the response
        distribution = {cat: float(data.get(cat, 0.0)) for cat in categories}
        return {
            "year": year,
            "categories": categories,
            "distribution": distribution,
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error fetching category distribution: {str(e)}"
        )


# Month number to abbreviation mapping
MONTH_ABBR = {
    1: "Jan",
    2: "Feb",
    3: "Mar",
    4: "Apr",
    5: "May",
    6: "Jun",
    7: "Jul",
    8: "Aug",
    9: "Sep",
    10: "Oct",
    11: "Nov",
    12: "Dec",
}


@router.get(
    "/transactions/monthly-summary/{year}",
    response_model=YearlyTransactionSummaryResponse,
)
@use_db_session
async def get_monthly_transaction_summary(
    year: int = datetime.now().year,
    user_id: int = 606,  # Default user_id, can be changed based on auth
    db=None,
):
    """
    Get monthly credit and expenses summary for a specific year.

    Args:
        year: The year to get the summary for (default: current year)
        user_id: The user ID to filter transactions (default: 1)

    Returns:
        YearlyTransactionSummaryResponse with monthly credit and expenses
    """
    try:
        # Query to get monthly credit amounts
        credit_query = (
            select(
                extract("month", transactions.c.created_at).label("month"),
                func.coalesce(func.sum(transactions.c.amount), 0).label("total_credit"),
            )
            .where(
                and_(
                    transactions.c.user_id == user_id,
                    transactions.c.transaction_type == "CREDIT",
                    extract("year", transactions.c.created_at) == year,
                )
            )
            .group_by(extract("month", transactions.c.created_at))
        )

        # Query to get monthly expense amounts
        expense_query = (
            select(
                extract("month", transactions.c.created_at).label("month"),
                func.coalesce(func.sum(transactions.c.amount), 0).label(
                    "total_expense"
                ),
            )
            .where(
                and_(
                    transactions.c.user_id == user_id,
                    transactions.c.transaction_type == "DEBIT",
                    extract("year", transactions.c.created_at) == year,
                )
            )
            .group_by(extract("month", transactions.c.created_at))
        )

        # Execute queries
        credit_result = await db.execute(credit_query)
        expense_result = await db.execute(expense_query)

        # Convert to dictionaries for easier processing
        credit_data = {int(row.month): float(row.total_credit) for row in credit_result}
        expense_data = {
            int(row.month): float(row.total_expense) for row in expense_result
        }

        # Initialize response data
        months = []
        credits = []
        expenses = []

        # Fill data for all 12 months
        for month_num in range(1, 13):
            months.append(MONTH_ABBR[month_num])
            credits.append(credit_data.get(month_num, 0.0))
            expenses.append(expense_data.get(month_num, 0.0))

        return {
            "year": year,
            "months": months,
            "credits": credits,
            "expenses": expenses,
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error fetching transaction summary: {str(e)}"
        )
