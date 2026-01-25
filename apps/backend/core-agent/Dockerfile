FROM python:3.11-slim

WORKDIR /app

# Copy shared package
COPY packages/shared-python /packages/shared-python

COPY apps/backend/core-agent/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY apps/backend/core-agent/app/ ./app/
COPY alembic.ini .
COPY migrations/ ./migrations/

EXPOSE 8001

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]
