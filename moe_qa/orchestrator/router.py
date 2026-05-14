"""
MOE Orchestrator - Routes code analysis to appropriate experts.

References
----------
- LangChain local: https://python.langchain.com/docs/guides/local_llms
- Ollama Python: https://github.com/ollama/ollama-python (v0.1.x)
"""

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator

from experts.security_expert import SecurityExpert
from experts.quality_expert import QualityExpert
from experts.test_expert import TestExpert
from experts.docs_expert import DocsExpert
from experts.base_expert import ExpertResponse
from config.settings import Settings

logger = logging.getLogger(__name__)


@dataclass
class MOEReport:
    """
    Aggregated report from all experts.

    Parameters
    ----------
    file_path : str
        Analyzed file path.
    security : ExpertResponse
        Security expert findings.
    quality : ExpertResponse
        Code quality findings.
    tests : ExpertResponse
        Test coverage findings.
    docs : ExpertResponse
        Documentation findings.
    overall_severity : str
        Highest severity across all experts.
    """

    file_path: str
    security: ExpertResponse
    quality: ExpertResponse
    tests: ExpertResponse
    docs: ExpertResponse
    overall_severity: str


SEVERITY_RANK = {"critical": 4, "high": 3, "medium": 2, "low": 1, "unknown": 0}


class MOEOrchestrator:
    """
    Orchestrates multiple QA experts for comprehensive code analysis.

    Parameters
    ----------
    settings : Settings
        Application configuration.

    Examples
    --------
    >>> orchestrator = MOEOrchestrator(settings=Settings())
    >>> report = orchestrator.analyze_file("src/auth.py")
    >>> print(report.overall_severity)
    'critical'
    """

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._experts = self._initialize_experts()

    def _initialize_experts(self) -> dict:
        """
        Initialize all expert instances with local models.

        Returns
        -------
        dict
            Mapping of expert names to initialized instances.
        """
        host = self._settings.ollama_host
        return {
            "security": SecurityExpert(host=host),
            "quality": QualityExpert(host=host),
            "tests": TestExpert(host=host),
            "docs": DocsExpert(host=host),
        }

    def _determine_overall_severity(self, responses: list[ExpertResponse]) -> str:
        """
        Compute overall severity from all expert responses.

        Parameters
        ----------
        responses : list[ExpertResponse]
            All expert responses to aggregate.

        Returns
        -------
        str
            Highest severity level found.
        """
        return max(
            responses,
            key=lambda r: SEVERITY_RANK.get(r.severity, 0),
        ).severity

    def analyze_file(self, file_path: str, context: str = None) -> MOEReport:
        """
        Run all experts against a single file.

        Parameters
        ----------
        file_path : str
            Path to the source file to analyze.
        context : str, optional
            Additional context for analysis (e.g., framework, dependencies).

        Returns
        -------
        MOEReport
            Aggregated findings from all experts.

        Raises
        ------
        FileNotFoundError
            If the specified file does not exist.
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        code = path.read_text(encoding="utf-8")

        # Run all experts in parallel (conceptually - actual parallelization can be added)
        logger.info(f"Analyzing {file_path} with all experts...")

        security_response = self._experts["security"].analyze(code, context)
        quality_response = self._experts["quality"].analyze(code, context)
        test_response = self._experts["tests"].analyze(code, context)
        docs_response = self._experts["docs"].analyze(code, context)

        responses = [security_response, quality_response, test_response, docs_response]
        overall_severity = self._determine_overall_severity(responses)

        report = MOEReport(
            file_path=str(file_path),
            security=security_response,
            quality=quality_response,
            tests=test_response,
            docs=docs_response,
            overall_severity=overall_severity,
        )

        logger.info(
            f"Analysis complete for {file_path}. Overall severity: {overall_severity}"
        )
        return report

    def analyze_directory(
        self, directory_path: str, pattern: str = "**/*.py", context: str = None
    ) -> Iterator[MOEReport]:
        """
        Analyze all matching files in a directory recursively.

        Parameters
        ----------
        directory_path : str
            Root directory to analyze.
        pattern : str
            Glob pattern for files to analyze (default: "**/*.py").
        context : str, optional
            Additional context for analysis.

        Yields
        ------
        MOEReport
            Report for each analyzed file.

        Raises
        ------
        NotADirectoryError
            If the specified path is not a directory.
        """
        directory = Path(directory_path)
        if not directory.is_dir():
            raise NotADirectoryError(f"Not a directory: {directory_path}")

        files = list(directory.glob(pattern))
        logger.info(f"Found {len(files)} files matching pattern '{pattern}'")

        for file_path in files:
            try:
                yield self.analyze_file(str(file_path), context)
            except Exception as exc:
                logger.error(f"Error analyzing {file_path}: {exc}")
                continue
