"""Minimal Gradio UI for chatting with the agent."""
import warnings
warnings.filterwarnings("ignore", category=UserWarning, module="gradio")

import gradio as gr
from agent.workflow import ask_agent
from main import db_has_orders, vectorstore_exists, initial_setup


def ensure_setup():
    """Run the heavy setup steps if the DB or vector store are missing."""
    if not (db_has_orders() and vectorstore_exists()):
        initial_setup()

ensure_setup()

def gradio_ask(message: str, history: list[tuple[str, str]]) -> str:
    """Wrapper for gradio ChatInterface."""
    return ask_agent(message)

# Instantiate the basic chat interface
demo = gr.ChatInterface(
    fn=gradio_ask,
    title="Ecommerce AI Agent",
    description="Ask questions about orders or general FAQs",
)

if __name__ == "__main__":
    # Bind to 0.0.0.0 so the Gradio server is reachable from outside the
    # container when running under Docker or Docker Compose.
    demo.launch(server_name="0.0.0.0", server_port=7860)