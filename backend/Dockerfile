# ---- Stage 1: Builder ----
FROM python:3.11.9-slim AS builder

WORKDIR /app

# Install build dependencies needed by some packages (chromadb, sentence-transformers)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies first (better layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# ---- Stage 2: Runtime ----
FROM python:3.11.9-slim

WORKDIR /app

# Install minimal runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy installed Python packages from builder
COPY --from=builder /install /usr/local

# Copy application source code
COPY main.py chat.py retriever.py prompts.py ingest.py transcribe.py ./

# Copy pre-built knowledge base and ChromaDB data
COPY knowledge/ ./knowledge/
COPY chroma_db/ ./chroma_db/

# Expose the port uvicorn will listen on
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the FastAPI app with uvicorn
# Use 0.0.0.0 to bind to all interfaces inside the container
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
