#!/bin/bash

echo "========================================"
echo " Face Attendance System - Admin Setup"
echo "========================================"
echo

echo "[1/4] Checking Python and environment..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 not found! Please install Python 3.8+"
    exit 1
fi

echo "✅ Python is ready"

echo
echo "[2/4] Installing Backend dependencies..."
cd "$(dirname "$0")/../backend"

if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

echo "🔧 Activating virtual environment..."
source venv/bin/activate

echo "📦 Installing packages..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "❌ Failed to install dependencies!"
    exit 1
fi

echo "✅ Backend dependencies installed"

echo
echo "[3/4] Setting up database..."
echo "🗄️ Running database migrations..."
alembic upgrade head
if [ $? -ne 0 ]; then
    echo "⚠️ Database migration failed - database might not be set up yet"
    echo "ℹ️ You can run this again after configuring database"
fi

echo
echo "[4/4] Starting system..."
echo "🚀 Starting Face Attendance System..."
echo
echo "========================================"
echo " 🌐 Admin Dashboard: http://localhost:8000/admin"
echo " 📚 API Documentation: http://localhost:8000/docs"
echo " 🔧 API Base URL: http://localhost:8000/api/v1"
echo "========================================"
echo
echo "Press Ctrl+C to stop server"
echo

# Try to open browser (works on most systems)
if command -v xdg-open &> /dev/null; then
    xdg-open http://localhost:8000/admin &
elif command -v open &> /dev/null; then
    open http://localhost:8000/admin &
fi

python start_server.py
