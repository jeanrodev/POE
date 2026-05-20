#!/bin/bash
# Ollama model initialization script
# Runs inside the container on startup

echo "🚀 Initializing Ollama models..."

# Wait for Ollama to be ready
for i in {1..30}; do
    if curl -s http://localhost:11434/api/tags > /dev/null; then
        echo "✓ Ollama server is ready"
        break
    fi
    echo "Waiting for Ollama... ($i/30)"
    sleep 2
done

# Define models to pull
MODELS=(
    "codellama:34b"
    "deepseek-coder:33b"
    "wizardcoder:34b"
    "mistral:7b"
)

# Pull models
for model in "${MODELS[@]}"; do
    echo ""
    echo "Pulling $model..."
    if ollama pull "$model"; then
        echo "✓ $model downloaded successfully"
    else
        echo "❌ Failed to pull $model"
    fi
done

echo ""
echo "✅ Model initialization complete"
echo ""
ollama list
