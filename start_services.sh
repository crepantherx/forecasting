#!/bin/bash

# Kill any existing processes on ports 8000-8003, 8080
lsof -ti:8000,8001,8002,8003,8080 | xargs kill -9 2>/dev/null

echo "Starting Classical Service on port 8001..."
cd classical-service && uvicorn main:app --host 0.0.0.0 --port 8001 &
PID_CLASSICAL=$!

echo "Starting ML Service on port 8002..."
cd ml-service && uvicorn main:app --host 0.0.0.0 --port 8002 &
PID_ML=$!

echo "Starting DL Service on port 8003..."
cd dl-service && uvicorn main:app --host 0.0.0.0 --port 8003 &
PID_DL=$!

echo "Starting Gateway on port 8000..."
cd gateway && uvicorn main:app --host 0.0.0.0 --port 8000 &
PID_GATEWAY=$!

echo "Starting Frontend on port 8080..."
cd frontend-service && uvicorn main:app --host 0.0.0.0 --port 8080 &
PID_FRONTEND=$!

echo "All services started!"
echo "Gateway: http://localhost:8000"
echo "Frontend: http://localhost:8080"
echo "Press CTRL+C to stop all services."

wait
