#!/bin/bash
# Start all backend services in the background

echo "Starting Gateway..."
cd apps/backend/gateway && uvicorn app.main:app --port 8000 --reload &
GATEWAY_PID=$!
echo "Gateway running on PID $GATEWAY_PID"

echo "Starting Core Agent..."
cd ../../../apps/backend/core-agent && uvicorn app.main:app --port 8001 --reload &
CORE_PID=$!
echo "Core Agent running on PID $CORE_PID"

echo "Starting RAG Worker..."
cd ../rag-worker && uvicorn app.main:app --port 8002 --reload &
RAG_PID=$!
echo "RAG Worker running on PID $RAG_PID"

echo "Services started! Logs will appear below."
wait
