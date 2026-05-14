# Contributing to MOE QA System

Thank you for your interest in contributing to the MOE QA System!

## Development Setup

```bash
# Clone the repository
git clone <repo-url>
cd POE

# Run setup script
bash setup.sh          # Linux/macOS
# or
powershell -ExecutionPolicy Bypass -File setup.ps1  # Windows

# Download models
bash setup-models.sh
```

## Code Style

We follow PEP 8 with a few conventions:

```bash
# Format code
black moe_qa/

# Check style
flake8 moe_qa/

# Type checking
mypy moe_qa/
```

## Testing

```bash
# Run all tests
pytest tests/ -v

# With coverage
pytest tests/ --cov=moe_qa
```

## Areas for Contribution

### 1. Additional Expert Roles
- **Performance Expert**: Profiling, optimization, bottleneck detection
- **Accessibility Expert**: WCAG compliance, a11y best practices
- **DevOps Expert**: Container, k8s, infrastructure analysis

### 2. Language Support
- JavaScript/TypeScript analyzer
- Go analyzer
- Rust analyzer
- C/C++ analyzer

### 3. Infrastructure
- GitHub Actions CI/CD integration
- GitLab CI integration
- Jenkins integration
- Parallel expert execution (threading/async)

### 4. Reporting
- PDF report generation
- SARIF format support (VS Code integration)
- Slack integration
- GitHub PR comments

### 5. Models
- Fine-tuned models for specific domains
- Lightweight quantized versions
- Real-time streaming responses

## Adding a New Expert

1. Create a new file in `moe_qa/experts/`:
   ```python
   from experts.base_expert import BaseExpert, ExpertResponse
   
   class PerformanceExpert(BaseExpert):
       def _build_prompt(self, code, context=None):
           return f"Analyze performance: {code}"
       
       def analyze(self, code, context=None):
           response = self._query_model(self._build_prompt(code, context))
           return ExpertResponse(
               expert_name="PerformanceExpert",
               findings=[response],
               severity="medium",
               raw_response=response
           )
   ```

2. Register in `orchestrator/router.py`:
   ```python
   from experts.performance_expert import PerformanceExpert
   
   def _initialize_experts(self):
       return {
           ...
           "performance": PerformanceExpert(host=self._settings.ollama_host),
       }
   ```

3. Update `MOEReport` dataclass to include new expert

4. Test with examples

## Submitting Changes

1. Fork the repository
2. Create feature branch: `git checkout -b feature/new-expert`
3. Commit with clear messages: `git commit -m "Add PerformanceExpert"`
4. Push to branch: `git push origin feature/new-expert`
5. Open Pull Request with description

## Pull Request Guidelines

- Include tests for new features
- Update documentation
- Run `black` and `mypy`
- Keep PRs focused on single feature/fix
- Reference issues when applicable

## Reporting Issues

Before reporting, check:
1. Ollama is running: `curl http://localhost:11434/api/tags`
2. Models are installed: `ollama list`
3. Latest code: `git pull origin main`

Include in issue report:
- Python version
- OS and Docker version
- Error logs from `qa_reports/`
- Minimal code reproduction

## License

By contributing, you agree that your contributions will be licensed under the same license as the project.

## Code of Conduct

Be respectful, constructive, and inclusive. We're building tools to improve software quality for everyone.

---

Questions? Open a discussion or reach out to maintainers.
