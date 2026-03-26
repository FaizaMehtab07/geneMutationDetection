#!/bin/bash
# Quick Start Script - Starts both backend and frontend

echo "Starting Gene Mutation Detection System..."
echo ""

# Start backend in background
echo "Starting backend server..."
cd backend
source venv/bin/activate 2>/dev/null || python3 -m venv venv && source venv/bin/activate
pip install -q -r requirements.txt
uvicorn server:app --host 0.0.0.0 --port 8001 --reload &
BACKEND_PID=$!
echo "✓ Backend starting (PID: $BACKEND_PID)..."

# Wait for backend to be ready
sleep 3

# Start frontend in new terminal would require terminal emulator
# Instead, provide instructions
echo ""
echo "========================================="
echo "Backend is running at http://localhost:8001"
echo ""
echo "To start frontend, open a NEW terminal and run:"
echo "  cd frontend"
echo "  yarn start"
echo ""
echo "Then visit: http://localhost:3000"
echo "========================================="
echo ""
echo "Press Ctrl+C to stop backend"

# Keep script running
wait $BACKEND_PID
