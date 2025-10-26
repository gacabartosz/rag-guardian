"""Groundedness metric implementation."""

from typing import Dict, Any, List, Set

from rag_guardian.core.types import RAGOutput, TestCase
from rag_guardian.metrics.base import BaseMetric


class GroundednessMetric(BaseMetric):
    """
    Measures if the answer actually uses the retrieved context.

    Checks what percentage of context facts appear in the answer.
    """

    name = "groundedness"

    def compute(self, test_case: TestCase, rag_output: RAGOutput) -> float:
        """
        Compute groundedness score.

        Score = (context facts used in answer) / (total context facts)
        """
        # Extract key terms from contexts
        context_terms = self._extract_key_terms(rag_output.contexts)

        if not context_terms:
            # No context means nothing to ground on
            return 1.0

        # Check which terms appear in answer
        answer_lower = rag_output.answer.lower()
        used_terms = sum(1 for term in context_terms if term in answer_lower)

        return used_terms / len(context_terms)

    def _extract_key_terms(self, contexts: List[str]) -> Set[str]:
        """
        Extract key terms from contexts.

        MVP: Extract meaningful words (filter common words).
        TODO: Use TF-IDF or named entity recognition.
        """
        # Common stop words to filter
        stop_words = {
            "the",
            "a",
            "an",
            "and",
            "or",
            "but",
            "in",
            "on",
            "at",
            "to",
            "for",
            "of",
            "with",
            "by",
            "from",
            "is",
            "are",
            "was",
            "were",
            "be",
            "been",
            "being",
            "have",
            "has",
            "had",
            "do",
            "does",
            "did",
            "will",
            "would",
            "could",
            "should",
            "may",
            "might",
            "can",
            "this",
            "that",
            "these",
            "those",
        }

        key_terms = set()

        for context in contexts:
            words = context.lower().split()
            # Keep words longer than 3 chars that aren't stop words
            meaningful_words = [w for w in words if len(w) > 3 and w not in stop_words]
            key_terms.update(meaningful_words)

        return key_terms

    def _get_details(
        self, test_case: TestCase, rag_output: RAGOutput, score: float
    ) -> Dict[str, Any]:
        """Get details about groundedness check."""
        context_terms = self._extract_key_terms(rag_output.contexts)
        answer_lower = rag_output.answer.lower()

        used_terms = [term for term in context_terms if term in answer_lower]
        unused_terms = [term for term in context_terms if term not in answer_lower]

        return {
            "score": score,
            "threshold": self.threshold,
            "passed": score >= self.threshold,
            "total_key_terms": len(context_terms),
            "used_terms_count": len(used_terms),
            "sample_used_terms": list(used_terms)[:10],
            "sample_unused_terms": list(unused_terms)[:10],
            "note": "MVP uses keyword extraction. Upgrade to NER/TF-IDF recommended.",
        }
