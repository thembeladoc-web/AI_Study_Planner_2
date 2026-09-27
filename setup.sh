#!/bin/bash
set -e

echo "=========================================="
echo "Timetable Planner - Setup Script"
echo "=========================================="
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python 3 is not installed"
    exit 1
fi

# Check Node.js
if ! command -v node &> /dev/null; then
    echo "[ERROR] Node.js is not installed"
    exit 1
fi

echo "[1/6] Creating Python virtual environment..."
cd backend
python3 -m venv .venv

echo "[2/6] Activating virtual environment..."
source .venv/bin/activate

echo "[3/6] Installing Python dependencies..."
pip install -r requirements.txt

echo "[4/6] Running database migrations..."
python manage.py migrate

echo "[5/6] Installing frontend dependencies..."
cd ../frontend
npm install

echo "[6/6] Setup complete!"
echo ""
echo "To start the application:"
echo "  1. Start backend: cd backend && source .venv/bin/activate && python manage.py runserver"
echo "  2. Start frontend: cd frontend && npm start"
echo ""
