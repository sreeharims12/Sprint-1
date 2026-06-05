from pydantic import BaseModel, Field
from typing import Optional, Literal


class IntentOutput(BaseModel):
    """
    Structured procurement intent extracted from raw user input.
    Every downstream agent reads from this object.
    """
    service_category: str = Field(
        description="Service type e.g. plumber, electrician, house cleaner"
    )
    location: Optional[str] = Field(
        default=None,
        description="City, district, or address where the service is needed"
    )
    budget_min: Optional[float] = Field(
        default=None,
        description="Minimum budget in the specified currency"
    )
    budget_max: Optional[float] = Field(
        default=None,
        description="Maximum budget the user will not exceed"
    )
    currency: str = Field(
        default="EUR",
        description="ISO currency code e.g. EUR, USD, GBP"
    )
    timeline: Optional[str] = Field(
        default=None,
        description="When the service is needed e.g. tomorrow morning, this week"
    )
    urgency: Literal["low", "medium", "high"] = Field(
        default="medium",
        description="Urgency level inferred from language and timeline"
    )
    detected_language: Literal["en", "de"] = Field(
        default="en",
        description="Language detected in the original user query"
    )
    raw_query: str = Field(
        default="",
        description="Original unmodified user input preserved for audit"
    )
    confidence: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Overall extraction confidence from 0.0 to 1.0"
    )
    missing_fields: list[str] = Field(
        default_factory=list,
        description="Field names the model could not determine"
    )
    special_requirements: Optional[str] = Field(
        default=None,
        description="Extra constraints e.g. must speak German, needs certification"
    )


class IntentAgentState(BaseModel):
    """
    LangGraph state — flows through every node in the graph.
    Each node reads from this and returns an updated copy.
    """
    raw_input: str
    intent: Optional[IntentOutput] = None
    needs_clarification: bool = False
    clarification_questions: list[str] = Field(default_factory=list)
    error: Optional[str] = None
