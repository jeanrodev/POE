"""
Code Quality Expert for refactoring and best practices.

References
----------
- PEP 8: https://www.python.org/dev/peps/pep-0008/
- Pylint: https://pylint.pycqa.org/
- Flake8: https://flake8.pycqa.org/
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


QUALITY_SYSTEM_PROMPT = """You are a code quality expert specialized in:
- Python best practices and PEP 8 compliance
- Code refactoring suggestions
- Design pattern recommendations
- Complexity analysis
- Naming conventions and documentation

Analyze the code and return findings in this exact JSON format:
{
    "findings": ["issue1", "issue2"],
    "severity": "critical|high|medium|low",
    "recommendations": [
        {
            "description": "specific refactoring suggestion",
            "priority": "critical|high|medium|low",
            "effort": "minimal|small|medium|large",
            "impact": "critical|high|medium|low",
            "code_before": "current code snippet",
            "code_after": "refactored code snippet"
        }
    ],
    "refactoring_suggestions": [],
    "patterns": []
}
"""


class QualityExpert(BaseExpert):
    """
    Expert specialized in code quality and refactoring suggestions.

    Uses both LLM analysis and static analysis tools (Pylint, Flake8).

    Parameters
    ----------
    host : str
        Local Ollama server URL.
    """

    def __init__(self, host: str = "http://localhost:11434") -> None:
        super().__init__(
            model=ExpertModel.QUALITY,
            host=host,
            temperature=0.2,
        )

    def _build_prompt(
        self, code_snippet: str, context: Optional[str] = None
    ) -> str:
        """Build quality-focused analysis prompt."""
        context_block = f"\nContext: {context}" if context else ""
        return (
            f"{QUALITY_SYSTEM_PROMPT}"
            f"{context_block}\n\n"
            f"```python\n{code_snippet}\n```\n\n"
            "Provide code quality analysis:"
        )

    def _build_fix_prompt(
        self, code: str, context: Optional[str] = None
    ) -> str:
        """Build a quality-focused fix prompt."""
        context_block = f"\nContext: {context}" if context else ""
        return (
            "You are a code quality expert. Refactor the code below to follow "
            "PEP 8, improve naming, reduce complexity, and apply best practices."
            f"{context_block}\n\n"
            "Rules:\n"
            "- Return ONLY the complete refactored Python code, no explanations.\n"
            "- Preserve all existing functionality exactly.\n"
            "- Fix code style, naming, and structure issues.\n\n"
            f"```python\n{code}\n```"
        )

    def _run_pylint(self, code_snippet: str) -> list[str]:
        """Run Pylint static analysis locally."""
        try:
            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".py", delete=False
            ) as tmp_file:
                tmp_file.write(code_snippet)
                tmp_path = tmp_file.name

            result = subprocess.run(
                ["pylint", tmp_path, "--output-format=json"],
                capture_output=True,
                text=True,
            )

            Path(tmp_path).unlink(missing_ok=True)

            if not result.stdout:
                return []

            pylint_data = json.loads(result.stdout)
            return [
                f"[Pylint] {msg['message']} ({msg['symbol']}) at line {msg['line']}"
                for msg in pylint_data
            ]
        except FileNotFoundError:
            logger.warning("Pylint not installed, skipping static analysis")
            return []
        except Exception as exc:
            logger.error(f"Error running Pylint: {exc}")
            return []

    def analyze(
        self, code_snippet: str, context: Optional[str] = None
    ) -> ExpertResponse:
        """
        Perform comprehensive code quality analysis.

        Parameters
        ----------
        code_snippet : str
            Source code to analyze.
        context : str, optional
            Additional context for analysis.

        Returns
        -------
        ExpertResponse
            Standardized expert response with quality findings.
        """
        # LLM-based analysis
        prompt = self._build_prompt(code_snippet, context)
        raw_response = self._query_model(prompt)

        # Static analysis via Pylint
        pylint_findings = self._run_pylint(code_snippet)

        # Parse LLM response
        findings = []
        severity = "medium"
        recommendations = []
        
        try:
            llm_data = json.loads(raw_response)
            findings = llm_data.get("findings", []) + pylint_findings
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
                        code_before=rec.get("code_before", ""),
                        code_after=rec.get("code_after", ""),
                    )
                )
        except json.JSONDecodeError:
            findings = pylint_findings + [raw_response]
            severity = "unknown"

        return ExpertResponse(
            expert_name="QualityExpert",
            findings=findings,
            severity=severity,
            recommendations=recommendations,
            raw_response=raw_response,
            metadata={"pylint_count": len(pylint_findings)},
        )
