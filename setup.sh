#!/bin/bash
# MOE QA System Setup Script for Linux/macOS

set -e

echo "🚀 MOE QA System Setup"
echo "====================="

# Check Python version
echo "Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.8+"
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo "✓ Python $PYTHON_VERSION found"

# Create virtual environment
echo ""
echo "Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate
echo "✓ Virtual environment activated"

# Install dependencies
echo ""
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
echo "✓ Dependencies installed"

# Create necessary directories
echo ""
echo "Creating directories..."
mkdir -p qa_reports
mkdir -p logs
echo "✓ Directories created"

# Check Docker
echo ""
echo "Checking Docker/Docker Compose..."
if command -v docker-compose &> /dev/null; then
    echo "✓ Docker Compose found"
    echo ""
    echo "To start Ollama infrastructure, run:"
    echo "  docker-compose up -d"
else
    echo "⚠ Docker Compose not found. Install from https://docs.docker.com/compose/install/"
fi

# Final instructions
echo ""
echo "✅ Setup Complete!"
echo ""
echo "Next steps:"
echo "1. Start Ollama: docker-compose up -d"
echo "2. Pull models: bash setup-models.sh"
echo "3. Run analysis: python moe_qa/main.py src/ --format html"
echo ""
