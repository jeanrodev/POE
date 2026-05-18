"""
Configuration module for MOE QA System.

Notes
-----
Uses local Ollama instance exclusively.
No data transmitted to external services.

References
----------
- Ollama Python SDK: https://github.com/ollama/ollama-python (v0.1.x)
- Pydantic: https://docs.pydantic.dev/latest/ (v2.x)
"""

from pydantic import BaseSettings, Field
from enum import Enum


class ExpertModel(str, Enum):
    """Available local models for expert roles."""

    SECURITY = "codellama:7b"
    QUALITY = "deepseek-coder:6.7b"
    TEST = "wizardcoder:7b"
    DOCS = "mistral:7b"
    ORCHESTRATOR = "mistral:7b"


class Settings(BaseSettings):
    """
    Application settings loaded from environment.

    Parameters
    ----------
    ollama_host : str
        Local Ollama server host URL.
    max_tokens : int
        Maximum tokens per expert response.
    temperature : float
        Model temperature for responses.

    Examples
    --------
    >>> settings = Settings()
    >>> print(settings.ollama_host)
    'http://localhost:11434'
    """

    ollama_host: str = Field(
        default="http://localhost:11434",
        description="Local Ollama server - NEVER point to external URL"
    )
    max_tokens: int = Field(default=4096)
    temperature: float = Field(default=0.1)
    report_output_dir: str = Field(default="./qa_reports")

    class Config:
        env_file = ".env"
        env_prefix = "MOE_"
