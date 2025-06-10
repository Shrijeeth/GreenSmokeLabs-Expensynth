from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class MonthlyTransactionSummary(BaseModel):
    month: str  # e.g., "Jan", "Feb", etc.
    credit: float
    expenses: float


class YearlyTransactionSummaryResponse(BaseModel):
    months: List[str]  # e.g., ["Jan", "Feb", ...]
    credits: List[float]
    expenses: List[float]
    year: int = datetime.now().year  # Default to current year


class YearlyCategoryDistributionResponse(BaseModel):
    year: int
    categories: List[str]
    distribution: dict[str, float]
