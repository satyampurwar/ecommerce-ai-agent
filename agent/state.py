"""Pydantic models for workflow state and short-term memory."""

from __future__ import annotations

from typing import Optional, List, Dict, Any

from pydantic import BaseModel, Field


class AgentTurn(BaseModel):
    """Container for a single question and answer pair.

    Attributes
    ----------
    user : str
        Text of the user question.
    agent : str
        Response text from the agent.
    """

    user: str
    agent: str


class AgentState(BaseModel):
    """Mutable state used by the workflow.

    Parameters
    ----------
    input : str
        The latest user query.
    classification : str, optional
        Detected intent label.
    tool_output : str, optional
        Raw output from the selected tool.
    output : str, optional
        Final answer returned to the user.
    history : list[AgentTurn]
        Recent conversation turns.
    intermediate_steps : list[dict], optional
        Debug information from the workflow.
    context : dict, optional
        Extra values that tools may attach.
    """

    input: str
    classification: Optional[str] = None
    tool_output: Optional[str] = None
    output: Optional[str] = None
    history: List[AgentTurn] = Field(default_factory=list)
    intermediate_steps: Optional[List[Dict[str, Any]]] = None
    context: Optional[Dict[str, Any]] = None

    def add_turn(self, user: str, agent: str, limit: int = 3) -> None:
        """Append a new conversation turn and optionally trim history.

        Parameters
        ----------
        user : str
            The user's message.
        agent : str
            The agent's response.
        limit : int, optional
            Number of turns of history to keep. ``0`` keeps everything.
        """

        self.history.append(AgentTurn(user=user, agent=agent))
        if limit > 0:
            self.history = self.history[-limit:]
