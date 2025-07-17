from agent.workflow import ask_agent
from db.db_setup import create_db_and_tables, populate_database
from vectorstore.faq_vectorstore import FAQVectorStore
import os

def initial_setup():
    """
    Performs all setup needed for the project (DB, vector store, etc).
    Only runs on first launch or when files are missing.
    """
    print("Performing initial setup ...")
    # 1. Database
    engine = create_db_and_tables()
    populate_database(engine)
    # 2. Vectorstore
    print("Ensuring FAQ vector store is ready ...")
    FAQVectorStore()  # Will populate if empty
    print("Setup complete.\n")

def cli_loop():
    """
    Simple command-line chat loop for testing the agent.
    """
    print("Ecommerce AI Agent (type 'quit' or 'exit' to stop).")
    while True:
        user_query = input("You: ")
        if user_query.strip().lower() in {"quit", "exit"}:
            print("Goodbye!")
            break
        response = ask_agent(user_query)
        print("AI:", response)

if __name__ == "__main__":
    # Optional: skip setup if running in production where data already exists
    run_setup = not (os.path.exists("olist.db") and os.path.exists("./faq_vectorstore"))
    if run_setup:
        initial_setup()
    cli_loop()