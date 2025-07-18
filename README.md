# Ecommerce LLM Agent

**Conversational AI for E-commerce Support**

* ✅ Order status and review lookup (by order ID)
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
git clone <your-repo-url> ecommerce_agent
cd ecommerce_agent
conda env create -f environment.yml
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

You: Check order status for ID 9f3c8ad34e86c41a0ef3e743c94e5a48
AI: Order 9f3c8ad34e86c41a0ef3e743c94e5a48 status: delivered
```

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
