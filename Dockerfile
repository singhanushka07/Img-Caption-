FROM python:3.11-slim

# System dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python deps before copying code (layer cache)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create runtime directories
RUN mkdir -p data/faiss_index mlruns

# Gradio port
EXPOSE 7860
# FastAPI port (optional)
EXPOSE 8000

# Default: Gradio-only (HF Spaces compatible)
CMD ["python", "app.py"]
