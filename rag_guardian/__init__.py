"""RAG Guardian - Production-grade quality assurance for RAG systems."""

__version__ = "0.1.0"
__author__ = "Bartosz Gaca"
__email__ = "hello@bartoszgaca.pl"

from rag_guardian.core.config import Config
from rag_guardian.core.pipeline import EvaluationPipeline
from rag_guardian.core.types import EvaluationResult, TestCase

__all__ = [
    "Config",
    "EvaluationPipeline",
    "EvaluationResult",
    "TestCase",
    "__version__",
]
