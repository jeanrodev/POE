"""
Documentation Expert for documentation quality and completeness.

References
----------
- Google Style Guide: https://google.github.io/styleguide/pyguide.html
- Sphinx: https://www.sphinx-doc.org/
- PEP 257: https://www.python.org/dev/peps/pep-0257/
"""

from typing import Optional
import logging

from .base_expert import BaseExpert, ExpertResponse
from config.settings import ExpertModel

logger = logging.getLogger(__name__)


DOCS_SYSTEM_PROMPT = """You are a technical documentation expert specialized in:
- Docstring completeness (Google/NumPy style)
- API documentation clarity
- Code comments quality
- Example accuracy
- README and architectural documentation

Analyze the code and return findings in this exact JSON format:
{
    "findings": ["gap1", "gap2"],
    "severity": "critical|high|medium|low",
    "missing_docstrings": [],
    "documentation_improvements": []
}
"""


class DocsExpert(BaseExpert):
    """
    Expert specialized in documentation quality and completeness.

    Parameters
    ----------
    host : str
        Local Ollama server URL.
    """

    def __init__(self, host: str = "http://localhost:11434") -> None:
        super().__init__(
            model=ExpertModel.DOCS,
            host=host,
            temperature=0.15,
        )

    def _build_prompt(
        self, code_snippet: str, context: Optional[str] = None
    ) -> str:
        """Build documentation-focused analysis prompt."""
        context_block = f"\nContext: {context}" if context else ""
        return (
            f"{DOCS_SYSTEM_PROMPT}"
            f"{context_block}\n\n"
            f"```python\n{code_snippet}\n```\n\n"
            "Provide documentation analysis:"
        )

    def _build_fix_prompt(
        self, code: str, context: Optional[str] = None
    ) -> str:
        """Build a documentation-focused fix prompt."""
        context_block = f"\nContext: {context}" if context else ""
        return (
            "You are a technical documentation expert. Add or improve all "
            "docstrings and inline comments in the code below (NumPy/Google style)."
            f"{context_block}\n\n"
            "Rules:\n"
            "- Return ONLY the complete Python code with improved docs, no explanations.\n"
            "- Every public function, class, and method must have a docstring.\n"
            "- Do not change any logic or behaviour.\n\n"
            f"```python\n{code}\n```"
        )

    def analyze(
        self, code_snippet: str, context: Optional[str] = None
    ) -> ExpertResponse:
        """
        Perform comprehensive documentation analysis.

        Parameters
        ----------
        code_snippet : str
            Source code to analyze.
        context : str, optional
            Additional context for analysis.

        Returns
        -------
        ExpertResponse
            Standardized expert response with documentation findings.
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
            expert_name="DocsExpert",
            findings=findings,
            severity=severity,
            raw_response=raw_response,
            metadata={
                "missing_docstrings": (
                    llm_data.get("missing_docstrings", [])
                    if isinstance(llm_data, dict)
                    else []
                )
            },
        )
