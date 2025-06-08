from datetime import datetime

from fastapi import APIRouter, BackgroundTasks, HTTPException
from sqlalchemy import insert
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR

from green_smoke_labs_expensynth.configs.database import use_db_session
from green_smoke_labs_expensynth.services.transaction_parsing_service import (
    TransactionParserWorkflow,
)
from green_smoke_labs_expensynth.utils.embeddings import TextFormatter

from ..schemas.db_schemas import transactions
from ..schemas.transaction_parsing_schemas import ParseTransactionRequest

router = APIRouter()
text_formatter = TextFormatter()


@router.post("/parse-transaction")
@use_db_session
async def parse_transaction(params: ParseTransactionRequest, background_tasks: BackgroundTasks, db=None):
    try:
        flow = TransactionParserWorkflow()
        response = await flow.kickoff_async(
            inputs=params.model_dump(),
        )
        background_tasks.add_task(_insert_into_db, db, response)
        background_tasks.add_task(text_formatter.insert_into_vector_db, response.get("original_message"), response.get("data"))

        return response
    except Exception as e:
        raise HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

async def _insert_into_db(db, response):
    print(f"Inserting into DB: {response}")
    data = response.get("data", {})
    message = response.get("original_message", "")

    transaction_date = data.transaction_date
    if not transaction_date:
        transaction_date = datetime.utcnow()
    else:
        transaction_date = datetime.fromisoformat(transaction_date)
        insert_stmt = insert(transactions).values(
            created_at=transaction_date,
            updated_at=transaction_date,
            user_id=606,
            transaction_type=data.transaction_type,
            amount=data.transaction_amount,
            category=data.transaction_category,
            third_party=data.third_party_name,
            message=message,
        )

        await db.execute(insert_stmt)
        await db.commit()

    return {"success": True, "message": "Transaction saved", "data": data}