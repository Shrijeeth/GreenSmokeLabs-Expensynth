from pydantic import BaseModel


class ParseTransactionRequest(BaseModel):
    transaction_message: str
