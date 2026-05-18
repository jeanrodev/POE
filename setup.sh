#!/bin/bash
# MOE QA System Setup Script for Linux/macOS
# Ollama and all LLM models run entirely inside Docker — no local install needed.

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
echo "Checking Docker..."
if ! command -v docker &> /dev/null; then
    echo "❌ Docker not found. Install from https://docs.docker.com/get-docker/"
    exit 1
fi
echo "✓ Docker found"

# Check Docker Compose (v2 plugin or standalone)
if docker compose version &> /dev/null 2>&1; then
    COMPOSE_CMD="docker compose"
elif command -v docker-compose &> /dev/null; then
    COMPOSE_CMD="docker-compose"
else
    echo "❌ Docker Compose not found. Install from https://docs.docker.com/compose/install/"
    exit 1
fi
echo "✓ Docker Compose found ($COMPOSE_CMD)"

# Build the custom Ollama image
echo ""
echo "Building the Ollama image (includes model auto-pull on first start)..."
$COMPOSE_CMD build ollama
echo "✓ Image built"

# Final instructions
echo ""
echo "✅ Setup Complete!"
echo ""
echo "Next steps:"
echo "1. Start the stack:  $COMPOSE_CMD up -d"
echo "   ↳ On first start, models are automatically downloaded inside the container."
echo "   ↳ This may take 30–60 minutes depending on your connection."
echo ""
echo "2. Monitor model download:"
echo "   docker logs -f ollama_server"
echo ""
echo "3. Open the chat UI: http://localhost:3000"
echo ""
echo "4. Run code analysis: python moe_qa/main.py src/ --format html"
echo "   (Ollama must be reachable at http://localhost:11434)"
echo ""
