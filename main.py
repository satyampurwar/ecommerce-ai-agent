from agent.workflow import ask_agent
from db.db_setup import create_db_and_tables, populate_database
from vectorstore.faq_vectorstore import FAQVectorStore
from config import DATABASE_FILE, VECTOR_DB_DIR, DATABASE_URL, DATA_FOLDER, CSV_TABLE_MAP
from sqlalchemy import create_engine, text
import os

def initial_setup():
    """
    Performs all setup needed for the project (DB, vector store, etc).
    Only runs on first launch or when files are missing.
    """
    print("Performing initial setup ...")
    # 1. Database
    engine = create_db_and_tables(database_url=DATABASE_URL)
    populate_database(engine, data_folder=DATA_FOLDER, table_map=CSV_TABLE_MAP)
    # 2. Vectorstore
    print("Ensuring FAQ vector store is ready ...")
    FAQVectorStore()  # Will populate if empty
    print("Setup complete.\n")

def vectorstore_exists() -> bool:
    """Return True if the FAQ vector store directory looks populated."""
    return os.path.isdir(VECTOR_DB_DIR) and len(os.listdir(VECTOR_DB_DIR)) > 0

def db_has_orders() -> bool:
    """Return True if the orders table exists and has rows."""
    if not os.path.exists(DATABASE_FILE):
        return False
    try:
        engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
        with engine.connect() as conn:
            conn.execute(text("SELECT 1 FROM olist_orders_dataset LIMIT 1"))
        return True
    except Exception:
        return False

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
    run_setup = not (db_has_orders() and vectorstore_exists())
    if run_setup:
        initial_setup()
    cli_loop()
