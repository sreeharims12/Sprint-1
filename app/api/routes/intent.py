from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.agents.intent_agent import intent_agent, IntentAgentState
from app.storage import save_output

router = APIRouter(prefix="/intent", tags=["Intent Agent"])


class IntentRequest(BaseModel):
    query: str


class IntentResponse(BaseModel):
    status: str
    intent: dict | None = None
    clarification_questions: list[str] = []
    error: str | None = None


@router.post("/extract", response_model=IntentResponse)
async def extract_intent(request: IntentRequest):
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")

    initial_state = IntentAgentState(raw_input=request.query)

    try:
        raw_result = intent_agent.invoke(initial_state)

        # LangGraph returns a dict — convert it back to our model
        result = IntentAgentState(**raw_result)

    except Exception as e:
        response = IntentResponse(
            status="error",
            error=str(e),
        )
        save_output(request.query, response.model_dump())
        return response

    if result.error:
        response = IntentResponse(
            status="error",
            error=result.error
        )
        save_output(request.query, response.model_dump())
        return response

    if result.needs_clarification:
        response = IntentResponse(
            status="needs_clarification",
            intent=result.intent.model_dump() if result.intent else None,
            clarification_questions=result.clarification_questions
        )
        save_output(request.query, response.model_dump())
        return response

    response = IntentResponse(
        status="complete",
        intent=result.intent.model_dump()
    )
    save_output(request.query, response.model_dump())
    return response
