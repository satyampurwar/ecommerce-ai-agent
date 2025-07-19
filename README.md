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
# Alternatively use pip:
# pip install -r requirements.txt
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

Create a `.env` file in your project root with your API keys. At minimum you
need the OpenAI key if you want to use OpenAI for intent detection:

```
OPENAI_API_KEY=sk-xxxxxx
# Optional: override the chat model (default: gpt-4o-mini)
# OPENAI_MODEL_NAME=gpt-4o-mini

# Optional: use HuggingFace instead of OpenAI for intent classification
# INTENT_CLASSIFIER=huggingface
# HUGGINGFACE_API_TOKEN=hf_xxxx
# HF_INTENT_MODEL=facebook/bart-large-mnli
# Optional: enable Langfuse observability
# LANGFUSE_PUBLIC_KEY=pk_xxxx
# LANGFUSE_SECRET_KEY=sk_xxxx
# LANGFUSE_HOST=https://app.langfuse.com
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

### 5. Launch the Web Chat (Gradio)

```bash
python gradio_app.py
```
This starts a simple web UI so you can chat with the agent in your browser.

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
* HuggingFace or OpenAI model config (OpenAI chat model: `gpt-4o-mini`, HF intent model: `facebook/bart-large-mnli`)
* `INTENT_CLASSIFIER` to choose between OpenAI or HuggingFace for intent detection

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

## Docker Quickstart

The project includes a `Dockerfile` and `docker-compose.yml` so you can run
everything inside containers. Follow these steps:

1. **Create a `.env` file** with your OpenAI (and optional HuggingFace) keys.

2. **Build the image** (only required the first time):

   ```bash
   docker compose build
   ```

   The first build copies the contents of `data/` into the image (Step 6 in the
   `Dockerfile`). Once that data lives in the volume you can comment out that
   step for subsequent builds.

3. **Create the external volumes** (only required once):

   The volumes defined in `docker-compose.yml` have `external: true`, so Docker
   will not create them automatically. Ensure they exist before running
   `docker compose up`:

   ```bash
   docker volume create ecommerce_data
   docker volume create ecommerce_database
   docker volume create ecommerce_vectorstore
   docker volume create ecommerce_logs

4. **Start the application** and open <http://localhost:7860> in your browser:

   ```bash
   docker compose up
   ```

   - **Detached mode**

     ```bash
     docker compose up -d
     ```

   - **Interactive shell**

     ```bash
     docker compose run --entrypoint bash -it app
     ```

5. **Stop or restart the containers**:

   ```bash
   docker compose stop     # stop
   docker compose restart  # restart
   ```

6. **Remove everything** when you're done:

   ```bash
   docker compose down
   ```

### Inspecting Docker Resources

- **Volumes**

  ```bash
  docker volume ls
  docker volume inspect ecommerce_data
  ```

- **Networks**

  ```bash
  docker network ls
  docker network inspect <network_name>
  ```

- **Services and containers**

  ```bash
  docker compose ps
  ```

- **Images**

  ```bash
  docker images
  ```

---

## Langfuse Observability

The project integrates [Langfuse](https://www.langfuse.com/) (tested with the Python SDK v3.2.1) for tracing,
prompt management, metrics and evals. Provide your Langfuse keys in `.env` and
the agent will record each query, LLM call and registered prompt. Custom metrics
and evaluation scores are also sent so you can monitor performance over time.
Observability is optional; if keys are missing the agent runs without tracing.

---

## License

MIT License

---

## Credits

* Olist dataset (public domain)
* [LangChain](https://github.com/langchain-ai/langchain), [ChromaDB](https://github.com/chroma-core/chroma)
* HuggingFace Datasets, OpenAI GPT

---
