FROM python:3.11-slim

LABEL maintainer="Bartosz Gaca <gaca.bartosz@gmail.com>"
LABEL description="RAG Guardian - Production-grade quality assurance for RAG systems"

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Poetry
RUN pip install --no-cache-dir poetry==1.7.1

# Copy dependency files
COPY pyproject.toml poetry.lock ./

# Install dependencies
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --no-dev

# Copy application
COPY rag_guardian/ ./rag_guardian/
COPY README.md ./

# Set up user (security best practice)
RUN useradd -m -u 1000 user && chown -R user:user /app
USER user

# Entry point
ENTRYPOINT ["python", "-m", "rag_guardian"]
CMD ["--help"]
