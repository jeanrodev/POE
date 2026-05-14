# MOE (Mixture of Experts) Quality Assurance System

A GDPR-compliant, local-first QA framework using Ollama LLMs for pre-release software quality assurance.

## 🎯 Overview

MOE QA provides a modular expert system for comprehensive code analysis:

- **Security Expert**: Vulnerability detection (OWASP Top 10, secrets, CVEs)
- **Code Quality Expert**: Refactoring suggestions, design patterns, best practices
- **Test Coverage Expert**: Test generation, gap analysis, edge case identification
- **Documentation Expert**: Docstring completeness, API clarity, examples

All analysis runs **locally** on your machine using Ollama. No code leaves your environment.

## ⚡ Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Start Ollama Infrastructure

```bash
# Option A: Docker Compose (recommended)
docker-compose up -d

# Option B: Local Ollama (https://ollama.ai)
ollama serve
```

### 3. Pull Required Models

```bash
# In another terminal
ollama pull codellama:34b
ollama pull deepseek-coder:33b
ollama pull wizardcoder:34b
ollama pull mistral:7b
```

### 4. Run Analysis

```bash
# Analyze single file
python moe_qa/main.py src/auth.py --format html

# Analyze directory
python moe_qa/main.py src/ --format json --output-dir ./reports

# With additional context
python moe_qa/main.py src/api.py --context "FastAPI v0.100.0"
```

## 📂 Project Structure

```
moe_qa/
├── __init__.py
├── config/
│   ├── __init__.py
│   └── settings.py              # Configuration management
├── experts/
│   ├── __init__.py
│   ├── base_expert.py           # Abstract base class
│   ├── security_expert.py       # Vulnerability detection
│   ├── quality_expert.py        # Code quality analysis
│   ├── test_expert.py           # Test coverage gaps
│   └── docs_expert.py           # Documentation review
├── orchestrator/
│   ├── __init__.py
│   └── router.py                # MOE orchestration logic
├── reports/
│   ├── __init__.py
│   └── generator.py             # HTML/JSON report generation
└── main.py                      # CLI entry point
```

## 🔧 Configuration

Edit `.env` to customize:

```env
MOE_OLLAMA_HOST=http://localhost:11434
MOE_MAX_TOKENS=4096
MOE_TEMPERATURE=0.1
MOE_REPORT_OUTPUT_DIR=./qa_reports
```

## 📊 Report Output

MOE generates two report types:

### HTML Report
Interactive, browser-viewable report with color-coded severity levels.

### JSON Report
Machine-readable format for CI/CD integration and automation.

## 🔒 Security & Privacy

- **Zero Network Calls**: All LLM inference runs locally via Ollama
- **No Cloud Storage**: Reports stay on your machine
- **No Telemetry**: No usage data collected
- **GDPR Compliant**: Full data sovereignty

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
     │       │        │        │
     └───────┴────┬───┴────────┘
             ┌────▼─────────┐
             │Local Ollama   │
             │LLM Models     │
             └───────────────┘
```

## 📚 Expert Roles & Models

| Expert | Primary Model | Task |
|--------|---------------|------|
| Security | CodeLlama:34b | Vulnerability detection, OWASP analysis |
| Quality | DeepSeek-Coder:33b | Refactoring, patterns, complexity |
| Tests | WizardCoder:34b | Test generation, gap analysis |
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

### Ollama Connection Error
```bash
# Verify Ollama is running
curl http://localhost:11434/api/tags

# If docker: check container logs
docker-compose logs ollama
```

### Model Not Found
```bash
# List available models
ollama list

# Pull missing model
ollama pull codellama:34b
```

### High Memory Usage
- Use smaller models: `codellama:7b` instead of `34b`
- Adjust `MOE_MAX_TOKENS` in `.env`
- Run on GPU-enabled hardware

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
