"""Workflow definition for the conversational agent."""

from langgraph.graph import StateGraph
from langgraph.checkpoint.memory import InMemorySaver
from agent.state import AgentState
from llm.llm import classify_intent, rephrase_text
from tools.business_tools import (
    search_faq,
    get_order_status,
    get_refund_status,
    get_review,
    get_order_details,
)
from db.db_setup import get_session
from config import DATABASE_URL, LOG_FILE
from sqlalchemy import create_engine, text
import datetime

# Engine is created lazily when the workflow first needs DB access
engine = None

def initialize_engine(database_url: str = DATABASE_URL):
    """Create the database engine if it hasn't been created yet."""
    global engine
    if engine is None:
        # Create a new engine instance. check_same_thread=False allows
        # SQLite to be accessed from different threads (as LangGraph may).
        engine = create_engine(database_url, connect_args={"check_same_thread": False})
        # Ensure foreign key constraints are enforced for SQLite
        with engine.connect() as conn:
            conn.execute(text("PRAGMA foreign_keys=ON"))
    return engine

def perception_node(state: AgentState) -> AgentState:
    """Intent classification node."""

    query = state.input
    # Use the LLM to determine what the user wants to do
    intent = classify_intent(query)
    state.classification = intent
    return state

def tool_node(state: AgentState) -> AgentState:
    """Dispatch to the correct tool based on classified intent."""

    classification = state.classification
    query = state.input
    # Lazily create DB engine and session for each invocation
    engine_local = initialize_engine()
    session = get_session(engine_local)
    try:
        # Route the request to the appropriate business tool
        if classification == "order_status":
            output = get_order_status(query, session)
        elif classification == "order_details":
            output = get_order_details(query, session)
        elif classification == "faq":
            output = search_faq(query)
        elif classification == "refund_status":
            output = get_refund_status(query, session)
        elif classification == "review":
            output = get_review(query, session)
        else:
            output = "I'm sorry, I could not classify your request."
    except Exception as e:
        # Any unexpected error is returned to the user for visibility
        output = f"Error during tool dispatch: {e}"
    finally:
        # Always close the DB session
        session.close()
    state.tool_output = output
    return state

def answer_node(state: AgentState) -> AgentState:
    """
    Formats the output for final agent answer.
    """
    # Take the raw tool output and rephrase it for a nicer user experience
    answer = state.tool_output or ""
    rephrased = rephrase_text(answer)
    state.output = rephrased
    return state

def log_interaction(user_query: str, agent_answer: str) -> None:
    """
    Logs Q&A for learning, retraining, or analytics.
    """
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        # Store timestamped interaction for later analysis or fine tuning
        f.write(
            f"{datetime.datetime.now().isoformat()} | Q: {user_query} | A: {agent_answer}\n"
        )

def learning_node(state: AgentState) -> AgentState:
    """Learning step: log output for future improvement."""

    log_interaction(state.input, state.output or "")
    return state

def build_workflow() -> StateGraph:
    """Compile the LangGraph workflow with in-memory checkpointing."""

    checkpointer = InMemorySaver()
    workflow = StateGraph(AgentState)
    workflow.add_node("perception", perception_node)
    workflow.add_node("tool_use", tool_node)
    workflow.add_node("answer", answer_node)
    workflow.add_node("learning", learning_node)
    workflow.add_edge("__start__", "perception")
    workflow.add_edge("perception", "tool_use")
    workflow.add_edge("tool_use", "answer")
    workflow.add_edge("answer", "learning")
    return workflow.compile(checkpointer=checkpointer)

# --- Main agent callable ---

graph = build_workflow()

_conversation_state: AgentState | None = None
_THREAD_ID = "default"


def ask_agent(user_query: str) -> str:
    """Single entrypoint for the conversational agent with short-term memory."""

    global _conversation_state
    if _conversation_state is None:
        _conversation_state = AgentState(input=user_query)
    else:
        _conversation_state.input = user_query
        _conversation_state.classification = None
        _conversation_state.tool_output = None
        _conversation_state.output = None

    # Execute the workflow and update state
    _conversation_state = graph.invoke(
        _conversation_state, config={"configurable": {"thread_id": _THREAD_ID}}
    )
    if isinstance(_conversation_state, dict):
        _conversation_state = AgentState.model_validate(_conversation_state)
    assert _conversation_state is not None
    # Append to short-term history (keep last 3 turns)
    _conversation_state.add_turn(user_query, _conversation_state.output or "")
    return _conversation_state.output or ""

# Example usage for CLI
if __name__ == "__main__":
    print("Ecommerce AI Agent (type 'quit' to exit).")
    while True:
        q = input("You: ")
        if q.lower() in {"quit", "exit"}:
            break
        print("AI:", ask_agent(q))
