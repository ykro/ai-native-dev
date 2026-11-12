FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . backend/

# Expose port
EXPOSE 8080

# Command to run the application
# Using port 8080 for Cloud Run compatibility
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8080"]
