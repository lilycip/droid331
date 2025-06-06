FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Create necessary directories
RUN mkdir -p data/memory data/generated data/meme_templates logs

# Set environment variables
ENV PYTHONPATH=/app
ENV DROID_CONFIG=/app/config/config.yaml
ENV PORT=12000

# Expose the port
EXPOSE 12000

# Run the web interface by default, but allow overriding with CMD
ENTRYPOINT ["python"]
CMD ["run_web.py"]