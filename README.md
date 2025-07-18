# Ecommerce LLM Agent

**Conversational AI for E-commerce Support**

* ✅ Order status and review lookup (by order ID)
* ✅ Comprehensive order details for any order
* ✅ FAQ semantic search (vector DB)
* ✅ Refund/payment check
* ✅ Easily extensible agent workflow (LangGraph/LangChain + OpenAI)
* ✅ SQLAlchemy ORM, Chroma vector DB, HuggingFace embeddings

---

## Features

* **Natural language support** for order queries and FAQ
* **Semantic search**: users get best-match answers from your FAQ corpus
* **Integrated SQL database** from Olist public dataset
* **Vector search with Chroma** (state-of-the-art)
* **Production-ready modular Python codebase**

---

## Project Structure

```
ecommerce_agent/
├── agent/
│   ├── state.py
│   └── workflow.py
├── db/
│   ├── db_setup.py
│   └── models.py
├── tools/
│   └── business_tools.py
├── vectorstore/
│   └── faq_vectorstore.py
├── llm/
│   └── llm.py
├── data/
│   └── ... (CSV files: see below)
├── deploy/
│   └── conda/
│       └── env.yml
├── main.py
├── config.py
├── requirements.txt
├── environment.yml
├── README.md
├── .env
├── agent_interactions.log
└── faq_vectorstore/

```

---

## Quickstart

### 1. Clone and Install

```bash
git clone <your-repo-url>
cd ecommerce-llm-agent
conda env create -f deploy/conda/env.yml
conda activate ecommerce_agent
```

or (with pip):

```bash
pip install -r requirements.txt
```

---

### 2. Prepare Data

* Place all Olist CSV files in the `data/` directory.

  * Example files:

    * `olist_customers_dataset.csv`
    * `olist_geolocation_dataset.csv`
    * `olist_orders_dataset.csv`
    * `olist_order_items_dataset.csv`
    * `olist_order_payments_dataset.csv`
    * `olist_order_reviews_dataset.csv`
    * `olist_products_dataset.csv`
    * `olist_sellers_dataset.csv`
    * `product_category_name_translation.csv`
* FAQ will be loaded automatically from HuggingFace on first run.

---

### 3. Set Up API Keys

Create a `.env` file in your project root with your OpenAI key:

```
OPENAI_API_KEY=sk-xxxxxx
```

---

### 4. Run the Agent (CLI)

```bash
python main.py
```
The first execution automatically builds `olist.db` and the FAQ vector store by
running the setup modules.

Example conversation:

```
You: What is your refund policy?
AI: [semantic FAQ answer]

You: Check order status for ID 000229ec398224ef6ca0657da4fc703e
AI: Order 000229ec398224ef6ca0657da4fc703e status: delivered
```

## Sample Questions

Try these example prompts to explore the agent's capabilities:

1. **General FAQ** – "What is your refund policy?" or "How do I return an item?"
2. **Order Status** – "Where is my order `<order_id>`?"
3. **Order Details** – "Give me all details for order `<order_id>` (items, customer city, payments, review)."
4. **Refund/Payment** – "Has order `<order_id>` been refunded?"
5. **Order Review** – "What review did I leave for order `<order_id>`?"
6. **Item Breakdown** – "Which products were in order `<order_id>` and what categories are they in?"
7. **Seller Info** – "Who were the sellers for the items in order `<order_id>`?"
8. **Payment Method** – "How much was paid for order `<order_id>` and what payment method was used?"
9. **Customer Location** – "Which city/state is the customer from for order `<order_id>`?"
10. **Additional FAQs** – "How long does shipping usually take?" or "What is your return policy for defective items?"

---

## How it Works

* **Startup:**

  * Creates and populates SQLite DB from CSVs (ORM: all relationships preserved)
  * Builds FAQ vector DB (Chroma + HuggingFace sentence transformers)
* **Agent Loop:**

  * Classifies intent via LLM
  * Routes query to the correct tool (order lookup, refund, review, FAQ search)
  * Logs every interaction for analytics/continual improvement

---

## Configuration

Edit `config.py` to set:

* Model names (vector embeddings)
* DB and vectorstore paths
* HuggingFace or OpenAI model config

---

## Extending

* Add new tools to `tools/business_tools.py`
* Add new intent types to the agent workflow
* Swap out the LLM in `llm/llm.py` for Claude, Gemini, etc.
* Plug into a web API (Flask, FastAPI) with a few lines

---

## Troubleshooting

* Make sure all CSVs are in `data/` and `.env` contains your API key.
* For vectorstore/embedding errors: check internet access for model download on first run.
* If you change DB schema or CSVs, delete `olist.db` and rerun `main.py`.

---

## License

MIT License (or your preferred license)

---

## Credits

* Olist dataset (public domain)
* [LangChain](https://github.com/langchain-ai/langchain), [ChromaDB](https://github.com/chroma-core/chroma)
* HuggingFace Datasets, OpenAI GPT

---

**Questions?**
File an issue or email your maintainer.
