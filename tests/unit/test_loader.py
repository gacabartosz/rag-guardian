"""Unit tests for DataLoader."""

import tempfile
from pathlib import Path

import pytest

from rag_guardian.core.loader import DataLoader
from rag_guardian.core.types import TestCase
from rag_guardian.exceptions import DatasetError


class TestDataLoader:
    """Tests for DataLoader."""

    def test_load_valid_jsonl(self):
        """Test loading valid JSONL file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as f:
            f.write('{"question": "Q1", "expected_answer": "A1"}\n')
            f.write('{"question": "Q2", "expected_answer": "A2", "metadata": {"cat": "test"}}\n')
            path = f.name

        try:
            test_cases = DataLoader.load_jsonl(path)

            assert len(test_cases) == 2
            assert test_cases[0].question == "Q1"
            assert test_cases[0].expected_answer == "A1"
            assert test_cases[1].question == "Q2"
            assert test_cases[1].metadata["cat"] == "test"
        finally:
            Path(path).unlink()

    def test_load_with_empty_lines(self):
        """Test loading JSONL with empty lines."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as f:
            f.write('{"question": "Q1"}\n')
            f.write('\n')  # Empty line
            f.write('{"question": "Q2"}\n')
            path = f.name

        try:
            test_cases = DataLoader.load_jsonl(path)
            assert len(test_cases) == 2
        finally:
            Path(path).unlink()

    def test_load_with_all_fields(self):
        """Test loading test case with all optional fields."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as f:
            f.write(
                '{"question": "Q", "expected_answer": "A", "expected_contexts": ["C1"], '
                '"acceptable_answers": ["A1", "A2"], "required_contexts": ["R1"], '
                '"forbidden_contexts": ["F1"], "metadata": {"key": "value"}}\n'
            )
            path = f.name

        try:
            test_cases = DataLoader.load_jsonl(path)

            assert len(test_cases) == 1
            tc = test_cases[0]
            assert tc.question == "Q"
            assert tc.expected_answer == "A"
            assert tc.expected_contexts == ["C1"]
            assert tc.acceptable_answers == ["A1", "A2"]
            assert tc.required_contexts == ["R1"]
            assert tc.forbidden_contexts == ["F1"]
            assert tc.metadata == {"key": "value"}
        finally:
            Path(path).unlink()

    def test_missing_file(self):
        """Test error when file doesn't exist."""
        with pytest.raises(DatasetError, match="Dataset file not found"):
            DataLoader.load_jsonl("/nonexistent/file.jsonl")

    def test_wrong_extension(self):
        """Test error for non-JSONL file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            path = f.name

        try:
            with pytest.raises(DatasetError, match="Expected .jsonl file"):
                DataLoader.load_jsonl(path)
        finally:
            Path(path).unlink()

    def test_invalid_json(self):
        """Test error on invalid JSON."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as f:
            f.write('{"question": "Q1"}\n')
            f.write('not valid json\n')
            path = f.name

        try:
            with pytest.raises(DatasetError, match="Invalid JSON on line 2"):
                DataLoader.load_jsonl(path)
        finally:
            Path(path).unlink()

    def test_missing_question_field(self):
        """Test error when question field is missing."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as f:
            f.write('{"expected_answer": "A"}\n')
            path = f.name

        try:
            with pytest.raises(DatasetError, match="Missing required field 'question'"):
                DataLoader.load_jsonl(path)
        finally:
            Path(path).unlink()

    def test_empty_file(self):
        """Test error on empty file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as f:
            path = f.name

        try:
            with pytest.raises(DatasetError, match="No valid test cases found"):
                DataLoader.load_jsonl(path)
        finally:
            Path(path).unlink()

    def test_save_jsonl(self):
        """Test saving test cases to JSONL."""
        test_cases = [
            TestCase(question="Q1", expected_answer="A1", metadata={"cat": "test"}),
            TestCase(
                question="Q2",
                expected_answer="A2",
                acceptable_answers=["A2", "A3"],
            ),
        ]

        with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as f:
            path = f.name

        try:
            DataLoader.save_jsonl(test_cases, path)

            # Verify saved content
            loaded = DataLoader.load_jsonl(path)
            assert len(loaded) == 2
            assert loaded[0].question == "Q1"
            assert loaded[0].metadata["cat"] == "test"
            assert loaded[1].acceptable_answers == ["A2", "A3"]
        finally:
            Path(path).unlink()

    def test_save_creates_directory(self):
        """Test that save creates parent directory if needed."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "subdir" / "test.jsonl"

            test_cases = [TestCase(question="Q1")]
            DataLoader.save_jsonl(test_cases, str(path))

            assert path.exists()
            loaded = DataLoader.load_jsonl(str(path))
            assert len(loaded) == 1
