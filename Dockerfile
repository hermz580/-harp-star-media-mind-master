FROM python:3.11-slim

WORKDIR /app

# Install system dependencies if any
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY brand-engine/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY brand-engine/ .

# Expose Streamlit port
EXPOSE 8501

# Run the app
CMD ["streamlit", "run", "ui/app.py", "--server.port=8501", "--server.address=0.0.0.0"]
