"""RAG Guardian - Production-grade quality assurance for RAG systems."""

__version__ = "1.0.0"
__author__ = "Bartosz Gaca"
__email__ = "gaca.bartosz@gmail.com"

# Core types and config
from rag_guardian.core.config import Config
from rag_guardian.core.loader import DataLoader
from rag_guardian.core.pipeline import EvaluationPipeline, Evaluator
from rag_guardian.core.types import (
    EvaluationResult,
    MetricScore,
    MetricType,
    RAGOutput,
    TestCase,
    TestCaseResult,
)

# Exceptions
from rag_guardian.exceptions import (
    ConfigurationError,
    DatasetError,
    IntegrationError,
    MetricComputationError,
    PipelineError,
    RAGGuardianError,
    ValidationError,
)

# Integrations
from rag_guardian.integrations.base import BaseRAGAdapter
from rag_guardian.integrations.custom import CustomHTTPAdapter, CustomRAGAdapter
from rag_guardian.integrations.langchain import (
    LangChainAdapter,
    LangChainRetrievalQAAdapter,
)
from rag_guardian.integrations.llamaindex import (
    LlamaIndexAdapter,
    LlamaIndexChatEngineAdapter,
    LlamaIndexVectorStoreAdapter,
)

# Metrics
from rag_guardian.metrics.base import BaseMetric

# Reporting
from rag_guardian.reporting.html import HTMLReporter
from rag_guardian.reporting.json import JSONReporter

__all__ = [
    # Version
    "__version__",
    # Core
    "Config",
    "DataLoader",
    "EvaluationPipeline",
    "Evaluator",
    # Types
    "EvaluationResult",
    "TestCase",
    "TestCaseResult",
    "RAGOutput",
    "MetricScore",
    "MetricType",
    # Exceptions
    "RAGGuardianError",
    "ConfigurationError",
    "DatasetError",
    "MetricComputationError",
    "IntegrationError",
    "ValidationError",
    "PipelineError",
    # Integrations
    "BaseRAGAdapter",
    "CustomRAGAdapter",
    "CustomHTTPAdapter",
    # LangChain
    "LangChainAdapter",
    "LangChainRetrievalQAAdapter",
    # LlamaIndex
    "LlamaIndexAdapter",
    "LlamaIndexVectorStoreAdapter",
    "LlamaIndexChatEngineAdapter",
    # Metrics
    "BaseMetric",
    # Reporting
    "JSONReporter",
    "HTMLReporter",
]
