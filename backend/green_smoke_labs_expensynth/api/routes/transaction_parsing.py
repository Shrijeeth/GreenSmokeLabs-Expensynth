from fastapi import APIRouter, HTTPException
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR

from green_smoke_labs_expensynth.services.transaction_parsing_service import (
    TransactionParserWorkflow,
)

from ..schemas.transaction_parsing_schemas import ParseTransactionRequest

router = APIRouter()


@router.post("/parse-transaction")
async def parse_transaction(params: ParseTransactionRequest):
    try:
        flow = TransactionParserWorkflow()
        return await flow.kickoff_async(
            inputs=params.model_dump(),
        )
    except Exception as e:
        raise HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
