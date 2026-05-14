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
            available_models = [m["name"] for m in self._client.list()["models"]]
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

    @abstractmethod
    def _build_prompt(self, code_snippet: str, context: Optional[str]) -> str:
        """Build expert-specific prompt."""
        ...

    @abstractmethod
    def analyze(self, code_snippet: str, context: Optional[str] = None) -> ExpertResponse:
        """Run expert analysis on provided code."""
        ...
