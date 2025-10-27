"""Answer correctness metric implementation."""

from typing import Any

from rag_guardian.core.types import RAGOutput, TestCase
from rag_guardian.metrics.base import BaseMetric


class AnswerCorrectnessMetric(BaseMetric):
    """
    Measures how well the generated answer matches the expected answer.

    Uses a simple string similarity approach for MVP.
    In production, this should use semantic similarity with embeddings.
    """

    name = "answer_correctness"

    def compute(self, test_case: TestCase, rag_output: RAGOutput) -> float:
        """
        Compute answer correctness score.

        For MVP: Simple token overlap and length-based scoring.
        TODO: Upgrade to semantic similarity with embeddings.
        """
        if not test_case.expected_answer:
            # No expected answer to compare against
            return 1.0

        generated = rag_output.answer.lower().strip()
        expected = test_case.expected_answer.lower().strip()

        # Check acceptable answers list
        if test_case.acceptable_answers:
            scores = [
                self._compute_similarity(generated, answer.lower().strip())
                for answer in test_case.acceptable_answers
            ]
            return max(scores)

        return self._compute_similarity(generated, expected)

    def _compute_similarity(self, generated: str, expected: str) -> float:
        """
        Compute similarity between two strings.

        MVP implementation using token overlap.
        """
        if generated == expected:
            return 1.0

        # Tokenize
        generated_tokens = set(generated.split())
        expected_tokens = set(expected.split())

        if not expected_tokens:
            return 0.0

        # Jaccard similarity (token overlap)
        intersection = generated_tokens & expected_tokens
        union = generated_tokens | expected_tokens

        if not union:
            return 0.0

        jaccard = len(intersection) / len(union)

        # Length similarity (completeness check)
        len_ratio = min(len(generated), len(expected)) / max(len(generated), len(expected))

        # Combined score (favor jaccard more)
        score = 0.7 * jaccard + 0.3 * len_ratio

        return min(score, 1.0)

    def _get_details(
        self, test_case: TestCase, rag_output: RAGOutput, score: float
    ) -> dict[str, Any]:
        """Get details about the comparison."""
        return {
            "score": score,
            "threshold": self.threshold,
            "passed": score >= self.threshold,
            "generated_answer": rag_output.answer,
            "expected_answer": test_case.expected_answer,
            "note": "MVP uses token overlap. Upgrade to semantic similarity recommended.",
        }
