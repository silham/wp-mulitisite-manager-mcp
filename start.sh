#!/bin/bash
# Quick start script for WordPress MCP Server

echo "🚀 Starting WordPress MCP Server (HTTP/SSE mode)"
echo "================================================"

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found!"
    echo "Creating from .env.example..."
    if [ -f .env.example ]; then
        cp .env.example .env
        echo "✅ Created .env file. Please edit it with your WordPress credentials."
        echo "   Run this script again after configuring .env"
        exit 1
    else
        echo "❌ .env.example not found. Please create .env manually."
        exit 1
    fi
fi

# Check if virtual environment exists
if [ ! -d .venv ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source .venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -q --upgrade pip
pip install -q -e .

# Run the server
echo ""
echo "✅ Starting server..."
echo "   SSE endpoint: http://localhost:8000/sse"
echo "   Health check: http://localhost:8000/health"
echo "   Press Ctrl+C to stop"
echo ""

python server_http.py
