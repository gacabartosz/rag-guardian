"""Configuration management for RAG Guardian."""

import os
import re
from pathlib import Path
from typing import Any, Dict, Optional

import yaml
from pydantic import BaseModel, Field, field_validator


class MetricConfig(BaseModel):
    """Configuration for a single metric."""

    enabled: bool = True
    threshold: float = 0.8
    required: bool = False


class RAGSystemConfig(BaseModel):
    """Configuration for RAG system connection."""

    type: str = "custom"  # "langchain", "llamaindex", "custom"
    endpoint: Optional[str] = None
    timeout: int = 30
    headers: Dict[str, str] = Field(default_factory=dict)


class MetricsConfig(BaseModel):
    """Configuration for all metrics."""

    faithfulness: MetricConfig = Field(default_factory=MetricConfig)
    groundedness: MetricConfig = Field(default_factory=MetricConfig)
    context_relevancy: MetricConfig = Field(default_factory=MetricConfig)
    answer_correctness: MetricConfig = Field(default_factory=MetricConfig)


class ReportingConfig(BaseModel):
    """Configuration for reporting."""

    formats: list[str] = Field(default_factory=lambda: ["json"])
    output_dir: str = "results"


class Config(BaseModel):
    """Main configuration for RAG Guardian."""

    version: str = "1.0"
    rag_system: RAGSystemConfig = Field(default_factory=RAGSystemConfig)
    metrics: MetricsConfig = Field(default_factory=MetricsConfig)
    reporting: ReportingConfig = Field(default_factory=ReportingConfig)

    @classmethod
    def from_yaml(cls, path: str) -> "Config":
        """Load configuration from YAML file."""
        yaml_path = Path(path)
        if not yaml_path.exists():
            raise FileNotFoundError(f"Config file not found: {path}")

        with open(yaml_path, "r") as f:
            raw_data = yaml.safe_load(f)

        # Substitute environment variables
        raw_data = cls._substitute_env_vars(raw_data)

        return cls(**raw_data)

    @classmethod
    def _substitute_env_vars(cls, data: Any) -> Any:
        """Recursively substitute environment variables in config."""
        if isinstance(data, dict):
            return {k: cls._substitute_env_vars(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [cls._substitute_env_vars(item) for item in data]
        elif isinstance(data, str):
            # Replace ${VAR_NAME} with environment variable value
            def replace_env_var(match):
                var_name = match.group(1)
                return os.environ.get(var_name, match.group(0))

            return re.sub(r"\$\{([^}]+)\}", replace_env_var, data)
        else:
            return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Config":
        """Create config from dictionary."""
        return cls(**data)

    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary."""
        return self.model_dump()
