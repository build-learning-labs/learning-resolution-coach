FROM python:3.11-slim

WORKDIR /app

# 1. Copy shared package
COPY packages/shared-python /packages/shared-python

# 2. Copy requirements
COPY apps/backend/rag-worker/requirements.txt .

# 3. FIX: Remove broken line & install manually
RUN sed -i '/shared-python/d' requirements.txt && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir /packages/shared-python

# 4. Copy app code
COPY apps/backend/rag-worker/app/ ./app/

EXPOSE 8002

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8002"]