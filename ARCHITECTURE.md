# MOE (Mixture of Experts) QA System - Architecture & Design

## System Overview

MOE QA is a modular expert system for comprehensive pre-release software quality assurance. It orchestrates multiple specialized LLM-based experts to analyze code from different perspectives:

```
Input Code
    ↓
[Orchestrator]
    ├→ [Security Expert] → Vulnerability Detection
    ├→ [Quality Expert] → Refactoring & Patterns
    ├→ [Test Expert] → Coverage & Test Gaps
    └→ [Docs Expert] → Documentation Quality
    ↓
[Report Generator]
    └→ HTML / JSON Reports
```

## Architectural Components

### 1. Configuration Layer (`config/settings.py`)

**Responsibility**: Centralized configuration management

```
Settings (Pydantic BaseModel)
├── ollama_host: URL to local Ollama server
├── max_tokens: Maximum response length
├── temperature: Model sampling temperature
└── report_output_dir: Report output location
```

**Key Design Pattern**: Singleton via environment variables
- Supports `.env` file loading
- Type-safe with Pydantic validation
- Extensible for future settings

### 2. Expert Layer (`experts/`)

**Responsibility**: Specialized analysis implementations

```
BaseExpert (Abstract)
├── _validate_model_available()
├── _query_model(prompt) → str
├── _build_prompt() [abstract]
└── analyze() [abstract]

ExpertResponse (Dataclass)
├── expert_name: str
├── findings: list[str]
├── severity: str (critical|high|medium|low)
├── raw_response: str (for traceability)
└── metadata: dict
```

#### Expert Implementations

**SecurityExpert** (`security_expert.py`)
- Model: CodeLlama 34B
- Tools: Bandit (static analysis), LLM prompting
- Focus: OWASP Top 10, CVEs, secrets detection
- Temperature: 0.05 (deterministic)

**QualityExpert** (`quality_expert.py`)
- Model: DeepSeek-Coder 33B
- Tools: Pylint, LLM prompting
- Focus: Refactoring, patterns, complexity
- Temperature: 0.2 (balanced)

**TestExpert** (`test_expert.py`)
- Model: WizardCoder 34B
- Tools: LLM prompting
- Focus: Test generation, coverage gaps, edge cases
- Temperature: 0.3 (creative)

**DocsExpert** (`docs_expert.py`)
- Model: Mistral 7B (lightweight)
- Tools: LLM prompting
- Focus: Docstrings, comments, examples
- Temperature: 0.15 (consistent)

### 3. Orchestration Layer (`orchestrator/router.py`)

**Responsibility**: Coordinate experts and aggregate findings

```
MOEOrchestrator
├── _initialize_experts() → dict[str, BaseExpert]
├── analyze_file(path, context) → MOEReport
├── analyze_directory(path, pattern, context) → Iterator[MOEReport]
└── _determine_overall_severity(responses) → str

MOEReport (Dataclass)
├── file_path: str
├── security: ExpertResponse
├── quality: ExpertResponse
├── tests: ExpertResponse
├── docs: ExpertResponse
└── overall_severity: str
```

**Severity Ranking Algorithm**:
```python
SEVERITY_RANK = {
    "critical": 4,
    "high": 3,
    "medium": 2,
    "low": 1,
    "unknown": 0
}

overall = max(expert_responses).severity
```

### 4. Reporting Layer (`reports/generator.py`)

**Responsibility**: Convert analysis results to consumable formats

```
ReportGenerator
├── generate_json_report(report) → Path
└── generate_html_report(report) → Path

Report Output
├── JSON: Machine-readable, CI/CD integration
└── HTML: Interactive, human-readable with color-coding
```

**Report Structure**:
```json
{
  "file_path": "src/auth.py",
  "timestamp": "2024-05-14T10:30:00",
  "overall_severity": "high",
  "security": {
    "findings": ["SQL Injection risk at line 42"],
    "severity": "high"
  },
  ...
}
```

## Data Flow

```
1. CLI Entry (main.py)
   └─ Parse arguments (file/dir, format, context)

2. Orchestrator Initialization
   └─ Create expert instances with local Ollama

3. File Analysis
   ├─ Read file content
   ├─ Build file-specific prompt
   ├─ Query model via Ollama
   ├─ Parse response into ExpertResponse
   └─ Repeat for each expert

4. Aggregation
   ├─ Collect all ExpertResponse objects
   ├─ Determine overall severity
   └─ Create MOEReport

5. Report Generation
   ├─ Format findings
   ├─ Render HTML/JSON
   └─ Save to output directory
```

## Communication Protocol

### Local LLM Communication

```
Client → Ollama API (HTTP, container port 11434)
         ├─ Chat endpoint: POST /api/chat
         ├─ List models: GET /api/tags
         └─ Generate: POST /api/generate

All communication stays within the Docker network.
No external network calls are made.
```

