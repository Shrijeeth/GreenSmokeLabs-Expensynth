from fastapi import APIRouter, BackgroundTasks, HTTPException
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR

from green_smoke_labs_expensynth.configs.database import use_db_session
from green_smoke_labs_expensynth.services.transaction_parsing_service import (
    TransactionParserWorkflow,
)

from ..schemas.transaction_parsing_schemas import ParseTransactionRequest
from ..schemas.db_schemas import transactions
from datetime import datetime
from sqlalchemy import insert


router = APIRouter()


@router.post("/parse-transaction")
@use_db_session
async def parse_transaction(params: ParseTransactionRequest, db, background_tasks: BackgroundTasks):
    try:
        flow = TransactionParserWorkflow()
        response = await flow.kickoff_async(
            inputs=params.model_dump(),
        )
        background_tasks.add_task(_insert_into_db, db, response)

        return response
    except Exception as e:
        raise HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@use_db_session
async def _insert_into_db(db=None, response=None):
    print(f"Inserting into DB: {response}")
    data = response.get("data", {})
    message = response.get("original_message", "")

    transaction_date = data.get("transaction_date")
    if not transaction_date:
        transaction_date = datetime.utcnow()
    else:
        transaction_date = datetime.fromisoformat(transaction_date)
        insert_stmt = insert(transactions).values(
            created_at=transaction_date,
            updated_at=transaction_date,
            user_id=606,
            transaction_type=data.get("transaction_type"),
            amount=data.get("transaction_amount"),
            category=data.get("transaction_category"),
            third_party=data.get("third_party_name"),
            message=message,
        )

        await db.execute(insert_stmt)
        await db.commit()

    return {"success": True, "message": "Transaction saved", "data": data}