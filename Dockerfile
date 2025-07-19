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

# 3. Install Python dependencies with pip. The packages
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

# 4. Copy the rest of the application code into the image.
COPY config.py /app/
COPY main.py /app/
COPY gradio_app.py /app/
COPY db /app/db
COPY vectorstore /app/vectorstore
COPY tools /app/tools
COPY llm /app/llm
COPY agent /app/agent

# 5. Create directories that will be mapped to Docker
# volumes for persistent storage of the datat, SQLite database
# and the FAQ vector store.
RUN mkdir -p /data /database /vectorstore

# 6. Copy static data into the container for the first build.
# - This step ensures that the initial data is available inside the container.
# - The data will be persisted in the "ecommerce_data" volume as defined in docker-compose.yml.
# - Once the data is copied and mounted as a volume, you can safely remove or comment out this step
#   in subsequent builds to avoid redundant copying.
# - The container will then use the persisted data from the mounted volume.
# COPY data /data

# 7. Set environment variables so the app writes the
# database and vector store to the mounted volumes.
ENV DATA_FOLDER=/data
ENV DATABASE_FILE=/database/olist.db
ENV VECTOR_DB_DIR=/vectorstore

# 8. Expose the port used by the Gradio UI so it is
# reachable from the host machine.
EXPOSE 7860

# 8. When the container starts, launch the Gradio web app.
CMD ["python", "gradio_app.py"]