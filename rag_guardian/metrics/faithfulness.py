"""Faithfulness metric implementation."""

import re
from typing import Dict, Any, List

from rag_guardian.core.types import RAGOutput, TestCase
from rag_guardian.metrics.base import BaseMetric


class FaithfulnessMetric(BaseMetric):
    """
    Measures if the answer is based only on retrieved context (no hallucinations).

    MVP implementation uses simple claim extraction and substring matching.
    Production should use LLM-as-judge for claim verification.
    """

    name = "faithfulness"

    def compute(self, test_case: TestCase, rag_output: RAGOutput) -> float:
        """
        Compute faithfulness score.

        Score = (claims supported by context) / (total claims)
        """
        # Extract claims from answer
        claims = self._extract_claims(rag_output.answer)

        if not claims:
            # No claims means nothing to verify - perfect score
            return 1.0

        # Check which claims are supported by contexts
        supported_claims = 0
        for claim in claims:
            if self._is_claim_supported(claim, rag_output.contexts):
                supported_claims += 1

        return supported_claims / len(claims)

    def _extract_claims(self, answer: str) -> List[str]:
        """
        Extract atomic claims from answer.

        MVP: Split by sentences.
        TODO: Use NLP for proper claim extraction.
        """
        # Split by common sentence delimiters
        sentences = re.split(r"[.!?]+", answer)

        # Clean and filter
        claims = [s.strip() for s in sentences if s.strip() and len(s.strip()) > 10]

        return claims

    def _is_claim_supported(self, claim: str, contexts: List[str]) -> bool:
        """
        Check if a claim is supported by any context.

        MVP: Simple substring matching.
        TODO: Use semantic similarity or LLM-as-judge.
        """
        claim_lower = claim.lower()

        # Check each context
        for context in contexts:
            context_lower = context.lower()

            # Simple keyword overlap check
            claim_words = set(claim_lower.split())
            context_words = set(context_lower.split())

            # If most claim words appear in context, consider it supported
            overlap = claim_words & context_words
            if len(overlap) / len(claim_words) > 0.6:  # 60% word overlap
                return True

        return False

    def _get_details(
        self, test_case: TestCase, rag_output: RAGOutput, score: float
    ) -> Dict[str, Any]:
        """Get details about faithfulness check."""
        claims = self._extract_claims(rag_output.answer)

        claim_support = []
        for claim in claims:
            supported = self._is_claim_supported(claim, rag_output.contexts)
            claim_support.append({"claim": claim, "supported": supported})

        return {
            "score": score,
            "threshold": self.threshold,
            "passed": score >= self.threshold,
            "total_claims": len(claims),
            "supported_claims": sum(1 for cs in claim_support if cs["supported"]),
            "claim_details": claim_support,
            "note": "MVP uses keyword matching. Upgrade to LLM-as-judge recommended.",
        }
