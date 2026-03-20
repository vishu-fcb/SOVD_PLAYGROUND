FROM python:3.13-slim

WORKDIR /app

# Copy requirements file
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the main application file
COPY sovd-token-service.py .

# Copy the UI directory
COPY ui/ ./ui/

# Create keys directory for mounted keys
RUN mkdir -p keys

# Expose the port the service runs on
EXPOSE 8000

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Command to run the service
CMD ["uvicorn", "sovd-token-service:app", "--host", "0.0.0.0", "--port", "8000"]
