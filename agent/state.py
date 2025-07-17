from typing import TypedDict, Optional, List, Dict, Any

class AgentState(TypedDict, total=False):
    """
    The main state dict passed through the agent workflow graph.
    - input: The user's query (string).
    - classification: The intent determined by the LLM (string).
    - tool_output: The result of calling a tool (string).
    - output: The final agent answer to be returned (string).
    - history: (Optional) List of past Q&A interactions.
    - intermediate_steps: (Optional) Used for multi-hop reasoning or tool chaining.
    - context: (Optional) Dict for storing temporary values, e.g. extracted entities, order_id, etc.
    """
    input: str
    classification: str
    tool_output: str
    output: str
    history: Optional[List[Dict[str, Any]]]
    intermediate_steps: Optional[List[Dict[str, Any]]]
    context: Optional[Dict[str, Any]]

# Example helper: define a single Q&A turn (for history, if you wish to support conversation memory)
class AgentTurn(TypedDict):
    user: str
    agent: str

# Example helper: use this to append to state['history']
def add_turn_to_history(state: AgentState, user: str, agent: str):
    """
    Adds a Q&A pair to the state's history list.
    """
    if 'history' not in state or state['history'] is None:
        state['history'] = []
    state['history'].append({'user': user, 'agent': agent})
    return state

# Usage in your workflow:
# from agent.state import AgentState, add_turn_to_history
# state = add_turn_to_history(state, user_query, agent_answer)