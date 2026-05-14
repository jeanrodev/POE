"""
Main entry point for MOE QA System.

Provides CLI interface for analyzing Python files and directories.

Usage
-----
    python main.py <file_or_directory> [--format html|json] [--context "context string"]

Examples
--------
    # Analyze single file
    python main.py src/auth.py --format html

    # Analyze directory
    python main.py src/ --format json

    # Analyze with context
    python main.py src/api.py --context "FastAPI v0.100"
"""

import argparse
import logging
from pathlib import Path

from config.settings import Settings
from orchestrator.router import MOEOrchestrator
from reports.generator import ReportGenerator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="MOE Quality Assurance System - GDPR Compliant Local LLM QA",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py src/auth.py --format html
  python main.py src/ --format json --context "FastAPI framework"
        """,
    )

    parser.add_argument(
        "target",
        help="File or directory to analyze",
    )

    parser.add_argument(
        "--format",
        choices=["html", "json"],
        default="html",
        help="Output report format (default: html)",
    )

    parser.add_argument(
        "--context",
        type=str,
        default=None,
        help="Additional context for analysis (e.g., framework, dependencies)",
    )

    parser.add_argument(
        "--output-dir",
        type=str,
        default="./qa_reports",
        help="Output directory for reports (default: ./qa_reports)",
    )

    args = parser.parse_args()

    try:
        # Initialize settings
        settings = Settings(report_output_dir=args.output_dir)

        # Create orchestrator
        orchestrator = MOEOrchestrator(settings=settings)

        # Create report generator
        generator = ReportGenerator(output_dir=args.output_dir)

        # Analyze target
        target_path = Path(args.target)

        if target_path.is_file():
            logger.info(f"Analyzing file: {args.target}")
            report = orchestrator.analyze_file(args.target, context=args.context)
            
            # Generate report
            if args.format == "html":
                output_path = generator.generate_html_report(report)
            else:
                output_path = generator.generate_json_report(report)

            logger.info(f"Report saved to: {output_path}")
            print(f"\n✓ Report generated: {output_path}")
            print(f"  Overall Severity: {report.overall_severity.upper()}")

        elif target_path.is_dir():
            logger.info(f"Analyzing directory: {args.target}")
            reports = list(
                orchestrator.analyze_directory(args.target, context=args.context)
            )
            logger.info(f"Analyzed {len(reports)} files")

            # Generate reports
            for report in reports:
                if args.format == "html":
                    output_path = generator.generate_html_report(report)
                else:
                    output_path = generator.generate_json_report(report)

                logger.info(f"Report saved: {output_path}")

            print(f"\n✓ {len(reports)} reports generated in {args.output_dir}")

        else:
            logger.error(f"Target not found: {args.target}")
            print(f"✗ Error: {args.target} is not a valid file or directory")
            return 1

        return 0

    except Exception as exc:
        logger.error(f"Error during analysis: {exc}", exc_info=True)
        print(f"✗ Error: {exc}")
        return 1


if __name__ == "__main__":
    exit(main())
