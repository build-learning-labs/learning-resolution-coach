FROM python:3.11-slim
WORKDIR /app
# Copy shared package
COPY packages/shared-python /packages/shared-python

COPY apps/backend/notification-worker/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY apps/backend/notification-worker/app/ ./app/
EXPOSE 8004
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8004"]
