from typing import Optional

from pydantic import BaseModel, Field

from green_smoke_labs_expensynth.utils.types import TransactionCategory, TransactionType


class ParsedTransactionData(BaseModel):
    transaction_date: str = Field(
        description="Transaction Date in the format YYYY-MM-DD HH:MM:SS"
    )
    transaction_amount: float = Field(description="Transaction Amount")
    third_party_name: str = Field(description="Third Party Name")
    transaction_category: TransactionCategory = Field(
        description="Transaction Category"
    )
    transaction_type: TransactionType = Field(description="Transaction Type")
    card_number: str = Field(
        description="Last 4 digits of Masked Card Number", min_length=4, max_length=4
    )
