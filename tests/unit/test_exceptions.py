"""Unit tests for custom exceptions."""

import pytest

from rag_guardian.exceptions import (
    ConfigurationError,
    DatasetError,
    IntegrationError,
    MetricComputationError,
    PipelineError,
    RAGGuardianError,
    ValidationError,
)


class TestExceptionHierarchy:
    """Test exception inheritance and hierarchy."""

    def test_base_exception(self):
        """Test RAGGuardianError is base exception."""
        error = RAGGuardianError("base error")
        assert str(error) == "base error"
        assert isinstance(error, Exception)

    def test_configuration_error_inherits_base(self):
        """Test ConfigurationError inherits from RAGGuardianError."""
        error = ConfigurationError("config error")
        assert isinstance(error, RAGGuardianError)
        assert isinstance(error, Exception)

    def test_dataset_error_inherits_base(self):
        """Test DatasetError inherits from RAGGuardianError."""
        error = DatasetError("dataset error")
        assert isinstance(error, RAGGuardianError)

    def test_metric_computation_error_inherits_base(self):
        """Test MetricComputationError inherits from RAGGuardianError."""
        error = MetricComputationError("metric error")
        assert isinstance(error, RAGGuardianError)

    def test_integration_error_inherits_base(self):
        """Test IntegrationError inherits from RAGGuardianError."""
        error = IntegrationError("integration error")
        assert isinstance(error, RAGGuardianError)

    def test_validation_error_inherits_base(self):
        """Test ValidationError inherits from RAGGuardianError."""
        error = ValidationError("validation error")
        assert isinstance(error, RAGGuardianError)

    def test_pipeline_error_inherits_base(self):
        """Test PipelineError inherits from RAGGuardianError."""
        error = PipelineError("pipeline error")
        assert isinstance(error, RAGGuardianError)


class TestExceptionCatching:
    """Test exception catching patterns."""

    def test_catch_specific_exception(self):
        """Test catching specific exception type."""
        with pytest.raises(DatasetError, match="specific error"):
            raise DatasetError("specific error")

    def test_catch_base_exception(self):
        """Test catching via base exception."""
        with pytest.raises(RAGGuardianError):
            raise ConfigurationError("config error")

    def test_catch_any_rag_guardian_error(self):
        """Test that all custom exceptions can be caught as RAGGuardianError."""
        exceptions = [
            ConfigurationError("test"),
            DatasetError("test"),
            MetricComputationError("test"),
            IntegrationError("test"),
            ValidationError("test"),
            PipelineError("test"),
        ]

        for exc in exceptions:
            with pytest.raises(RAGGuardianError):
                raise exc


class TestExceptionUsage:
    """Test typical exception usage patterns."""

    def test_configuration_error_usage(self):
        """Test ConfigurationError in typical usage."""

        def load_config(path: str):
            if not path:
                raise ConfigurationError("Config path cannot be empty")
            return {}

        with pytest.raises(ConfigurationError, match="cannot be empty"):
            load_config("")

    def test_dataset_error_usage(self):
        """Test DatasetError in typical usage."""

        def load_dataset(path: str):
            if not path.endswith(".jsonl"):
                raise DatasetError(f"Expected .jsonl file, got: {path}")
            return []

        with pytest.raises(DatasetError, match="Expected .jsonl"):
            load_dataset("file.json")

    def test_metric_computation_error_usage(self):
        """Test MetricComputationError in typical usage."""

        def compute_metric(value: float):
            if value < 0 or value > 1:
                raise MetricComputationError(
                    f"Metric value must be between 0 and 1, got {value}"
                )
            return value

        with pytest.raises(MetricComputationError, match="between 0 and 1"):
            compute_metric(1.5)

    def test_integration_error_usage(self):
        """Test IntegrationError in typical usage."""

        def execute_rag(adapter):
            if adapter is None:
                raise IntegrationError("RAG adapter cannot be None")
            return {}

        with pytest.raises(IntegrationError, match="cannot be None"):
            execute_rag(None)

    def test_pipeline_error_usage(self):
        """Test PipelineError in typical usage."""

        def run_pipeline(test_cases):
            if not test_cases:
                raise PipelineError("Cannot evaluate empty dataset")
            return {}

        with pytest.raises(PipelineError, match="empty dataset"):
            run_pipeline([])

    def test_validation_error_usage(self):
        """Test ValidationError in typical usage."""

        def validate_test_case(test_case):
            if not test_case.get("question"):
                raise ValidationError("Test case must have a question")
            return test_case

        with pytest.raises(ValidationError, match="must have a question"):
            validate_test_case({})


class TestExceptionChaining:
    """Test exception chaining with 'from'."""

    def test_chain_exceptions(self):
        """Test chaining exceptions for better error context."""

        def inner_function():
            raise ValueError("Original error")

        def outer_function():
            try:
                inner_function()
            except ValueError as e:
                raise DatasetError("Failed to load dataset") from e

        with pytest.raises(DatasetError) as exc_info:
            outer_function()

        assert exc_info.value.__cause__ is not None
        assert isinstance(exc_info.value.__cause__, ValueError)
        assert str(exc_info.value.__cause__) == "Original error"


class TestExceptionMessages:
    """Test exception message formatting."""

    def test_detailed_error_messages(self):
        """Test that exceptions can carry detailed messages."""
        error_details = {
            "file": "test.jsonl",
            "line": 42,
            "error": "Invalid JSON",
        }

        error = DatasetError(
            f"Parse error at {error_details['file']}:{error_details['line']}: "
            f"{error_details['error']}"
        )

        assert "test.jsonl" in str(error)
        assert "42" in str(error)
        assert "Invalid JSON" in str(error)

    def test_multiline_error_messages(self):
        """Test exceptions with multiline messages."""
        message = """
        Configuration validation failed:
        - Missing required field: 'rag_system.endpoint'
        - Invalid threshold: faithfulness.threshold must be between 0 and 1
        """

        error = ConfigurationError(message)
        assert "Missing required field" in str(error)
        assert "Invalid threshold" in str(error)
