from agent.workflow import ask_agent
from config import DATABASE_FILE, VECTOR_DB_DIR, DATABASE_URL
from sqlalchemy import create_engine, text
import subprocess
import os

def initial_setup():
    """
    Performs all setup needed for the project (DB, vector store, etc).
    Only runs on first launch or when files are missing.
    """
    print("[SETUP] Performing initial setup ...")
    print("[SETUP] Creating and populating database ...")
    subprocess.run(["python", "-m", "db.db_setup"], check=True)
    print("[SETUP] Building FAQ vector store ...")
    subprocess.run(["python", "-m", "vectorstore.faq_vectorstore"], check=True)
    print("[SETUP] Initial setup complete.\n")

def vectorstore_exists() -> bool:
    """Return True if the FAQ vector store directory looks populated."""
    result = os.path.isdir(VECTOR_DB_DIR) and len(os.listdir(VECTOR_DB_DIR)) > 0
    print(f"[CHECK] Vectorstore exists: {result}")
    return result

def db_has_orders() -> bool:
    """Return True if the orders table exists and has rows."""
    if not os.path.exists(DATABASE_FILE):
        print(f"[CHECK] DB file {DATABASE_FILE} does not exist.")
        return False
    try:
        engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
        with engine.connect() as conn:
            conn.execute(text("SELECT 1 FROM olist_orders_dataset LIMIT 1"))
        print("[CHECK] DB has data in 'olist_orders_dataset'.")
        return True
    except Exception as e:
        print(f"[CHECK] DB check failed or orders table is empty: {e}")
        return False

def cli_loop():
    """
    Simple command-line chat loop for testing the agent.
    """
    print("\nEcommerce AI Agent (type 'quit' or 'exit' to stop).")
    while True:
        user_query = input("You: ")
        if user_query.strip().lower() in {"quit", "exit"}:
            print("Goodbye!")
            break
        response = ask_agent(user_query)
        print("AI:", response)

if __name__ == "__main__":
    print("[MAIN] Starting main.py ...")
    run_setup = not (db_has_orders() and vectorstore_exists())
    print(f"[MAIN] Run initial setup? {run_setup}")
    if run_setup:
        initial_setup()
    else:
        print("[MAIN] Skipping setup; DB and vectorstore look ready.")
    cli_loop()
