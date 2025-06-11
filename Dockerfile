# Use official Python image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy project files
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose FastAPI port
EXPOSE 8000

# Run FastAPI app
CMD ["uvicorn", "aflac_api_server_SECURE:app", "--host", "0.0.0.0", "--port", "8000"]
