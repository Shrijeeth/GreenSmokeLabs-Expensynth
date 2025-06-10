from enum import Enum


class TransactionType(Enum):
    DEBIT = "DEBIT"
    CREDIT = "CREDIT"

    @classmethod
    def get_all(cls):
        return [item.value for item in TransactionType]


class TransactionCategory(Enum):
    FOOD = "FOOD"
    RETAIL = "RETAIL"
    TRAVEL = "TRAVEL"
    ENTERTAINMENT = "ENTERTAINMENT"
    UTILITIES = "UTILITIES"
    HEALTHCARE = "HEALTHCARE"
    FINANCIAL = "FINANCIAL"
    EDUCATION = "EDUCATION"
    OTHER = "OTHER"

    @classmethod
    def get_all(cls):
        return [item.value for item in TransactionCategory]
