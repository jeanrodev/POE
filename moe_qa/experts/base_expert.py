"""
Base Expert module defining the interface for all QA experts.

References
----------
- Ollama Python: https://github.com/ollama/ollama-python
- ABC Python docs: https://docs.python.org/3/library/abc.html
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional
import re
import ollama
import logging

logger = logging.getLogger(__name__)


@dataclass
class ExpertResponse:
    """
    Standardized response from any expert.

    Parameters
    ----------
    expert_name : str
        Name of the expert that generated this response.
    findings : list[str]
        List of identified issues or suggestions.
    severity : str
        Overall severity: 'critical', 'high', 'medium', 'low'.
    raw_response : str
        Raw model output for traceability.
    metadata : dict
        Additional context from the expert.
    """

    expert_name: str
    findings: list[str]
    severity: str
    raw_response: str
    metadata: dict = field(default_factory=dict)


class BaseExpert(ABC):
    """
    Abstract base class for all QA experts.

    Parameters
    ----------
    model : str
        Ollama model identifier to use.
    host : str
        Local Ollama server URL.
    temperature : float
        Sampling temperature for generation.

    Notes
    -----
    All subclasses MUST implement `analyze` and `_build_prompt`.
    Communication is strictly local via Ollama API.
    """

    def __init__(
        self,
        model: str,
        host: str = "http://localhost:11434",
        temperature: float = 0.1,
    ) -> None:
        self.model = model
        self.temperature = temperature
        self._client = ollama.Client(host=host)
        self._validate_model_available()

    def _validate_model_available(self) -> None:
        """
        Ensure the model is pulled locally before use.

        Raises
        ------
        RuntimeError
            If the model is not available locally.
        """
        try:
            available_models = [m.model for m in self._client.list().models]
            if self.model not in available_models:
                raise RuntimeError(
                    f"Model '{self.model}' not found locally. "
                    f"Run: ollama pull {self.model}"
                )
        except Exception as exc:
            logger.warning(f"Could not validate model availability: {exc}")

    def _query_model(self, prompt: str) -> str:
        """
        Send prompt to local model and retrieve response.

        Parameters
        ----------
        prompt : str
            Formatted prompt for the model.

        Returns
        -------
        str
            Model response text.

        Raises
        ------
        ConnectionError
            If local Ollama server is unreachable.
        """
        try:
            response = self._client.chat(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                options={"temperature": self.temperature},
            )
            return response["message"]["content"]
        except Exception as exc:
            logger.error("Failed to query local model %s: %s", self.model, exc)
            raise

    def _extract_code(self, response: str) -> str:
        """
        Extract raw code from a model response that may be wrapped in markdown fences.

        Parameters
        ----------
        response : str
            Raw model output, possibly containing ```python ... ``` blocks.

        Returns
        -------
        str
            The extracted code, or the full response if no fences were found.
        """
        match = re.search(r"```(?:python)?\n(.*?)```", response, re.DOTALL)
        if match:
            return match.group(1).strip()
        return response.strip()

    def _build_fix_prompt(
        self, code: str, context: Optional[str] = None
    ) -> str:
        """
        Build the expert-specific prompt for in-place code fixing.

        Subclasses should override this with domain-specific instructions.

        Parameters
        ----------
        code : str
            Original source code.
        context : str, optional
            Additional context (framework, dependencies).

        Returns
        -------
        str
            Prompt requesting fixed code as output.
        """
        context_block = f"\nContext: {context}" if context else ""
        return (
            f"You are an expert code reviewer. Fix all issues in the code below."
            f"{context_block}\n\n"
            f"Return ONLY the complete corrected Python code with no explanations.\n\n"
            f"```python\n{code}\n```"
        )

    def fix(self, code: str, context: Optional[str] = None) -> str:
        """
        Apply expert-specific fixes to code and return the corrected version.

        This is the in-place editing counterpart to `analyze()`. Each expert
        applies its domain knowledge to rewrite the code.

        Parameters
        ----------
        code : str
            Original source code.
        context : str, optional
            Additional context for analysis.

        Returns
        -------
        str
            Fixed source code. Falls back to original if the model fails.
        """
        try:
            prompt = self._build_fix_prompt(code, context)
            raw = self._query_model(prompt)
            fixed = self._extract_code(raw)
            # Sanity check: reject if the result is suspiciously short
            if len(fixed) < len(code) * 0.3:
                logger.warning(
                    "%s returned suspiciously short fix output — keeping original",
                    self.__class__.__name__,
                )
                return code
            return fixed
        except Exception as exc:
            logger.error("%s.fix() failed: %s", self.__class__.__name__, exc)
            return code

    @abstractmethod
    def _build_prompt(self, code_snippet: str, context: Optional[str]) -> str:
        """Build expert-specific analysis prompt."""
        ...

    @abstractmethod
    def analyze(
        self, code_snippet: str, context: Optional[str] = None
    ) -> ExpertResponse:
        """Run expert analysis on provided code."""
        ...
