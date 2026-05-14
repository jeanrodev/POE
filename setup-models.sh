#!/bin/bash
# Model Setup Script - Pull all required Ollama models

set -e

echo "📦 Downloading MOE QA Models"
echo "============================="
echo ""

# Check if Ollama is available
if ! command -v ollama &> /dev/null; then
    echo "❌ Ollama not found. Please install from https://ollama.ai"
    exit 1
fi

# Check if Ollama server is running
echo "Checking Ollama server..."
if ! curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "⚠️  Ollama server not running at localhost:11434"
    echo "Start it with: ollama serve"
    exit 1
fi
echo "✓ Ollama server running"

echo ""
echo "This process may take 30-60 minutes depending on your internet speed."
echo "Models will be stored locally (no cloud upload)."
echo ""

MODELS=(
    "codellama:34b"
    "deepseek-coder:33b"
    "wizardcoder:34b"
    "mistral:7b"
)

TOTAL=${#MODELS[@]}
CURRENT=0

for model in "${MODELS[@]}"; do
    CURRENT=$((CURRENT + 1))
    echo ""
    echo "[$CURRENT/$TOTAL] Pulling $model..."
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    if ollama pull "$model"; then
        echo "✓ $model installed successfully"
    else
        echo "❌ Failed to pull $model"
        exit 1
    fi
done

echo ""
echo "✅ All models installed!"
echo ""
echo "Verify installation:"
echo "  ollama list"
echo ""
echo "Test a model:"
echo "  ollama run codellama:34b 'def hello(): return \"world\"'"
echo ""
