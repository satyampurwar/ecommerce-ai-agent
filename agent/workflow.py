from langgraph.graph import StateGraph
from agent.state import AgentState
from llm.llm import classify_intent, chat_completion
from tools.business_tools import (
    search_faq,
    get_order_status,
    get_refund_status,
    get_review
)
from db.db_setup import get_session
from config import DATABASE_URL
from sqlalchemy import create_engine, text
import datetime

# Engine will be lazily initialised when the workflow is used
engine = None

def initialize_engine(database_url: str = DATABASE_URL):
    """Create the database engine if it hasn't been created yet."""
    global engine
    if engine is None:
        engine = create_engine(database_url, connect_args={"check_same_thread": False})
        # Ensure foreign key constraints are enforced for SQLite
        with engine.connect() as conn:
            conn.execute(text("PRAGMA foreign_keys=ON"))
    return engine

def perception_node(state: AgentState) -> AgentState:
    """
    Intent classification node: uses LLM to determine query intent.
    """
    query = state["input"]
    intent = classify_intent(query)
    state["classification"] = intent
    return state

def tool_node(state: AgentState) -> AgentState:
    """
    Dispatch to the correct tool based on classified intent.
    """
    classification = state["classification"]
    query = state["input"]
    engine_local = initialize_engine()
    session = get_session(engine_local)
    try:
        if classification == "order_status":
            output = get_order_status(query, session)
        elif classification == "faq":
            output = search_faq(query)
        elif classification == "refund_status":
            output = get_refund_status(query, session)
        elif classification == "review":
            output = get_review(query, session)
        else:
            output = "I'm sorry, I could not classify your request."
    except Exception as e:
        output = f"Error during tool dispatch: {e}"
    finally:
        session.close()
    state["tool_output"] = output
    return state

def answer_node(state: AgentState) -> AgentState:
    """
    Formats the output for final agent answer.
    """
    answer = state["tool_output"]
    state["output"] = answer
    return state

def log_interaction(user_query: str, agent_answer: str):
    """
    Logs Q&A for learning, retraining, or analytics.
    """
    with open("agent_interactions.log", "a", encoding="utf-8") as f:
        f.write(f"{datetime.datetime.now().isoformat()} | Q: {user_query} | A: {agent_answer}\n")

def learning_node(state: AgentState) -> AgentState:
    """
    Learning step: log output for future improvement.
    """
    log_interaction(state.get("input", ""), state.get("output", ""))
    return state

def build_workflow() -> StateGraph:
    """
    Compiles the LangGraph workflow using AgentState.
    Returns the compiled StateGraph.
    """
    workflow = StateGraph(AgentState)
    workflow.add_node("perception", perception_node)
    workflow.add_node("tool_use", tool_node)
    workflow.add_node("answer", answer_node)
    workflow.add_node("learning", learning_node)
    workflow.add_edge("__start__", "perception")
    workflow.add_edge("perception", "tool_use")
    workflow.add_edge("tool_use", "answer")
    workflow.add_edge("answer", "learning")
    return workflow.compile()

# --- Main agent callable ---

graph = build_workflow()

def ask_agent(user_query: str) -> str:
    """
    Single entrypoint for conversational agent.
    Returns agent's answer for a user query.
    """
    state = {"input": user_query}
    result = graph.invoke(state)
    return result["output"]

# Example usage for CLI
if __name__ == "__main__":
    print("Ecommerce AI Agent (type 'quit' to exit).")
    while True:
        q = input("You: ")
        if q.lower() in {"quit", "exit"}:
            break
        print("AI:", ask_agent(q))
