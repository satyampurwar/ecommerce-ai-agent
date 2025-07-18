import gradio as gr
from agent.workflow import ask_agent
from main import db_has_orders, vectorstore_exists, initial_setup


def ensure_setup():
    if not (db_has_orders() and vectorstore_exists()):
        initial_setup()


ensure_setup()

demo = gr.ChatInterface(
    fn=ask_agent,
    title="Ecommerce AI Agent",
    description="Ask questions about orders or general FAQs",
)

if __name__ == "__main__":
    demo.launch()
