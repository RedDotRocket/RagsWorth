FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install uv for package management
RUN pip install uv

# Copy project files
COPY pyproject.toml .
COPY README.md .
COPY ragsworth/ ragsworth/
COPY static/ static/

# Create virtual environment and install dependencies
RUN uv venv /app/.venv \
    && . /app/.venv/bin/activate \
    && uv pip install -e .

# Download spaCy model
RUN . /app/.venv/bin/activate \
    && python -m spacy download en_core_web_sm

# Expose port
EXPOSE 8000

# Set environment variables
ENV PYTHONPATH=/app
ENV PATH=/app/.venv/bin:$PATH

# Run the application
CMD ["uvicorn", "ragsworth.api:app", "--host", "0.0.0.0", "--port", "8000"] 