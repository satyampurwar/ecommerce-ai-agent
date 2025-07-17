import os
from dotenv import load_dotenv

# Load variables from .env at project root
load_dotenv()

# === Paths & Directories ===
DATA_FOLDER = os.getenv("DATA_FOLDER", "./data")
VECTOR_DB_DIR = os.getenv("VECTOR_DB_DIR", "./faq_vectorstore")
DATABASE_FILE = os.getenv("DATABASE_FILE", "olist.db")
DATABASE_URL = f"sqlite:///{DATABASE_FILE}"

# === External API Keys ===
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
HF_TOKEN = os.getenv("HF_TOKEN")

# === Model & Embedding Settings ===
EMBEDDING_MODEL_NAME = os.getenv("EMBEDDING_MODEL_NAME", "sentence-transformers/all-MiniLM-L6-v2")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "faq")

# === Dataset Config ===
FAQ_DATASET_NAME = os.getenv("FAQ_DATASET_NAME", "Andyrasika/Ecommerce_FAQ")
FAQ_DATASET_SPLIT = os.getenv("FAQ_DATASET_SPLIT", "train")

# === CSV Table Mapping ===
# Maps SQL table name to CSV filename (do not change unless your data changes)
CSV_TABLE_MAP = {
    'olist_customers_dataset' : 'olist_customers_dataset.csv',
    'olist_geolocation_dataset' : 'olist_geolocation_dataset.csv',
    'olist_orders_dataset' : 'olist_orders_dataset.csv',
    'olist_order_items_dataset' : 'olist_order_items_dataset.csv',
    'olist_order_payments_dataset' : 'olist_order_payments_dataset.csv',
    'olist_order_reviews_dataset' : 'olist_order_reviews_dataset.csv',
    'olist_products_dataset' : 'olist_products_dataset.csv',
    'olist_sellers_dataset' : 'olist_sellers_dataset.csv',
    'product_category_name_translation' : 'product_category_name_translation.csv' 
}

# === Other Constants ===
LOG_FILE = os.getenv("LOG_FILE", "agent_interactions.log")

# === Sanity checks (optional, production-safe) ===
def sanity_check():
    if not OPENAI_API_KEY:
        raise RuntimeError("OPENAI_API_KEY is not set in your environment (.env)")
    if not os.path.isdir(DATA_FOLDER):
        print(f"Warning: DATA_FOLDER '{DATA_FOLDER}' does not exist.")
    if not HF_TOKEN:
        print("Warning: HF_TOKEN not set. HuggingFace features may not work.")

# Optionally run this at program start
# sanity_check()
