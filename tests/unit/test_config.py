"""Unit tests for configuration."""

import os
import tempfile
from pathlib import Path

import pytest
import yaml

from rag_guardian.core.config import Config, MetricConfig


class TestConfig:
    """Tests for Config loading."""

    def test_default_config(self):
        """Test default configuration values."""
        config = Config()

        assert config.version == "1.0"
        assert config.rag_system.type == "custom"
        assert config.metrics.faithfulness.enabled
        assert config.metrics.faithfulness.threshold == 0.8

    def test_from_dict(self):
        """Test loading from dictionary."""
        data = {
            "version": "1.0",
            "rag_system": {"type": "langchain", "endpoint": "http://localhost:8000"},
            "metrics": {
                "faithfulness": {"enabled": True, "threshold": 0.85, "required": True}
            },
        }

        config = Config.from_dict(data)

        assert config.rag_system.type == "langchain"
        assert config.rag_system.endpoint == "http://localhost:8000"
        assert config.metrics.faithfulness.threshold == 0.85
        assert config.metrics.faithfulness.required

    def test_from_yaml(self):
        """Test loading from YAML file."""
        yaml_content = """
version: "1.0"
rag_system:
  type: langchain
  endpoint: http://localhost:8000
  timeout: 30

metrics:
  faithfulness:
    enabled: true
    threshold: 0.85
    required: true

  groundedness:
    enabled: true
    threshold: 0.80
"""

        # Create temporary YAML file
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".yml", delete=False
        ) as f:
            f.write(yaml_content)
            temp_path = f.name

        try:
            config = Config.from_yaml(temp_path)

            assert config.rag_system.type == "langchain"
            assert config.metrics.faithfulness.threshold == 0.85
            assert config.metrics.groundedness.threshold == 0.80
        finally:
            os.unlink(temp_path)

    def test_env_var_substitution(self):
        """Test environment variable substitution."""
        os.environ["TEST_ENDPOINT"] = "http://test-server:8000"
        os.environ["TEST_API_KEY"] = "secret-key-123"

        yaml_content = """
version: "1.0"
rag_system:
  type: custom
  endpoint: ${TEST_ENDPOINT}
  headers:
    Authorization: "Bearer ${TEST_API_KEY}"
"""

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".yml", delete=False
        ) as f:
            f.write(yaml_content)
            temp_path = f.name

        try:
            config = Config.from_yaml(temp_path)

            assert config.rag_system.endpoint == "http://test-server:8000"
            assert config.rag_system.headers["Authorization"] == "Bearer secret-key-123"
        finally:
            os.unlink(temp_path)
            del os.environ["TEST_ENDPOINT"]
            del os.environ["TEST_API_KEY"]

    def test_missing_file(self):
        """Test error on missing config file."""
        with pytest.raises(FileNotFoundError):
            Config.from_yaml("/nonexistent/path/config.yml")
