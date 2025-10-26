"""Data loader for test cases."""

import json
from pathlib import Path
from typing import List

from rag_guardian.core.types import TestCase
from rag_guardian.exceptions import DatasetError


class DataLoader:
    """
    Loads test cases from JSONL files.

    JSONL format: one JSON object per line, each representing a test case.
    """

    @staticmethod
    def load_jsonl(file_path: str) -> List[TestCase]:
        """
        Load test cases from JSONL file.

        Args:
            file_path: Path to JSONL file

        Returns:
            List of TestCase objects

        Raises:
            DatasetError: If file doesn't exist or parsing fails
        """
        path = Path(file_path)

        if not path.exists():
            raise DatasetError(f"Dataset file not found: {file_path}")

        if path.suffix != ".jsonl":
            raise DatasetError(f"Expected .jsonl file, got: {path.suffix}")

        test_cases = []

        try:
            with open(path, "r", encoding="utf-8") as f:
                for line_num, line in enumerate(f, start=1):
                    line = line.strip()

                    if not line:  # Skip empty lines
                        continue

                    try:
                        data = json.loads(line)
                        test_case = DataLoader._parse_test_case(data, line_num)
                        test_cases.append(test_case)
                    except json.JSONDecodeError as e:
                        raise DatasetError(
                            f"Invalid JSON on line {line_num}: {str(e)}"
                        ) from e
                    except Exception as e:
                        raise DatasetError(
                            f"Error parsing test case on line {line_num}: {str(e)}"
                        ) from e

        except Exception as e:
            if isinstance(e, DatasetError):
                raise
            raise DatasetError(f"Error reading file {file_path}: {str(e)}") from e

        if not test_cases:
            raise DatasetError(f"No valid test cases found in {file_path}")

        return test_cases

    @staticmethod
    def _parse_test_case(data: dict, line_num: int) -> TestCase:
        """
        Parse a test case from JSON data.

        Args:
            data: Dictionary from JSON
            line_num: Line number (for error messages)

        Returns:
            TestCase object
        """
        # Required field
        if "question" not in data:
            raise DatasetError(f"Line {line_num}: Missing required field 'question'")

        # Create test case
        return TestCase(
            question=data["question"],
            expected_answer=data.get("expected_answer"),
            expected_contexts=data.get("expected_contexts"),
            metadata=data.get("metadata", {}),
            acceptable_answers=data.get("acceptable_answers"),
            required_contexts=data.get("required_contexts"),
            forbidden_contexts=data.get("forbidden_contexts"),
        )

    @staticmethod
    def save_jsonl(test_cases: List[TestCase], file_path: str) -> None:
        """
        Save test cases to JSONL file.

        Args:
            test_cases: List of TestCase objects
            file_path: Path where to save
        """
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        with open(path, "w", encoding="utf-8") as f:
            for test_case in test_cases:
                data = {
                    "question": test_case.question,
                    "expected_answer": test_case.expected_answer,
                    "expected_contexts": test_case.expected_contexts,
                    "metadata": test_case.metadata,
                }

                # Add optional fields if present
                if test_case.acceptable_answers:
                    data["acceptable_answers"] = test_case.acceptable_answers
                if test_case.required_contexts:
                    data["required_contexts"] = test_case.required_contexts
                if test_case.forbidden_contexts:
                    data["forbidden_contexts"] = test_case.forbidden_contexts

                f.write(json.dumps(data, ensure_ascii=False) + "\n")
