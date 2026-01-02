FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies for audio processing
RUN apt-get update && apt-get install -y \
    libsndfile1 \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for better caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create directories
RUN mkdir -p logs && mkdir -p .streamlit

# Create Streamlit config
RUN echo "[server]" > .streamlit/config.toml && \
    echo "headless = true" >> .streamlit/config.toml && \
    echo "port = 8501" >> .streamlit/config.toml && \
    echo "enableXsrfProtection = false" >> .streamlit/config.toml

# Expose ports
EXPOSE 8501 8000

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Run Streamlit app
CMD ["streamlit", "run", "streamlit_app.py"]# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/api/health')"

# Run the application
CMD ["python", "-m", "uvicorn", "src.app:app", "--host", "0.0.0.0", "--port", "8000"]
