FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libchromaprint1 \
    libchromaprint-dev \
    gcc \
    git \
    libmagic1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements and setup files
COPY requirements.txt setup.py ./

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install -e .

# Copy application code
COPY . .

# Create uploads directory
RUN mkdir -p uploads

# Set environment variables
ENV FLASK_APP=app
ENV FLASK_ENV=development
ENV PYTHONPATH=/app

# Command to run tests
CMD ["pytest", "-v", "tests/"]
