#!/bin/bash
# Starts the Ollama server and ensures all required models are present.
# Models are pulled on first run and cached in the mounted volume.

set -e

echo "🚀 Starting Ollama server..."
/bin/ollama serve &
OLLAMA_PID=$!

# Wait until the Ollama API responds
echo "⏳ Waiting for Ollama to be ready..."
until curl -sf http://localhost:11434/api/tags > /dev/null 2>&1; do
    sleep 1
done
echo "✓ Ollama server ready"

# Models required by the MOE QA experts
MODELS=(
    "codellama:34b"
    "deepseek-coder:33b"
    "wizardcoder:34b"
    "mistral:7b"
)

for model in "${MODELS[@]}"; do
    model_name="${model%%:*}"
    if ollama list 2>/dev/null | grep -q "^${model_name}"; then
        echo "✓ ${model} already present"
    else
        echo "📦 Pulling ${model} — this may take a while on first start..."
        ollama pull "${model}"
        echo "✓ ${model} ready"
    fi
done

echo ""
echo "✅ All models available. Ollama is serving on :11434"

# Keep the server running in the foreground
wait $OLLAMA_PID
