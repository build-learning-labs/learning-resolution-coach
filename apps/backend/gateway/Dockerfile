FROM python:3.11-slim

WORKDIR /app

# Copy shared package first
COPY packages/shared-python /packages/shared-python

# Install dependencies
COPY apps/backend/gateway/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY apps/backend/gateway/app/ ./app/

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
