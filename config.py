import os
from dotenv import load_dotenv

# Load variables from .env at project root
load_dotenv()

# === Paths & Directories ===
# Resolve paths relative to this file so scripts can be executed from any
# working directory.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATA_FOLDER = os.getenv("DATA_FOLDER", os.path.join(BASE_DIR, "data"))
VECTOR_DB_DIR = os.getenv("VECTOR_DB_DIR", os.path.join(BASE_DIR, "faq_vectorstore"))
db_file = os.getenv("DATABASE_FILE", "olist.db")
if not os.path.isabs(db_file):
    db_file = os.path.join(BASE_DIR, db_file)
DATABASE_FILE = db_file
DATABASE_URL = f"sqlite:///{DATABASE_FILE}"

# === External API Keys ===
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
HUGGINGFACE_API_TOKEN = os.getenv("HUGGINGFACE_API_TOKEN")

# Choose LLM provider: 'openai' or 'huggingface'
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai").lower()

# === LLM Settings ===
OPENAI_MODEL_NAME = os.getenv("OPENAI_MODEL_NAME", "gpt-4o-mini")
OPENAI_TEMPERATURE = float(os.getenv("OPENAI_TEMPERATURE", "0.2"))
OPENAI_MAX_TOKENS = int(os.getenv("OPENAI_MAX_TOKENS", "512"))
HUGGINGFACE_MODEL_NAME = os.getenv("HUGGINGFACE_MODEL_NAME", "EleutherAI/gpt-neo-2.7B")

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
    if LLM_PROVIDER == "openai" and not OPENAI_API_KEY:
        raise RuntimeError("OPENAI_API_KEY is not set in your environment (.env)")
    if LLM_PROVIDER == "huggingface" and not HUGGINGFACE_API_TOKEN:
        raise RuntimeError("HUGGINGFACE_API_TOKEN is not set in your environment (.env)")
    if not os.path.isdir(DATA_FOLDER):
        print(f"Warning: DATA_FOLDER '{DATA_FOLDER}' does not exist.")

# Optionally run this at program start
# sanity_check()
