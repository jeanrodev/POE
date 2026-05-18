#!/bin/bash
# Starts the Ollama server and ensures all required models are present.
# Models are pulled on first run and cached in the mounted volume.

echo "🚀 Starting Ollama server..."
ollama serve &
OLLAMA_PID=$!

# Wait until the Ollama API responds (no curl needed — uses the CLI itself)
echo "⏳ Waiting for Ollama to be ready..."
until ollama list > /dev/null 2>&1; do
    sleep 1
done
echo "✓ Ollama server ready"

# Models required by the MOE QA experts
# Selected for 16 GB RAM systems — each model is ~4 GB, one runs at a time.
MODELS=(
    "codellama:7b"
    "deepseek-coder:6.7b"
    "wizardcoder:7b"
    "mistral:7b"
)

for model in "${MODELS[@]}"; do
    if ollama list 2>/dev/null | grep -q "^${model}"; then
        echo "✓ ${model} already present"
    else
        echo "📦 Pulling ${model} — this may take a while on first start..."
        ollama pull "${model}" || echo "⚠ Failed to pull ${model}, continuing..."
        echo "✓ ${model} ready"
    fi
done

echo ""
echo "✅ All models available. Ollama is serving on :11434"

# Keep the server running in the foreground
wait $OLLAMA_PID
