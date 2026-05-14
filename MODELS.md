# MOE QA System - Model Setup Guide

This guide provides detailed instructions for pulling and configuring Ollama models locally.

## Prerequisites

- Docker and Docker Compose installed
- At least 32GB RAM (64GB+ recommended for 34b models)
- NVIDIA GPU recommended (CUDA 11.8+) for performance

## Model Pulling Strategy

### Minimum Setup (8GB RAM)

```bash
# Quick start with smaller models
ollama pull mistral:7b
```

### Recommended Setup (32GB+ RAM)

```bash
# Security: Best vulnerability detection
ollama pull codellama:34b

# Code Quality: Best refactoring suggestions  
ollama pull deepseek-coder:33b

# Testing: Best test generation
ollama pull wizardcoder:34b

# Documentation: Lightweight docs expert
ollama pull mistral:7b
```

### Full Setup (with GPU)

Pull all models + orchestrator model:

```bash
ollama pull codellama:34b
ollama pull deepseek-coder:33b
ollama pull wizardcoder:34b
ollama pull mistral:7b
ollama pull mixtral:8x7b  # Optional: better orchestration
```

## Starting Ollama

### Via Docker Compose

```bash
docker-compose up -d

# Verify running
docker-compose logs ollama
```

### Via Local Ollama Installation

```bash
# Install from https://ollama.ai
ollama serve

# In another terminal, pull models
ollama pull codellama:34b
```

## Verifying Models

```bash
# List installed models
ollama list

# Test a model
ollama run codellama:34b "def hello(): return 'world'"

# Check server health
curl http://localhost:11434/api/tags
```

## Storage Requirements

| Model | Size | Disk Space |
|-------|------|-----------|
| mistral:7b | 4.1GB | 5GB |
| codellama:34b | 19GB | 20GB |
| deepseek-coder:33b | 19GB | 20GB |
| wizardcoder:34b | 20GB | 22GB |
| **Total** | **~62GB** | **~67GB** |

## Performance Tuning

### GPU Acceleration (Recommended)

```bash
# NVIDIA GPU (CUDA 11.8+)
# Docker compose will auto-detect

# Verify GPU is used
docker-compose exec ollama nvidia-smi
```

### CPU-Only Mode

Edit `docker-compose.yml`, remove the `deploy` section to use CPU only.

### Memory Limits

For systems with limited RAM:

1. Use smaller models:
   ```bash
   ollama pull codellama:7b
   ollama pull mistral:7b
   ```

2. Adjust context window in `.env`:
   ```env
   MOE_MAX_TOKENS=2048
   ```

3. Process files sequentially (not in parallel)

## Model Selection Rationale

### Security Expert: CodeLlama 34B
- Specialized in security patterns
- Excellent vulnerability detection
- Understands OWASP principles
- Large context window for detailed analysis

### Quality Expert: DeepSeek-Coder 33B
- Trained on diverse codebases
- Strong refactoring suggestions
- Understands design patterns
- Balanced speed/quality trade-off

### Test Expert: WizardCoder 34B
- Exceptional test generation
- Understands edge cases
- Property-based testing awareness
- Best for coverage analysis

### Docs Expert: Mistral 7B
- Fast and efficient
- Clear documentation writing
- Good for comments and docstrings
- Lightweight for resource efficiency

## Upgrading Models

Monitor model performance and upgrade as needed:

```bash
# Check for model updates
ollama pull codellama:34b  # Re-pulls if newer version available

# Remove old models
ollama rm codellama:34b-old

# List all versions
ollama list
```

## Monitoring & Logging

```bash
# View Ollama logs
docker-compose logs -f ollama

# Monitor resource usage
docker stats ollama_server

# Check model loading times
time ollama run codellama:34b "print('loaded')"
```

## Troubleshooting

### Model Too Large Error
```bash
# Increase Docker memory allocation
docker-compose down
# Edit docker-compose.yml to increase memory limits
docker-compose up -d
```

### Slow Inference
1. Enable GPU acceleration (see GPU Acceleration section)
2. Use smaller models (7b instead of 34b)
3. Increase `MOE_TEMPERATURE` slightly for faster generation

### Model Loading Failures
```bash
# Clear model cache and re-pull
docker-compose exec ollama ollama rm codellama:34b
docker-compose exec ollama ollama pull codellama:34b
```

## References

- [Ollama Model Library](https://ollama.ai/library)
- [Available Models List](https://github.com/ollama/ollama#model-library)
- [Model Parameters Guide](https://github.com/ollama/ollama/blob/main/docs/modelfile.md)

---

Last Updated: 2024-05
