"""
Pytest configuration for MOE QA System.

Define shared fixtures and test configuration here.
"""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch


@pytest.fixture
def temp_dir():
    """Provide a temporary directory for tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def mock_ollama_client():
    """Mock Ollama client for testing."""
    with patch('ollama.Client') as mock:
        client = MagicMock()
        client.list.return_value = {
            "models": [
                {"name": "codellama:34b"},
                {"name": "mistral:7b"},
            ]
        }
        client.chat.return_value = {
            "message": {"content": '{"findings": ["test finding"], "severity": "low"}'}
        }
        mock.return_value = client
        yield mock


@pytest.fixture
def sample_python_code():
    """Provide sample Python code for analysis."""
    return """
def process_user_input(data):
    # Process user input
    result = eval(data)  # DANGEROUS
    return result

def database_query(user_id):
    query = f"SELECT * FROM users WHERE id={user_id}"
    cursor.execute(query)
    return cursor.fetchall()
"""


@pytest.fixture
def sample_config():
    """Provide sample configuration."""
    from config.settings import Settings
    return Settings(
        ollama_host="http://localhost:11434",
        max_tokens=2048,
        temperature=0.1
    )
