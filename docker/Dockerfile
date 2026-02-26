FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
RUN pip install --no-cache-dir fastapi uvicorn requests pydantic

# Copy source code from the 'src' directory relative to the build context
COPY src/main.py .

# Expose the API port
EXPOSE 38084

# Run the application
CMD ["python", "main.py"]
