FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libchromaprint1 \
    libchromaprint-dev \
    gcc \
    git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install audfprint from source
RUN git clone https://github.com/dpwe/audfprint.git /tmp/audfprint \
    && cd /tmp/audfprint \
    && python -c "import shutil; shutil.copy('audfprint.py', '/usr/local/bin/audfprint'); shutil.copy('audfprint_analyze.py', '/usr/local/lib/python3.11/site-packages/audfprint_analyze.py'); shutil.copy('audfprint_match.py', '/usr/local/lib/python3.11/site-packages/audfprint_match.py')" \
    && chmod +x /usr/local/bin/audfprint \
    && cd / \
    && rm -rf /tmp/audfprint

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Create uploads directory
RUN mkdir -p uploads

# Set environment variables
ENV FLASK_APP=app
ENV FLASK_ENV=production
ENV PYTHONUNBUFFERED=1

# Expose port
EXPOSE 5000

# Run gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "wsgi:app"]
