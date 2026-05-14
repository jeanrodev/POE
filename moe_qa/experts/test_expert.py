"""
Test Coverage Expert for test generation and coverage analysis.

References
----------
- Pytest: https://docs.pytest.org/
- Coverage.py: https://coverage.readthedocs.io/
- Hypothesis: https://hypothesis.readthedocs.io/
"""

import subprocess
from typing import Optional
import logging

from .base_expert import BaseExpert, ExpertResponse
from config.settings import ExpertModel

logger = logging.getLogger(__name__)


TEST_SYSTEM_PROMPT = """You are a test engineering expert specialized in:
- Unit test design and best practices
- Test coverage optimization
- Property-based testing
- Mock and fixture strategies
- Edge case identification

Analyze the code and return findings in this exact JSON format:
{
    "findings": ["gap1", "gap2"],
    "severity": "critical|high|medium|low",
    "test_suggestions": [],
    "coverage_gaps": [],
    "edge_cases": []
}
"""


class TestExpert(BaseExpert):
    """
    Expert specialized in test coverage and test generation.

    Parameters
    ----------
    host : str
        Local Ollama server URL.
    """

    def __init__(self, host: str = "http://localhost:11434") -> None:
        super().__init__(
            model=ExpertModel.TEST,
            host=host,
            temperature=0.3,
        )

    def _build_prompt(self, code_snippet: str, context: Optional[str] = None) -> str:
        """Build test-focused analysis prompt."""
        context_block = f"\nContext: {context}" if context else ""
        return (
            f"{TEST_SYSTEM_PROMPT}"
            f"{context_block}\n\n"
            f"```python\n{code_snippet}\n```\n\n"
            "Provide test coverage analysis:"
        )

    def analyze(
        self, code_snippet: str, context: Optional[str] = None
    ) -> ExpertResponse:
        """
        Perform comprehensive test coverage analysis.

        Parameters
        ----------
        code_snippet : str
            Source code to analyze.
        context : str, optional
            Additional context for analysis.

        Returns
        -------
        ExpertResponse
            Standardized expert response with test findings.
        """
        import json

        # LLM-based analysis
        prompt = self._build_prompt(code_snippet, context)
        raw_response = self._query_model(prompt)

        # Parse LLM response
        try:
            llm_data = json.loads(raw_response)
            findings = llm_data.get("findings", [])
            severity = llm_data.get("severity", "medium")
        except json.JSONDecodeError:
            findings = [raw_response]
            severity = "unknown"

        return ExpertResponse(
            expert_name="TestExpert",
            findings=findings,
            severity=severity,
            raw_response=raw_response,
            metadata={
                "test_suggestions": llm_data.get("test_suggestions", [])
                if isinstance(llm_data, dict)
                else []
            },
        )
