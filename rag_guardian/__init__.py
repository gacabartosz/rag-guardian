"""RAG Guardian - Production-grade quality assurance for RAG systems."""

__version__ = "1.0.0"
__author__ = "Bartosz Gaca"
__email__ = "hello@bartoszgaca.pl"

# Core types and config
from rag_guardian.core.config import Config
from rag_guardian.core.pipeline import EvaluationPipeline, Evaluator
from rag_guardian.core.types import (
    EvaluationResult,
    MetricScore,
    RAGOutput,
    TestCase,
    TestCaseResult,
)

# Integrations
from rag_guardian.integrations.base import BaseRAGAdapter
from rag_guardian.integrations.custom import CustomHTTPAdapter, CustomRAGAdapter

# Metrics
from rag_guardian.metrics.base import BaseMetric

# Reporting
from rag_guardian.reporting.json import JSONReporter

__all__ = [
    # Version
    "__version__",
    # Core
    "Config",
    "EvaluationPipeline",
    "Evaluator",
    # Types
    "EvaluationResult",
    "TestCase",
    "TestCaseResult",
    "RAGOutput",
    "MetricScore",
    # Integrations
    "BaseRAGAdapter",
    "CustomRAGAdapter",
    "CustomHTTPAdapter",
    # Metrics
    "BaseMetric",
    # Reporting
    "JSONReporter",
]
