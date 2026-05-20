"""
Security Expert for vulnerability detection.

References
----------
- OWASP Top 10: https://owasp.org/www-project-top-ten/
- Bandit: https://bandit.readthedocs.io/en/latest/ (v1.7.x)
- Semgrep: https://semgrep.dev/docs/ (v1.x)
"""

import subprocess
import tempfile
import json
from pathlib import Path
from typing import Optional
import logging

from .base_expert import BaseExpert, ExpertResponse, Recommendation
from config.settings import ExpertModel

logger = logging.getLogger(__name__)


SECURITY_SYSTEM_PROMPT = """You are a cybersecurity expert specialized in:
- OWASP Top 10 vulnerabilities
- SQL Injection, XSS, CSRF detection
- Secrets and credentials leakage
- Dependency vulnerabilities
- Authentication/Authorization flaws

Analyze the code and return findings in this exact JSON format:
{
    "findings": ["finding1", "finding2"],
    "severity": "critical|high|medium|low",
    "recommendations": [
        {
            "description": "specific recommended change",
            "priority": "critical|high|medium|low",
            "effort": "minimal|small|medium|large",
            "impact": "critical|high|medium|low"
        }
    ],
    "cve_references": [],
    "remediation": []
}
"""


class SecurityExpert(BaseExpert):
    """
    Expert specialized in security vulnerability detection.

    Uses both LLM analysis and static analysis tools (Bandit, Semgrep)
    for comprehensive coverage.

    Parameters
    ----------
    host : str
        Local Ollama server URL.

    Examples
    --------
    >>> expert = SecurityExpert()
    >>> result = expert.analyze("user_input = request.get('id')")
    >>> print(result.severity)
    'high'
    """

    def __init__(self, host: str = "http://localhost:11434") -> None:
        super().__init__(
            model=ExpertModel.SECURITY,
            host=host,
            temperature=0.05,  # Low temp for deterministic security findings
        )

    def _build_prompt(
        self, code_snippet: str, context: Optional[str] = None
    ) -> str:
        """
        Build security-focused analysis prompt.

        Parameters
        ----------
        code_snippet : str
            Source code to analyze.
        context : str, optional
            Additional context (framework, language version, etc.).

        Returns
        -------
        str
            Formatted prompt string.
        """
        context_block = f"\nContext: {context}" if context else ""
        return (
            f"{SECURITY_SYSTEM_PROMPT}"
            f"{context_block}\n\n"
            f"```python\n{code_snippet}\n```\n\n"
            "Provide security analysis:"
        )

    def _run_bandit(self, code_snippet: str) -> list[str]:
        """
        Run Bandit static analysis locally.

        Parameters
        ----------
        code_snippet : str
            Python code to analyze.

        Returns
        -------
        list[str]
            List of Bandit findings.
        """
        try:
            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".py", delete=False
            ) as tmp_file:
                tmp_file.write(code_snippet)
                tmp_path = tmp_file.name

            result = subprocess.run(
                ["bandit", "-r", tmp_path, "-f", "json", "-q"],
                capture_output=True,
                text=True,
            )

            Path(tmp_path).unlink(missing_ok=True)

            if not result.stdout:
                return []

            bandit_data = json.loads(result.stdout)
            return [
                f"[Bandit] {issue['issue_text']} at line {issue['line_number']}"
                for issue in bandit_data.get("results", [])
            ]
        except FileNotFoundError:
            logger.warning("Bandit not installed, skipping static analysis")
            return []
        except Exception as exc:
            logger.error(f"Error running Bandit: {exc}")
            return []

    def _build_fix_prompt(
        self, code: str, context: Optional[str] = None
    ) -> str:
        """Build a security-focused fix prompt."""
        context_block = f"\nContext: {context}" if context else ""
        return (
            "You are a cybersecurity expert. Fix ALL security vulnerabilities in the "
            "code below (OWASP Top 10, injection flaws, secrets leakage, insecure "
            f"auth, etc.).{context_block}\n\n"
            "Rules:\n"
            "- Return ONLY the complete fixed Python code, no explanations.\n"
            "- Do not remove functionality; only fix security issues.\n"
            "- Add input validation and sanitisation where needed.\n\n"
            f"```python\n{code}\n```"
        )

    def analyze(
        self, code_snippet: str, context: Optional[str] = None
    ) -> ExpertResponse:
        """
        Perform comprehensive security analysis.

        Parameters
        ----------
        code_snippet : str
            Source code to analyze.
        context : str, optional
            Additional context for analysis.

        Returns
        -------
        ExpertResponse
            Standardized expert response with security findings.
        """
        # LLM-based analysis
        prompt = self._build_prompt(code_snippet, context)
        raw_response = self._query_model(prompt)

        # Static analysis via Bandit (local tool)
        bandit_findings = self._run_bandit(code_snippet)

        # Parse LLM response
        findings = []
        severity = "medium"
        recommendations = []
        
        try:
            llm_data = json.loads(raw_response)
            findings = llm_data.get("findings", []) + bandit_findings
            severity = llm_data.get("severity", "medium")
            
            # Parse recommendations
            rec_data = llm_data.get("recommendations", [])
            for rec in rec_data:
                recommendations.append(
                    Recommendation(
                        description=rec.get("description", ""),
                        priority=rec.get("priority", "medium"),
                        effort=rec.get("effort", "medium"),
                        impact=rec.get("impact", "medium"),
                    )
                )
        except json.JSONDecodeError:
            findings = bandit_findings + [raw_response]
            severity = "unknown"

        return ExpertResponse(
            expert_name="SecurityExpert",
            findings=findings,
            severity=severity,
            recommendations=recommendations,
            raw_response=raw_response,
            metadata={"bandit_count": len(bandit_findings)},
        )
