#!/bin/bash
# 🚀 Frontend Dashboard Startup Script
# Quick setup and launch for the Streamlit dashboard

echo "📊 Data Warehouse Dashboard Launcher"
echo "===================================="
echo ""

# Check if Python is available
if ! command -v python &> /dev/null; then
    echo "❌ Python not found. Please install Python 3.8+"
    exit 1
fi

# Activate virtual environment if present
if [ -f ".venv/bin/activate" ]; then
    echo "🔧 Activating virtual environment..."
    source .venv/bin/activate
elif [ -f ".venv/Scripts/activate" ]; then
    echo "🔧 Activating virtual environment (Windows)..."
    source .venv/Scripts/activate
fi

# Check if dependencies are installed
echo "📦 Checking dependencies..."
python -c "import streamlit; import plotly; import pandas; import mysql.connector" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "⚠️  Installing missing dependencies..."
    pip install -q -r frontend/requirements.txt --break-system-packages || pip install -q -r frontend/requirements.txt
fi

# Validate database connection
echo "🔗 Validating database connection..."
python -c "
from pathlib import Path
import sys
sys.path.insert(0, 'frontend')
from data.repository import QueryRepository
repo = QueryRepository()
conn = repo._get_connection()
if conn:
    print('✅ Database connection OK')
    repo.close_connection()
else:
    print('❌ Database connection failed')
    sys.exit(1)
"

if [ $? -ne 0 ]; then
    echo "⚠️  Database connection failed. Ensure Docker container is running:"
    echo "   docker compose up -d"
    exit 1
fi

echo ""
echo "✅ All checks passed!"
echo ""
echo "🚀 Launching Streamlit dashboard..."
echo "   Open your browser to: http://localhost:8501"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Launch Streamlit
streamlit run frontend/main.py