### Prompt Engineering Strategy

Each expert uses a **System Prompt** to establish role and expected output format:

```
[SYSTEM]
You are a {role} expert specialized in:
- {domain 1}
- {domain 2}
- ...

Return findings in this exact JSON format:
{
  "findings": [...],
  "severity": "critical|high|medium|low",
  ...
}

[USER]
{code snippet}

{context if provided}
```

**Prompt Parameters**:
- **Temperature**: Controls randomness (lower = deterministic, higher = creative)
  - Security: 0.05 (deterministic, avoid false negatives)
  - Quality: 0.2 (balanced suggestions)
  - Tests: 0.3 (creative test cases)
  - Docs: 0.15 (consistent documentation)

## Performance Characteristics

### Model Selection Trade-offs

| Metric | Small (7B) | Medium (13B) | Large (34B) |
|--------|-----------|-------------|------------|
| Speed | Fast | Medium | Slow |
| Accuracy | Good | Better | Best |
| Memory | 8GB | 16GB | 32GB+ |
| Cost | Low | Medium | High |

### Recommended Hardware

**Minimum**:
- CPU: 8-core modern processor
- RAM: 32GB
- Disk: 70GB (for all models)

**Recommended**:
- CPU: 16+ cores
- RAM: 64GB
- GPU: NVIDIA A100/A6000 (40GB VRAM)
- Disk: 100GB SSD

**Cloud Alternative**: AWS EC2 g4dn instances

## Extensibility Points

### 1. Add New Expert

```python
class PerformanceExpert(BaseExpert):
    def __init__(self, host="http://localhost:11434"):
        super().__init__(model="your-model:size", host=host)
    
    def _build_prompt(self, code, context=None):
        return "Analyze for performance..."
    
    def analyze(self, code, context=None):
        response = self._query_model(...)
        return ExpertResponse(...)
```

Then register in `MOEOrchestrator._initialize_experts()`.

### 2. Custom Models

Edit `config/settings.py` ExpertModel enum:
```python
class ExpertModel(str, Enum):
    CUSTOM = "your-model:version"
```

Models must support Ollama's chat API.

### 3. Additional Tools

Experts can use external tools via subprocess:
```python
def _run_custom_analysis(self, code):
    result = subprocess.run(
        ["custom-tool", "--input", code],
        capture_output=True
    )
    return result.stdout
```

### 4. Report Formats

Add new format to `ReportGenerator`:
```python
def generate_pdf_report(self, report):
    # PDF generation logic
    pass

def generate_markdown_report(self, report):
    # Markdown generation logic
    pass
```

## Security Considerations

### Local Operation
- ✅ All code stays on your machine
- ✅ No cloud uploads
- ✅ GDPR/compliance friendly
- ✅ Zero external dependencies for inference
- ✅ No Ollama installation required on the host OS

### Model Provenance
- Models downloaded from Ollama Hub
- No model modifications
- Open-source model inspection possible

### Credentials Management
- Use `.env` for sensitive configuration
- `.env` is .gitignored
- Support for vault integration (future)

## Testing Strategy

### Unit Tests
- Test individual expert implementations
- Mock Ollama responses
- Verify prompt building logic

### Integration Tests
- Full pipeline with mock models
- Report generation validation
- End-to-end analysis flow

### System Tests
- Real Ollama inference (requires setup)
- Report quality assessment
- Performance benchmarking

Run tests:
```bash
pytest tests/ -v
pytest tests/ --cov=moe_qa  # With coverage
```

## CI/CD Integration

### GitHub Actions Workflow
- Runs MOE QA on every PR
- Comments results on PR
- Uploads artifacts
- Fails on critical severity

### Local Pre-commit
```bash
# Create .git/hooks/pre-commit
#!/bin/bash
python moe_qa/main.py . --format json
```

## Future Enhancements

1. **Parallel Expert Execution**
   - Use `asyncio` or `concurrent.futures`
   - Reduce analysis time

2. **Streaming Responses**
   - Real-time token streaming
   - Better UX for large analyses

3. **Fine-tuned Models**
   - Domain-specific versions
   - Higher accuracy for your codebase

4. **Multi-language Support**
   - TypeScript/JavaScript analyzer
   - Go, Rust, Java experts

5. **Advanced Reporting**
   - PDF with charts
   - SARIF format for IDE integration
   - Slack notifications

## References

- Ollama: https://ollama.ai
- LangChain: https://python.langchain.com
- OWASP Top 10: https://owasp.org/www-project-top-ten/
- PEP 257 Docstring Conventions: https://www.python.org/dev/peps/pep-0257/

---

**Trust Index: 7.5/10** — Architecture is stable, but tools and model capabilities evolve rapidly.
