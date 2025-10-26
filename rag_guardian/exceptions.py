"""Custom exceptions for RAG Guardian."""


class RAGGuardianError(Exception):
    """Base exception for all RAG Guardian errors."""

    pass


class ConfigurationError(RAGGuardianError):
    """Raised when configuration is invalid or missing."""

    pass


class DatasetError(RAGGuardianError):
    """Raised when dataset loading or parsing fails."""

    pass


class MetricComputationError(RAGGuardianError):
    """Raised when metric computation fails."""

    pass


class IntegrationError(RAGGuardianError):
    """Raised when RAG system integration fails."""

    pass


class ValidationError(RAGGuardianError):
    """Raised when data validation fails."""

    pass


class PipelineError(RAGGuardianError):
    """Raised when evaluation pipeline execution fails."""

    pass
