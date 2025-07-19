from __future__ import annotations

"""Langfuse observability helpers."""

import contextvars
from typing import Any
from langfuse import Langfuse
from config import LANGFUSE_PUBLIC_KEY, LANGFUSE_SECRET_KEY, LANGFUSE_HOST

_langfuse: Langfuse | None = None
_current_trace = contextvars.ContextVar("current_trace", default=None)

def get_langfuse() -> Langfuse | None:
    """Return a Langfuse client if keys are configured."""
    global _langfuse
    if _langfuse is None and LANGFUSE_PUBLIC_KEY and LANGFUSE_SECRET_KEY:
        _langfuse = Langfuse(
            public_key=LANGFUSE_PUBLIC_KEY,
            secret_key=LANGFUSE_SECRET_KEY,
            host=LANGFUSE_HOST or None,
        )
    return _langfuse

def start_trace(name: str, input: Any | None = None):
    """Start a Langfuse trace and set it as current."""
    lf = get_langfuse()
    if not lf:
        return None
    try:
        trace = lf.trace(name=name, input=input)
    except Exception:
        trace = None
    _current_trace.set(trace)
    return trace

def end_trace() -> None:
    """End and clear the current trace."""
    trace = _current_trace.get()
    if trace is not None:
        try:
            trace.end()
        except Exception:
            pass
    _current_trace.set(None)

def current_trace_id() -> str | None:
    """Return the ID of the current trace if one is active."""
    trace = _current_trace.get()
    return trace.id if trace else None


def log_metric(name: str, value: float, trace_id: str | None = None, **kwargs) -> None:
    """Record a custom metric in Langfuse if available."""
    lf = get_langfuse()
    if lf and hasattr(lf, "metric"):
        try:
            lf.metric(name=name, value=value, trace_id=trace_id, **kwargs)
        except Exception:
            pass


def log_score(name: str, value: float, trace_id: str | None = None, **kwargs) -> None:
    """Record an evaluation score in Langfuse if available."""
    lf = get_langfuse()
    if lf and hasattr(lf, "score"):
        try:
            lf.score(name=name, value=value, trace_id=trace_id, **kwargs)
        except Exception:
            pass


def register_prompt(name: str, prompt: str) -> None:
    """Register a prompt template with Langfuse if supported."""
    lf = get_langfuse()
    if lf and hasattr(lf, "prompt"):
        try:
            lf.prompt(name=name, prompt=prompt)
        except Exception:
            pass

if __name__ == "__main__":
    get_langfuse() # Initialize Langfuse client if keys are set 
