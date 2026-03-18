FROM python:3.11-slim

# Install system dependencies required for geospatial libraries
RUN apt-get update && apt-get install -y \
    libgdal-dev \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY backend/ ./backend/
COPY frontend/ ./frontend/
COPY scripts/ ./scripts/

# Set Python path so it can find the backend module
ENV PYTHONPATH=/app

# Expose the API port
EXPOSE 8000

# Start the application
CMD ["python", "backend/main.py"]
