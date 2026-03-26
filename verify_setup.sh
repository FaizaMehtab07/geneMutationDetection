#!/bin/bash
# Setup Verification Script for Gene Mutation Detection System
# Run this to check if your local environment is ready

echo "========================================="
echo "   Setup Verification"
echo "========================================="
echo ""

# Check Python
echo "[1/7] Checking Python..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
    echo "✓ Python found: $PYTHON_VERSION"
else
    echo "✗ Python 3 not found. Please install Python 3.11+"
    exit 1
fi

# Check Node
echo "[2/7] Checking Node.js..."
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    echo "✓ Node.js found: $NODE_VERSION"
else
    echo "✗ Node.js not found. Please install Node.js 18+"
    exit 1
fi

# Check Yarn
echo "[3/7] Checking Yarn..."
if command -v yarn &> /dev/null; then
    YARN_VERSION=$(yarn --version)
    echo "✓ Yarn found: $YARN_VERSION"
else
    echo "✗ Yarn not found. Please install: npm install -g yarn"
    exit 1
fi

# Check MongoDB
echo "[4/7] Checking MongoDB..."
if pgrep -x "mongod" > /dev/null; then
    echo "✓ MongoDB is running"
elif command -v mongod &> /dev/null; then
    echo "⚠ MongoDB installed but not running"
    echo "  Start it with: brew services start mongodb-community (macOS)"
    echo "  Or: sudo systemctl start mongod (Linux)"
else
    echo "✗ MongoDB not found. Please install MongoDB"
fi

# Check Backend Dependencies
echo "[5/7] Checking backend dependencies..."
if [ -f "backend/requirements.txt" ]; then
    echo "✓ requirements.txt found"
else
    echo "✗ requirements.txt missing"
fi

# Check Frontend Dependencies  
echo "[6/7] Checking frontend setup..."
if [ -f "frontend/package.json" ]; then
    echo "✓ package.json found"
else
    echo "✗ package.json missing"
fi

# Check Environment Files
echo "[7/7] Checking environment configuration..."
if [ -f "backend/.env" ]; then
    echo "✓ backend/.env found"
else
    echo "⚠ backend/.env missing - will need to create"
fi

if [ -f "frontend/.env" ]; then
    echo "✓ frontend/.env found"  
else
    echo "⚠ frontend/.env missing - will need to create"
fi

echo ""
echo "========================================="
echo "   Summary"
echo "========================================="
echo ""
echo "Next steps:"
echo "1. cd backend && python3 -m venv venv && source venv/bin/activate"
echo "2. pip install -r requirements.txt"
echo "3. uvicorn server:app --port 8001 --reload"
echo "4. In new terminal: cd frontend && yarn install && yarn start"
echo ""
echo "Visit: http://localhost:3000"
