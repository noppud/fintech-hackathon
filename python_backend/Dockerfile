# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory to parent directory
WORKDIR /app

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Copy requirements first for better caching
COPY requirements.txt python_backend/

# Install dependencies
RUN pip install --no-cache-dir -r python_backend/requirements.txt

# Copy the entire python_backend directory as a package
COPY . python_backend/

# Expose the port the app runs on
EXPOSE 8000

# Command to run the application as a Python module
# Using uvicorn with host 0.0.0.0 to accept external connections
CMD ["uvicorn", "python_backend.api:app", "--host", "0.0.0.0", "--port", "8000"]
