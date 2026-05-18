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

from moe_qa.experts.security_expert import SecurityExpert
from moe_qa.experts.quality_expert import QualityExpert
from moe_qa.experts.test_expert import TestExpert
from moe_qa.experts.docs_expert import DocsExpert
from moe_qa.experts.base_expert import ExpertResponse
from moe_qa.config.settings import Settings

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

    def _determine_overall_severity(
        self, responses: list[ExpertResponse]
    ) -> str:
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

        responses = [
            security_response,
            quality_response,
            test_response,
            docs_response,
        ]
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

    def fix_file(
        self,
        file_path: str,
        context: str = None,
        experts: list = None,
        backup: bool = True,
    ) -> dict:
        """
        Apply expert fixes to a file in place.

        Experts are applied sequentially in priority order:
        security → quality → docs. Each expert receives the output of
        the previous one. The TestExpert generates a companion test file
        instead of modifying the source.

        Parameters
        ----------
        file_path : str
            Path to the source file to fix.
        context : str, optional
            Additional context for analysis.
        experts : list[str], optional
            Subset of experts to apply: 'security', 'quality', 'docs', 'tests'.
            Defaults to all four.
        backup : bool
            If True, write a ``.bak`` copy of the original before modifying.

        Returns
        -------
        dict
            Summary with keys: file_path, backup_path, tests_path,
            experts_applied, changes_made.

        Raises
        ------
        FileNotFoundError
            If the specified file does not exist.
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        original_code = path.read_text(encoding="utf-8")

        active_experts = experts or ["security", "quality", "docs", "tests"]
        # Canonical application order
        apply_order = [
            e for e in ["security", "quality", "docs"] if e in active_experts
        ]

        # Backup original
        backup_path = None
        if backup:
            backup_path = path.with_suffix(path.suffix + ".bak")
            backup_path.write_text(original_code, encoding="utf-8")
            logger.info("Backup written to %s", backup_path)

        # Chain source-modifying experts
        code = original_code
        for expert_name in apply_order:
            logger.info("Applying %s fixes to %s…", expert_name, file_path)
            code = self._experts[expert_name].fix(code, context)

        # Write fixed source back in place
        changes_made = code != original_code
        if changes_made:
            path.write_text(code, encoding="utf-8")
            logger.info("Fixed source written to %s", file_path)
        else:
            logger.info("No changes made to %s", file_path)

        # TestExpert: generate companion test file
        tests_path = None
        if "tests" in active_experts:
            test_code = self._experts["tests"].fix(code, context)
            if test_code:
                tests_dir = path.parent / "tests"
                tests_dir.mkdir(exist_ok=True)
                tests_path = tests_dir / f"test_{path.name}"
                tests_path.write_text(test_code, encoding="utf-8")
                logger.info("Generated tests written to %s", tests_path)

        return {
            "file_path": str(file_path),
            "backup_path": str(backup_path) if backup_path else None,
            "tests_path": str(tests_path) if tests_path else None,
            "experts_applied": apply_order
            + (["tests"] if "tests" in active_experts else []),
            "changes_made": changes_made,
        }

    def fix_directory(
        self,
        directory_path: str,
        pattern: str = "**/*.py",
        context: str = None,
        experts: list = None,
        backup: bool = True,
    ) -> list[dict]:
        """
        Apply expert fixes to all matching files in a directory.

        Parameters
        ----------
        directory_path : str
            Root directory to process.
        pattern : str
            Glob pattern for files to fix (default: ``**/*.py``).
        context : str, optional
            Additional context for analysis.
        experts : list[str], optional
            Subset of experts to apply.
        backup : bool
            If True, write ``.bak`` files before modifying.

        Returns
        -------
        list[dict]
            One summary dict per processed file.
        """
        directory = Path(directory_path)
        if not directory.is_dir():
            raise NotADirectoryError(f"Not a directory: {directory_path}")

        files = list(directory.glob(pattern))
        logger.info("Found %d files matching pattern '%s'", len(files), pattern)

        results = []
        for file_path in files:
            try:
                result = self.fix_file(
                    str(file_path),
                    context=context,
                    experts=experts,
                    backup=backup,
                )
                results.append(result)
            except Exception as exc:
                logger.error("Error fixing %s: %s", file_path, exc)
        return results

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
