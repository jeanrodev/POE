# MOE (Mixture of Experts) Quality Assurance System

A GDPR-compliant, local-first QA framework using Ollama LLMs for pre-release software quality assurance.

## 🎯 Overview

MOE QA provides a modular expert system for comprehensive code analysis:

- **Security Expert**: Vulnerability detection (OWASP Top 10, secrets, CVEs)
- **Code Quality Expert**: Refactoring suggestions, design patterns, best practices
- **Test Coverage Expert**: Test generation, gap analysis, edge case identification
- **Documentation Expert**: Docstring completeness, API clarity, examples

All analysis runs **entirely inside Docker containers** on your machine. No code leaves your environment, no cloud services, no external APIs.

## ⚡ Quick Start

### Prerequisites

- Python 3.8+
- [Docker](https://docs.docker.com/get-docker/) with Docker Compose

**No Ollama installation required on the host.** Models are downloaded and served inside Docker.

### 1. Run Setup

```bash
bash setup.sh          # Linux/macOS
# or
powershell -ExecutionPolicy Bypass -File setup.ps1  # Windows
```

This installs Python dependencies and builds the custom Ollama Docker image.

### 2. Start the Stack

```bash
docker compose up -d
```

On **first start**, the Ollama container automatically downloads all required models (~70 GB total). Monitor progress:

```bash
docker logs -f ollama_server
```

Models are stored in a named Docker volume and persist across restarts — download happens only once.

### 3. Open the Chat UI (optional)

Browse to **http://localhost:3000** to use [Open WebUI](https://github.com/open-webui/open-webui), a browser-based chat interface connected to the local Ollama container.

### 4. Run Code Analysis

```bash
# Activate the virtual environment first
source venv/bin/activate   # Linux/macOS
# or: .\venv\Scripts\Activate.ps1  (Windows)

# Analyze a single file
python moe_qa/main.py src/auth.py --format html

# Analyze a directory
python moe_qa/main.py src/ --format json --output-dir ./reports

# With additional context
python moe_qa/main.py src/api.py --context "FastAPI v0.100.0"
```

### 🛠️ Fix mode — apply expert improvements in place

Each expert reads a Python file, applies its lens (security, quality, docs), and writes the
improved code back to disk. A `.bak` backup is created automatically unless `--no-backup` is
passed. The `tests` expert generates a companion `tests/test_<filename>.py` instead of modifying
the source.

```bash
# Fix all experts on a single file (backup written as auth.py.bak)
python moe_qa/main.py src/auth.py --fix

# Fix a whole directory
python moe_qa/main.py src/ --fix

# Run only the security and quality experts
python moe_qa/main.py src/auth.py --fix --experts security,quality

# Fix without writing backup files
python moe_qa/main.py src/auth.py --fix --no-backup

# Fix with context hint
python moe_qa/main.py src/api.py --fix --context "FastAPI v0.100.0"
```

Available expert names for `--experts`: `security`, `quality`, `docs`, `tests`

## 📂 Project Structure

```
├── Dockerfile.ollama            # Custom Ollama image (auto-pulls models)
├── ollama-entrypoint.sh         # Container startup script
├── docker-compose.yml           # Ollama + Open WebUI services
├── setup.sh / setup.ps1         # One-time host setup (Python + Docker build)
├── setup-models.sh              # Helper: list/force-pull models in container
└── moe_qa/
    ├── __init__.py
    ├── config/
    │   ├── __init__.py
    │   └── settings.py          # Configuration management
    ├── experts/
    │   ├── __init__.py
    │   ├── base_expert.py       # Abstract base class
    │   ├── security_expert.py   # Vulnerability detection
    │   ├── quality_expert.py    # Code quality analysis
    │   ├── test_expert.py       # Test coverage gaps
    │   └── docs_expert.py       # Documentation review
    ├── orchestrator/
    │   ├── __init__.py
    │   └── router.py            # MOE orchestration logic
    ├── reports/
    │   ├── __init__.py
    │   └── generator.py         # HTML/JSON report generation
    └── main.py                  # CLI entry point
```

## 🔧 Configuration

Create a `.env` file to override defaults:

```env
MOE_OLLAMA_HOST=http://localhost:11434
MOE_MAX_TOKENS=4096
MOE_TEMPERATURE=0.1
MOE_REPORT_OUTPUT_DIR=./qa_reports
WEBUI_SECRET_KEY=change-me-in-production
```

## 📊 Report Output

MOE generates two report types:

### HTML Report
Interactive, browser-viewable report with color-coded severity levels.

### JSON Report
Machine-readable format for CI/CD integration and automation.

## 🔒 Security & Privacy

- **Zero Network Calls**: All LLM inference runs inside Docker via Ollama
- **No Cloud Storage**: Reports stay on your machine
- **No Telemetry**: No usage data collected
- **GDPR Compliant**: Full data sovereignty
- **No Host Installation**: Ollama binary is not required on the host OS

## 🏗️ Architecture

```
┌─────────────────────────────────────────┐
│         CLI (main.py)                   │
└────────────────┬────────────────────────┘
                 │
┌────────────────▼────────────────────────┐
│    MOE Orchestrator (router.py)          │
│    ├─ Parses input files/dirs           │
│    ├─ Routes to experts                  │
│    └─ Aggregates findings                │
└────┬────────┬────────┬─────────┬────────┘
     │        │        │         │
┌────▼──┐ ┌──▼────┐ ┌─▼──────┐ ┌▼───────┐
│Security│ │Quality│ │Test    │ │Docs    │
│Expert  │ │Expert │ │Expert  │ │Expert  │
└────┬──┘ └──┬────┘ └─┬──────┘ └┬───────┘
     │       │        │         │
     └───────┴────┬───┴─────────┘
             ┌────▼──────────────────┐
             │  Ollama container     │
             │  (Docker, :11434)     │
             │  Models stored in     │
             │  named Docker volume  │
             └───────────────────────┘
```

## 📚 Expert Roles & Models

| Expert | Primary Model | Task |
|--------|---------------|------|
| Security | CodeLlama:7b | Vulnerability detection, OWASP analysis |
| Quality | DeepSeek-Coder:6.7b | Refactoring, patterns, complexity |
| Tests | WizardCoder:7b | Test generation, gap analysis |
| Docs | Mistral:7b | Docstring, comments, examples |

## 🚀 Advanced Usage

### Python API

```python
from config.settings import Settings
from orchestrator.router import MOEOrchestrator
from reports.generator import ReportGenerator

# Initialize
settings = Settings()
orchestrator = MOEOrchestrator(settings=settings)
generator = ReportGenerator(output_dir="./reports")

# Analyze file
report = orchestrator.analyze_file(
    file_path="src/critical_module.py",
    context="FastAPI authentication module"
)

# Generate report
output_path = generator.generate_html_report(report)
print(f"Report: {output_path}")
```

### Batch Directory Analysis

```python
for report in orchestrator.analyze_directory(
    directory_path="src/",
    pattern="**/*.py",
    context="FastAPI v0.100.0"
):
    generator.generate_json_report(report)
```

## 🔧 Customization

### Adding Custom Experts

1. Extend `BaseExpert` class
2. Implement `_build_prompt()` and `analyze()` methods
3. Register in `MOEOrchestrator._initialize_experts()`

Example:
```python
from experts.base_expert import BaseExpert, ExpertResponse

class CustomExpert(BaseExpert):
    def __init__(self, host="http://localhost:11434"):
        super().__init__(model="your-model:size", host=host)
    
    def _build_prompt(self, code, context=None):
        return f"Analyze this code: {code}"
    
    def analyze(self, code, context=None):
        response = self._query_model(self._build_prompt(code, context))
        return ExpertResponse(
            expert_name="CustomExpert",
            findings=[response],
            severity="medium",
            raw_response=response
        )
```

## 🐛 Troubleshooting

### Check container and model status
```bash
# Container health
docker compose ps

# Model list inside the container
bash setup-models.sh

# Live container logs
docker logs -f ollama_server
```

### Ollama connection error
```bash
# Verify the API is reachable from the host
curl http://localhost:11434/api/tags
```

### Force re-download a model
```bash
bash setup-models.sh pull
```

### High memory usage
- Use smaller models: set `codellama:7b` instead of `34b` in `moe_qa/config/settings.py`
- Adjust `MOE_MAX_TOKENS` in `.env`
- Run on GPU-enabled hardware (configure the `deploy.resources` section in `docker-compose.yml`)

## 📖 References

- [Ollama Documentation](https://ollama.ai)
- [Open-WebUI](https://github.com/open-webui/open-webui)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [PEP 8 Style Guide](https://www.python.org/dev/peps/pep-0008/)

## 📄 License

See LICENSE file.

## 🤝 Contributing

Contributions welcome! Areas for enhancement:
- Additional expert roles (performance, accessibility, etc.)
- Support for other languages (JavaScript, Go, Rust, etc.)
- Parallel expert execution
- Report customization templates

---

**Trust Index: 7.5/10** — This is a rapidly evolving field. Tool versions and capabilities change frequently.
