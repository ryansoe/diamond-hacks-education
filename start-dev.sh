#!/bin/bash

# Function to handle cleanup when script is interrupted
function cleanup {
  echo "Shutting down services..."
  kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
  exit
}

# Set up trap to call cleanup function when script is interrupted
trap cleanup SIGINT SIGTERM

echo "=== Starting Eventory Development Environment ==="
echo "Starting backend server..."

# Start the FastAPI backend
cd backend
python main.py &
BACKEND_PID=$!
cd ..

echo "Backend started with PID: $BACKEND_PID"
echo "Starting frontend development server..."

# Start the React frontend
cd frontend
npm start &
FRONTEND_PID=$!
cd ..

echo "Frontend started with PID: $FRONTEND_PID"
echo "=== Eventory is now running ==="
echo "Backend API: http://localhost:8000"
echo "Frontend: http://localhost:3000"
echo "Press Ctrl+C to shut down all services"

# Wait for both processes to finish
wait $BACKEND_PID $FRONTEND_PID 