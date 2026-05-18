# MOE QA System - Model Guide

This guide describes the models used by MOE QA and how to manage them.  
All models run inside the **`ollama_server` Docker container** — no Ollama installation is required on the host.

## Prerequisites

- Docker and Docker Compose installed
- At least 32 GB RAM (64 GB+ recommended for 34b models)
- NVIDIA GPU recommended (CUDA 11.8+) for acceptable inference speed

## How Models Are Managed

Models are downloaded automatically the **first time the container starts**:

```bash
docker compose up -d

# Monitor download progress (~70 GB total on first run)
docker logs -f ollama_server
```

Models are stored in the `ollama_data` Docker volume and persist across container restarts.  
You do **not** need to re-download them unless the volume is deleted.

## Checking Installed Models

```bash
# List models in the running container
bash setup-models.sh

# Check server health
curl http://localhost:11434/api/tags
```

## Storage Requirements

| Model | Disk Space |
|-------|-----------|
| mistral:7b | ~5 GB |
| codellama:34b | ~20 GB |
| deepseek-coder:33b | ~20 GB |
| wizardcoder:34b | ~22 GB |
| **Total** | **~67 GB** |

## Model Setup Options

### Minimum Setup (8 GB RAM)

Edit `moe_qa/config/settings.py` to use only the lightweight model, then in `ollama-entrypoint.sh` reduce `MODELS` to:

```bash
MODELS=("mistral:7b")
```

### Full Setup (32 GB+ RAM or GPU)

The default `ollama-entrypoint.sh` pulls all four models. For GPU-accelerated inference the `deploy.resources` section in `docker-compose.yml` is already configured for NVIDIA GPUs.

### CPU-Only Mode

Remove the `deploy` section from the `ollama` service in `docker-compose.yml` to run on CPU only (much slower for large models).

## Performance Tuning

### GPU Acceleration (Recommended)

```bash
# Verify the GPU is visible inside the container
docker compose exec ollama nvidia-smi
```

### Memory Limits

For systems with limited RAM, use smaller models by editing `ollama-entrypoint.sh`:

```bash
MODELS=("codellama:7b" "mistral:7b")
```

And update `moe_qa/config/settings.py` to match.

Also reduce the context window in `.env`:
```env
MOE_MAX_TOKENS=2048
```

## Force Re-pulling a Model

```bash
# Pull all models again (e.g., to get an updated version)
bash setup-models.sh pull

# Or target a single model inside the container
docker exec ollama_server ollama pull codellama:34b
```

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
- Best for coverage analysis

### Docs Expert: Mistral 7B
- Fast and efficient
- Clear documentation writing
- Lightweight for resource efficiency

## Monitoring

```bash
# View Ollama container logs
docker compose logs -f ollama

# Monitor resource usage
docker stats ollama_server
```

## Troubleshooting

### Model too large / OOM error
```bash
# Restart the stack after reducing MODELS in ollama-entrypoint.sh
docker compose down
docker compose up -d --build
```

### Slow inference
1. Enable GPU acceleration (see GPU section above)
2. Switch to smaller models (7b instead of 34b)
3. Increase `MOE_TEMPERATURE` slightly for faster generation

### Model loading failure / corrupt download
```bash
# Remove the model and re-pull
docker exec ollama_server ollama rm codellama:34b
docker exec ollama_server ollama pull codellama:34b
```

## References

- [Ollama Model Library](https://ollama.ai/library)
- [Available Models List](https://github.com/ollama/ollama#model-library)
- [Model Parameters Guide](https://github.com/ollama/ollama/blob/main/docs/modelfile.md)

---

Last Updated: 2025-05
