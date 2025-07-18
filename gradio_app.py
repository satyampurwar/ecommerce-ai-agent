import gradio as gr
from agent.workflow import ask_agent
from main import db_has_orders, vectorstore_exists, initial_setup


def ensure_setup():
    if not (db_has_orders() and vectorstore_exists()):
        initial_setup()


ensure_setup()

def gradio_ask(message: str, history: list[tuple[str, str]]) -> str:
    """Wrapper for gradio ChatInterface."""
    return ask_agent(message)


demo = gr.ChatInterface(
    fn=gradio_ask,
    title="Ecommerce AI Agent",
    description="Ask questions about orders or general FAQs",
)

if __name__ == "__main__":
    demo.launch()
