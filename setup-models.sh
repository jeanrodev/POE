#!/bin/bash
# Manage models inside the running Ollama container.
# Usage:
#   bash setup-models.sh          — show installed models
#   bash setup-models.sh pull     — force re-pull all required models
#   bash setup-models.sh status   — same as default

set -e

CONTAINER="ollama_server"

check_container() {
    if ! docker ps --format '{{.Names}}' | grep -q "^${CONTAINER}$"; then
        echo "❌ Container '${CONTAINER}' is not running."
        echo "   Start it with: docker compose up -d"
        exit 1
    fi
}

list_models() {
    echo "📋 Models installed in ${CONTAINER}:"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    docker exec "${CONTAINER}" ollama list
}

pull_models() {
    MODELS=(
        "codellama:34b"
        "deepseek-coder:33b"
        "wizardcoder:34b"
        "mistral:7b"
    )

    TOTAL=${#MODELS[@]}
    CURRENT=0

    echo "📦 Pulling all required models into ${CONTAINER}..."
    echo "This may take 30–60 minutes on first run."
    echo ""

    for model in "${MODELS[@]}"; do
        CURRENT=$((CURRENT + 1))
        echo "[$CURRENT/$TOTAL] $model"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        docker exec "${CONTAINER}" ollama pull "$model"
        echo "✓ $model ready"
        echo ""
    done

    echo "✅ All models ready!"
}

check_container

ACTION="${1:-status}"

case "$ACTION" in
    pull)
        pull_models
        ;;
    status|*)
        list_models
        ;;
esac
