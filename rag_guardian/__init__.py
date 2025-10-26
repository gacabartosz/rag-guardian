"""RAG Guardian - Production-grade quality assurance for RAG systems."""

__version__ = "0.1.0"
__author__ = "Bartosz Gaca"
__email__ = "hello@bartoszgaca.pl"

from rag_guardian.core.config import Config
from rag_guardian.core.types import EvaluationResult, TestCase, RAGOutput, MetricScore

__all__ = [
    "Config",
    "EvaluationResult",
    "TestCase",
    "RAGOutput",
    "MetricScore",
    "__version__",
]
