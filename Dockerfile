FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code from the brand-engine directory
COPY . .

# Expose FastAPI port
EXPOSE 8000

# Environment defaults
ENV PYTHONUNBUFFERED=1
ENV PORT=8000

# Run the app
CMD ["python", "main.py"]
