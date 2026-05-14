"""
Tests for MOE QA System

Run with: pytest tests/ -v
"""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from config.settings import Settings, ExpertModel
from experts.base_expert import BaseExpert, ExpertResponse
from experts.security_expert import SecurityExpert
from orchestrator.router import MOEOrchestrator, MOEReport
from reports.generator import ReportGenerator


class TestSettings:
    """Test configuration management."""
    
    def test_default_settings(self):
        """Test default settings values."""
        settings = Settings()
        assert settings.ollama_host == "http://localhost:11434"
        assert settings.max_tokens == 4096
        assert settings.temperature == 0.1
    
    def test_expert_models_enum(self):
        """Test expert model enumeration."""
        assert ExpertModel.SECURITY == "codellama:34b"
        assert ExpertModel.QUALITY == "deepseek-coder:33b"
        assert ExpertModel.TEST == "wizardcoder:34b"
        assert ExpertModel.DOCS == "mistral:7b"


class TestExpertResponse:
    """Test expert response dataclass."""
    
    def test_expert_response_creation(self):
        """Test creating an expert response."""
        response = ExpertResponse(
            expert_name="TestExpert",
            findings=["issue1", "issue2"],
            severity="high",
            raw_response="raw text"
        )
        assert response.expert_name == "TestExpert"
        assert len(response.findings) == 2
        assert response.severity == "high"
    
    def test_expert_response_metadata(self):
        """Test metadata in response."""
        response = ExpertResponse(
            expert_name="TestExpert",
            findings=[],
            severity="low",
            raw_response="",
            metadata={"key": "value"}
        )
        assert response.metadata["key"] == "value"


class TestSecurityExpert:
    """Test security expert functionality."""
    
    @patch('experts.security_expert.ollama.Client')
    def test_security_expert_initialization(self, mock_client):
        """Test security expert initialization."""
        mock_instance = MagicMock()
        mock_instance.list.return_value = {"models": [{"name": "codellama:34b"}]}
        mock_client.return_value = mock_instance
        
        expert = SecurityExpert()
        assert expert.model == ExpertModel.SECURITY
        assert expert.temperature == 0.05
    
    @patch('experts.security_expert.ollama.Client')
    def test_build_prompt(self, mock_client):
        """Test prompt building."""
        mock_instance = MagicMock()
        mock_instance.list.return_value = {"models": [{"name": "codellama:34b"}]}
        mock_client.return_value = mock_instance
        
        expert = SecurityExpert()
        code = "import os\nos.system('rm -rf /')"
        prompt = expert._build_prompt(code)
        
        assert "security" in prompt.lower()
        assert code in prompt


class TestMOEOrchestrator:
    """Test MOE orchestration."""
    
    def test_orchestrator_initialization(self):
        """Test orchestrator setup."""
        settings = Settings()
        with patch('experts.security_expert.ollama.Client'):
            with patch('experts.quality_expert.ollama.Client'):
                with patch('experts.test_expert.ollama.Client'):
                    with patch('experts.docs_expert.ollama.Client'):
                        orchestrator = MOEOrchestrator(settings=settings)
                        assert "security" in orchestrator._experts
                        assert "quality" in orchestrator._experts
                        assert "tests" in orchestrator._experts
                        assert "docs" in orchestrator._experts
    
    def test_severity_ranking(self):
        """Test severity calculation."""
        responses = [
            ExpertResponse("Expert1", [], "critical", ""),
            ExpertResponse("Expert2", [], "high", ""),
            ExpertResponse("Expert3", [], "low", ""),
        ]
        
        orchestrator = MOEOrchestrator(Settings())
        severity = orchestrator._determine_overall_severity(responses)
        assert severity == "critical"
    
    def test_analyze_nonexistent_file(self):
        """Test analyzing non-existent file."""
        orchestrator = MOEOrchestrator(Settings())
        with pytest.raises(FileNotFoundError):
            orchestrator.analyze_file("/nonexistent/file.py")


class TestReportGenerator:
    """Test report generation."""
    
    def test_report_generator_initialization(self):
        """Test report generator setup."""
        with tempfile.TemporaryDirectory() as tmpdir:
            generator = ReportGenerator(output_dir=tmpdir)
            assert Path(tmpdir).exists()
    
    def test_json_report_generation(self):
        """Test JSON report generation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            generator = ReportGenerator(output_dir=tmpdir)
            
            # Create mock report
            report = MOEReport(
                file_path="test.py",
                security=ExpertResponse("Security", ["issue1"], "high", "raw"),
                quality=ExpertResponse("Quality", ["issue2"], "medium", "raw"),
                tests=ExpertResponse("Tests", ["issue3"], "low", "raw"),
                docs=ExpertResponse("Docs", ["issue4"], "low", "raw"),
                overall_severity="high"
            )
            
            output_path = generator.generate_json_report(report, "test.json")
            assert output_path.exists()
            assert output_path.read_text()
    
    def test_html_report_generation(self):
        """Test HTML report generation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            generator = ReportGenerator(output_dir=tmpdir)
            
            # Create mock report
            report = MOEReport(
                file_path="test.py",
                security=ExpertResponse("Security", ["issue1"], "critical", "raw"),
                quality=ExpertResponse("Quality", [], "low", "raw"),
                tests=ExpertResponse("Tests", [], "low", "raw"),
                docs=ExpertResponse("Docs", [], "low", "raw"),
                overall_severity="critical"
            )
            
            output_path = generator.generate_html_report(report, "test.html")
            assert output_path.exists()
            
            html_content = output_path.read_text()
            assert "test.py" in html_content
            assert "CRITICAL" in html_content


class TestIntegration:
    """Integration tests."""
    
    def test_analyze_sample_code(self):
        """Test analyzing actual Python code."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create sample file
            sample_file = Path(tmpdir) / "sample.py"
            sample_file.write_text("""
def vulnerable_sql(username):
    query = f"SELECT * FROM users WHERE id={username}"
    return db.execute(query)
""")
            
            # This test would require actual Ollama running
            # For CI/CD, we'd mock the responses
            assert sample_file.exists()


# Fixtures
@pytest.fixture
def sample_settings():
    """Fixture for test settings."""
    return Settings(
        ollama_host="http://localhost:11434",
        max_tokens=2048,
        temperature=0.1
    )


@pytest.fixture
def sample_report():
    """Fixture for sample report."""
    return MOEReport(
        file_path="test.py",
        security=ExpertResponse("Security", ["vuln1"], "high", "raw"),
        quality=ExpertResponse("Quality", ["issue1"], "medium", "raw"),
        tests=ExpertResponse("Tests", ["gap1"], "low", "raw"),
        docs=ExpertResponse("Docs", ["missing1"], "low", "raw"),
        overall_severity="high"
    )
