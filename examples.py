"""
Example usage of MOE QA System

This script demonstrates how to use the MOE framework programmatically.
"""

from pathlib import Path
from moe_qa.config.settings import Settings
from moe_qa.orchestrator.router import MOEOrchestrator
from moe_qa.reports.generator import ReportGenerator


def example_single_file_analysis():
    """Analyze a single file and generate HTML report."""

    # Create sample Python file for analysis
    sample_code = '''
def authenticate_user(username, password):
    """Simple login function - VULNERABLE!"""
    query = f"SELECT * FROM users WHERE username='{username}' AND password='{password}'"
    result = db.execute(query)
    return result is not None
    
def process_user_input(user_data):
    """Process input without validation."""
    eval(user_data)  # DANGEROUS!
    return True
'''

    # Save sample file
    Path("sample_code.py").write_text(sample_code)

    # Initialize MOE system
    settings = Settings(report_output_dir="./qa_reports")
    orchestrator = MOEOrchestrator(settings=settings)
    generator = ReportGenerator(output_dir="./qa_reports")

    # Analyze file
    print("Analyzing sample_code.py...")
    report = orchestrator.analyze_file(
        file_path="sample_code.py",
        context="Simple authentication module (Python 3.9+)",
    )

    # Generate reports
    html_path = generator.generate_html_report(report)
    json_path = generator.generate_json_report(report)

    print(f"✓ HTML Report: {html_path}")
    print(f"✓ JSON Report: {json_path}")
    print(f"Overall Severity: {report.overall_severity}")

    return report


def example_directory_analysis():
    """Analyze all Python files in a directory."""

    settings = Settings(report_output_dir="./qa_reports")
    orchestrator = MOEOrchestrator(settings=settings)
    generator = ReportGenerator(output_dir="./qa_reports")

    # Create sample directory structure
    src_dir = Path("src")
    src_dir.mkdir(exist_ok=True)

    (src_dir / "auth.py").write_text("""
def login(user, pwd):
    import hashlib
    return hashlib.md5(f"{user}{pwd}".encode()).hexdigest()
""")

    (src_dir / "api.py").write_text("""
from fastapi import FastAPI
app = FastAPI()

@app.get("/users/{user_id}")
async def get_user(user_id: str):
    return {"user_id": user_id}
""")

    # Analyze directory
    print("Analyzing src/ directory...")
    report_count = 0

    for report in orchestrator.analyze_directory(
        directory_path="src/",
        pattern="**/*.py",
        context="FastAPI application v0.100.0",
    ):
        generator.generate_html_report(report)
        report_count += 1
        print(
            f"  ✓ Analyzed: {report.file_path} (severity: {report.overall_severity})"
        )

    print(f"✓ Analyzed {report_count} files")


def example_custom_context():
    """Demonstrate context-aware analysis."""

    settings = Settings()
    orchestrator = MOEOrchestrator(settings=settings)
    generator = ReportGenerator()

    # Code that's safe in one context but not another
    code_sample = """
import os
db_password = os.getenv("DB_PASSWORD")
api_key = os.getenv("API_KEY")
"""

    # Save for analysis
    Path("secrets_handling.py").write_text(code_sample)

    # Analyze WITH context
    print("Analyzing with production context...")
    report = orchestrator.analyze_file(
        file_path="secrets_handling.py",
        context="Production environment with strict security requirements",
    )

    generator.generate_html_report(report)
    print(f"Security severity: {report.security.severity}")

    # Analyze WITHOUT context
    print("Analyzing without context...")
    report2 = orchestrator.analyze_file(
        file_path="secrets_handling.py", context=None
    )

    generator.generate_html_report(report2)
    print(f"Security severity: {report2.security.severity}")


if __name__ == "__main__":
    print("MOE QA System - Example Usage\n")

    try:
        # Run examples
        print("=" * 50)
        print("Example 1: Single File Analysis")
        print("=" * 50)
        example_single_file_analysis()

        print("\n" + "=" * 50)
        print("Example 2: Directory Analysis")
        print("=" * 50)
        example_directory_analysis()

        print("\n" + "=" * 50)
        print("Example 3: Context-Aware Analysis")
        print("=" * 50)
        example_custom_context()

        print("\n✅ All examples completed successfully!")
        print("\nGenerated reports are in ./qa_reports/")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nMake sure Ollama is running and models are installed:")
        print("  docker-compose up -d")
        print(
            "  ollama pull codellama:34b deepseek-coder:33b wizardcoder:34b mistral:7b"
        )
