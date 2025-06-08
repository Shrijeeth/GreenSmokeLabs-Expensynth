from fastapi import APIRouter, HTTPException
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR

from green_smoke_labs_expensynth.api.schemas.bot_schemas import ChatHistory
from green_smoke_labs_expensynth.services.user_query_service.query_parser_workflow.flow import (
    FinancialAssistantWorkflow,
)

router = APIRouter()


@router.post("/query")
async def ask_bot(history: ChatHistory):
    try:
        user_message = None
        for msg in reversed(history.messages):
            if msg.role == "user":
                user_message = msg.content
                break
        if not user_message:
            raise HTTPException(status_code=400, detail="No user message found in chat history.")

        # Run the workflow
        flow = FinancialAssistantWorkflow()
        result = await flow.kickoff_async(inputs={"user_query": user_message})
        return result
    except Exception as e:
        raise HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
