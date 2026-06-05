from langgraph.graph import StateGraph, END
from .schemas import IntentAgentState
from .extractor import extract_intent_node, generate_clarification_questions_node


def _route_after_extraction(state: IntentAgentState) -> str:
    """
    Conditional edge function.
    Decides which node to go to after extraction runs.

    - Error occurred       → "clarify" (ask user to rephrase)
    - Confidence < 0.90    → "clarify" (missing fields)
    - Confidence >= 0.90   → "done"    (pass to Discovery Agent)
    """
    if state.error or state.needs_clarification:
        return "clarify"
    return "done"


def build_intent_agent():
    """
    Builds and compiles the LangGraph state graph for the Intent Agent.

    Graph structure:
        [START]
           |
        extract  ← calls LLM, produces IntentOutput
           |
        [conditional edge: _route_after_extraction]
          / \
    clarify  done
       |       |
      END     END
    """
    graph = StateGraph(IntentAgentState)

    # Register nodes
    graph.add_node("extract", extract_intent_node)
    graph.add_node("clarify", generate_clarification_questions_node)

    # Entry point
    graph.set_entry_point("extract")

    # Conditional routing after extraction
    graph.add_conditional_edges(
        "extract",
        _route_after_extraction,
        {
            "clarify": "clarify",
            "done":    END,
        }
    )

    # Clarify always ends after generating questions
    graph.add_edge("clarify", END)

    return graph.compile()


# Module-level singleton — import this in the route
intent_agent = build_intent_agent()
