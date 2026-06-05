import os
import json
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from .schemas import IntentOutput, IntentAgentState
from .prompts import INTENT_EXTRACTION_SYSTEM_PROMPT


def get_llm():
    """
    Returns a Groq LLM instance configured for JSON output.
    """
    return ChatGroq(
        api_key=os.getenv("GROQ_API_KEY"),
        model="llama-3.1-8b-instant",
        temperature=0,
    )


def extract_intent_node(state: IntentAgentState) -> IntentAgentState:
    """
    LangGraph node 1: calls the LLM and parses JSON response to get IntentOutput.
    Sets needs_clarification = True if confidence is below 0.90.
    """
    llm = get_llm()

    try:
        # Add JSON instruction to the system prompt
        system_prompt = INTENT_EXTRACTION_SYSTEM_PROMPT + """

RESPOND ONLY WITH VALID JSON. NO OTHER TEXT.
Output must be a single JSON object matching the IntentOutput schema exactly."""

        response = llm.invoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=state.raw_input),
        ])

        # Extract JSON from response
        response_text = response.content.strip()
        
        # Try to parse JSON from the response
        try:
            # If response is wrapped in markdown code blocks, extract it
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()
            
            intent_dict = json.loads(response_text)
        except json.JSONDecodeError as e:
            state.error = f"Failed to parse LLM response as JSON: {str(e)}\nResponse: {response_text}"
            state.needs_clarification = True
            return state

        # Convert dict to IntentOutput
        try:
            result = IntentOutput(**intent_dict)
        except Exception as e:
            state.error = f"Failed to validate intent output: {str(e)}"
            state.needs_clarification = True
            return state

        # Attach the original query for audit trail
        result.raw_query = state.raw_input

        state.intent = result
        state.needs_clarification = result.confidence < 0.90

    except Exception as e:
        state.error = f"Intent extraction failed: {str(e)}"
        state.needs_clarification = True

    return state


def generate_clarification_questions_node(state: IntentAgentState) -> IntentAgentState:
    """
    LangGraph node 2: maps missing fields to human-readable questions.
    Only runs when needs_clarification is True.
    """
    # If extraction itself failed with no intent, ask the most basic questions
    if not state.intent:
        state.clarification_questions = [
            "What type of service are you looking for?",
            "Where do you need this service? (city or district)",
        ]
        return state

    # Maps field names to plain English questions
    field_questions = {
        "location":         "Where do you need this service? (city or district)",
        "service_category": "What type of service are you looking for?",
        "budget_max":       "What is your maximum budget for this service?",
        "timeline":         "When do you need this done?",
    }

    questions = []

    # Add a question for each explicitly missing field
    for field in state.intent.missing_fields:
        if field in field_questions:
            questions.append(field_questions[field])

    # Fallback if confidence is low but no specific fields were flagged
    if not questions and state.needs_clarification:
        questions.append(
            "Could you provide more details? We need to know "
            "what service you need and where you are located."
        )

    state.clarification_questions = questions
    return state
