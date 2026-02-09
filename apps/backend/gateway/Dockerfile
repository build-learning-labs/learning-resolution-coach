FROM python:3.11-slim

WORKDIR /app

# 1. Copy the shared package to a fixed location
COPY packages/shared-python /packages/shared-python

# 2. Copy requirements
COPY apps/backend/gateway/requirements.txt .

# 3. FIX: Remove the broken relative path line & install shared package manually
RUN sed -i '/shared-python/d' requirements.txt && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir /packages/shared-python

# 4. Copy the rest of the app
COPY apps/backend/gateway/app/ ./app/
COPY migrations/ ./migrations/
COPY alembic.ini .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]