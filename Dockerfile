# Dockerfile for the Ecommerce LLM Agent
# --------------------------------------
# This file defines how to build a Docker image that
# contains all dependencies and code needed to run the
# project. Comments explain each step for clarity.

# 1. Use a small Python 3.10 image as the base.
FROM python:3.10-slim

# 2. Set the working directory inside the container.
# All following commands will run inside /app.
WORKDIR /app

# 3. Copy the Conda environment file so we know the
# required Python packages. We use pip here for
# simplicity when building the image.
COPY deploy/conda/env.yml /tmp/env.yml

# 4. Install Python dependencies with pip. The packages
# mirror those listed in deploy/conda/env.yml.
RUN pip install --no-cache-dir \
    pandas>=2.2.2 \
    sqlalchemy>=2.0.25 \
    tqdm>=4.66.4 \
    langchain>=0.1.17 \
    langgraph>=0.0.45 \
    langchain-chroma>=0.0.8 \
    chromadb>=0.5.0 \
    langchain-huggingface>=0.0.9 \
    datasets>=2.19.1 \
    openai>=1.25.0 \
    python-dotenv>=1.0.1 \
    typing-extensions>=4.11.0 \
    sentence-transformers>=0.6.0 \
    gradio>=4.24.0

# 5. Copy the rest of the application code into the image.
COPY . /app

# 6. Create directories that will be mapped to Docker
# volumes for persistent storage of the SQLite database
# and the FAQ vector store.
RUN mkdir -p /db /vectorstore

# 7. Set environment variables so the app writes the
# database and vector store to the mounted volumes.
ENV DATABASE_FILE=/db/olist.db
ENV VECTOR_DB_DIR=/vectorstore

# 8. Expose the port used by the Gradio UI so it is
# reachable from the host machine.
EXPOSE 7860

# 9. When the container starts, launch the Gradio web app.
CMD ["python", "gradio_app.py"]
