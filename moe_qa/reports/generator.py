"""
Report generation module for MOE QA System.

References
----------
- Jinja2: https://jinja.palletsprojects.com/
- Markdown: https://python-markdown.github.io/
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Optional

from orchestrator.router import MOEReport

logger_local = None


class ReportGenerator:
    """
    Generates HTML and JSON reports from MOE analysis results.

    Parameters
    ----------
    output_dir : str
        Directory to save generated reports.

    Examples
    --------
    >>> generator = ReportGenerator("./qa_reports")
    >>> generator.generate_html_report(moe_report, "report.html")
    """

    def __init__(self, output_dir: str = "./qa_reports") -> None:
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_json_report(self, report: MOEReport, filename: Optional[str] = None) -> Path:
        """
        Generate JSON report from MOE analysis.

        Parameters
        ----------
        report : MOEReport
            The MOE analysis report.
        filename : str, optional
            Output filename (default: auto-generated).

        Returns
        -------
        Path
            Path to generated JSON file.
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"moe_report_{timestamp}.json"

        report_data = {
            "file_path": report.file_path,
            "timestamp": datetime.now().isoformat(),
            "overall_severity": report.overall_severity,
            "security": {
                "findings": report.security.findings,
                "severity": report.security.severity,
            },
            "quality": {
                "findings": report.quality.findings,
                "severity": report.quality.severity,
            },
            "tests": {
                "findings": report.tests.findings,
                "severity": report.tests.severity,
            },
            "docs": {
                "findings": report.docs.findings,
                "severity": report.docs.severity,
            },
        }

        output_path = self.output_dir / filename
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(report_data, f, indent=2)

        return output_path

    def generate_html_report(self, report: MOEReport, filename: Optional[str] = None) -> Path:
        """
        Generate HTML report from MOE analysis.

        Parameters
        ----------
        report : MOEReport
            The MOE analysis report.
        filename : str, optional
            Output filename (default: auto-generated).

        Returns
        -------
        Path
            Path to generated HTML file.
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"moe_report_{timestamp}.html"

        html_content = self._build_html(report)
        output_path = self.output_dir / filename

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html_content)

        return output_path

    def _build_html(self, report: MOEReport) -> str:
        """Build HTML report content."""
        severity_color = {
            "critical": "#d32f2f",
            "high": "#f57c00",
            "medium": "#fbc02d",
            "low": "#388e3c",
            "unknown": "#757575",
        }

        def render_expert_section(name: str, response) -> str:
            color = severity_color.get(response.severity, "#757575")
            findings_html = "".join(
                f"<li>{finding}</li>" for finding in response.findings
            )
            return f"""
            <div class="expert-section">
                <h3 style="color: {color};">{name}</h3>
                <p><strong>Severity:</strong> <span style="color: {color}; font-weight: bold;">{response.severity.upper()}</span></p>
                <ul>
                    {findings_html}
                </ul>
            </div>
            """

        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>MOE QA Report - {report.file_path}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
                .header {{ background: #1976d2; color: white; padding: 20px; border-radius: 5px; margin-bottom: 20px; }}
                .container {{ background: white; padding: 20px; border-radius: 5px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
                .expert-section {{ margin: 20px 0; padding: 15px; border-left: 4px solid #1976d2; background: #f9f9f9; }}
                .expert-section h3 {{ margin-top: 0; }}
                ul {{ line-height: 1.8; }}
                .footer {{ text-align: center; margin-top: 30px; color: #666; font-size: 0.9em; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>MOE Quality Assurance Report</h1>
                <p><strong>File:</strong> {report.file_path}</p>
                <p><strong>Overall Severity:</strong> <span style="background: {severity_color.get(report.overall_severity, '#757575')}; color: white; padding: 5px 10px; border-radius: 3px;">{report.overall_severity.upper()}</span></p>
            </div>
            <div class="container">
                {render_expert_section("🔒 Security Expert", report.security)}
                {render_expert_section("📝 Code Quality Expert", report.quality)}
                {render_expert_section("🧪 Test Coverage Expert", report.tests)}
                {render_expert_section("📚 Documentation Expert", report.docs)}
            </div>
            <div class="footer">
                <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                <p>MOE QA System v0.1.0</p>
            </div>
        </body>
        </html>
        """
        return html
