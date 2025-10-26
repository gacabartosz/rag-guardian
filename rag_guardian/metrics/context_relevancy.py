"""Context relevancy metric implementation."""

from typing import Dict, Any, List

from rag_guardian.core.types import RAGOutput, TestCase
from rag_guardian.metrics.base import BaseMetric


class ContextRelevancyMetric(BaseMetric):
    """
    Measures if retrieved contexts are relevant to the question.

    Checks if contexts contain information related to the question.
    """

    name = "context_relevancy"

    def compute(self, test_case: TestCase, rag_output: RAGOutput) -> float:
        """
        Compute context relevancy score.

        Score = average relevancy of each context to the question
        """
        if not rag_output.contexts:
            return 0.0

        # Compute relevancy for each context
        relevancy_scores = [
            self._compute_relevancy(test_case.question, context)
            for context in rag_output.contexts
        ]

        # Return average
        return sum(relevancy_scores) / len(relevancy_scores)

    def _compute_relevancy(self, question: str, context: str) -> float:
        """
        Compute how relevant a context is to the question.

        MVP: Keyword overlap-based similarity.
        TODO: Use semantic similarity with embeddings.
        """
        question_lower = question.lower()
        context_lower = context.lower()

        # Extract meaningful words from question
        question_words = set(
            w for w in question_lower.split() if len(w) > 3 and w.isalnum()
        )

        if not question_words:
            return 0.5  # Neutral score if no meaningful words

        # Count how many question keywords appear in context
        matches = sum(1 for word in question_words if word in context_lower)

        # Score based on keyword coverage
        coverage = matches / len(question_words)

        # Boost score if context is not too long (more focused)
        context_length = len(context.split())
        length_penalty = 1.0 if context_length < 200 else 0.9

        return min(coverage * length_penalty, 1.0)

    def _get_details(
        self, test_case: TestCase, rag_output: RAGOutput, score: float
    ) -> Dict[str, Any]:
        """Get details about context relevancy."""
        context_scores = []

        for i, context in enumerate(rag_output.contexts):
            relevancy = self._compute_relevancy(test_case.question, context)
            context_scores.append(
                {
                    "context_index": i,
                    "relevancy_score": relevancy,
                    "context_preview": context[:100] + "..."
                    if len(context) > 100
                    else context,
                }
            )

        return {
            "score": score,
            "threshold": self.threshold,
            "passed": score >= self.threshold,
            "num_contexts": len(rag_output.contexts),
            "context_scores": context_scores,
            "note": "MVP uses keyword matching. Upgrade to semantic embeddings recommended.",
        }
