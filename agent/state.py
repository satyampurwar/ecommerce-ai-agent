"""Pydantic models for workflow state and short-term memory."""

from __future__ import annotations

from typing import Optional, List, Dict, Any

from pydantic import BaseModel, Field


class AgentTurn(BaseModel):
    """Single user/agent exchange stored in history."""

    user: str
    agent: str


class AgentState(BaseModel):
    """State object passed through the LangGraph workflow."""

    input: str
    classification: Optional[str] = None
    tool_output: Optional[str] = None
    output: Optional[str] = None
    history: List[AgentTurn] = Field(default_factory=list)
    intermediate_steps: Optional[List[Dict[str, Any]]] = None
    context: Optional[Dict[str, Any]] = None

    def add_turn(self, user: str, agent: str, limit: int = 3) -> None:
        """Append a Q&A pair and trim history to the last ``limit`` turns."""

        self.history.append(AgentTurn(user=user, agent=agent))
        if limit > 0:
            self.history = self.history[-limit:]
