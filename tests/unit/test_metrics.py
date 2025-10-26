"""Unit tests for metrics."""

import pytest

from rag_guardian.core.types import TestCase, RAGOutput
from rag_guardian.metrics import (
    AnswerCorrectnessMetric,
    FaithfulnessMetric,
    GroundednessMetric,
    ContextRelevancyMetric,
)


class TestAnswerCorrectnessMetric:
    """Tests for answer correctness metric."""

    def test_perfect_match(self):
        """Test exact match returns 1.0."""
        metric = AnswerCorrectnessMetric(threshold=0.8)

        test_case = TestCase(
            question="What is 2+2?",
            expected_answer="4",
        )

        rag_output = RAGOutput(
            question="What is 2+2?",
            answer="4",
            contexts=["Math fact: 2+2=4"],
        )

        score = metric.compute(test_case, rag_output)
        assert score == 1.0

    def test_similar_answer(self):
        """Test similar answers get high score."""
        metric = AnswerCorrectnessMetric(threshold=0.8)

        test_case = TestCase(
            question="What is the return policy?",
            expected_answer="Returns within 30 days",
        )

        rag_output = RAGOutput(
            question="What is the return policy?",
            answer="You can return items within 30 days",
            contexts=["Policy: 30 day returns"],
        )

        score = metric.compute(test_case, rag_output)
        assert score > 0.5  # Should have decent overlap

    def test_no_expected_answer(self):
        """Test when no expected answer provided."""
        metric = AnswerCorrectnessMetric(threshold=0.8)

        test_case = TestCase(question="What is RAG?")

        rag_output = RAGOutput(
            question="What is RAG?",
            answer="Retrieval-Augmented Generation",
            contexts=["RAG is a technique..."],
        )

        score = metric.compute(test_case, rag_output)
        assert score == 1.0  # No answer to compare = pass


class TestFaithfulnessMetric:
    """Tests for faithfulness metric."""

    def test_faithful_answer(self):
        """Test answer based on context gets high score."""
        metric = FaithfulnessMetric(threshold=0.8)

        test_case = TestCase(question="What is the price?")

        rag_output = RAGOutput(
            question="What is the price?",
            answer="The product costs $100",
            contexts=["Price: $100"],
        )

        score = metric.compute(test_case, rag_output)
        assert score >= 0.8

    def test_hallucination(self):
        """Test answer with hallucinations gets low score."""
        metric = FaithfulnessMetric(threshold=0.8)

        test_case = TestCase(question="What is the price?")

        rag_output = RAGOutput(
            question="What is the price?",
            answer="The product costs $100 and comes in 5 colors and is waterproof",
            contexts=["Price: $100"],
        )

        score = metric.compute(test_case, rag_output)
        # Should detect unsupported claims
        assert score < 1.0


class TestGroundednessMetric:
    """Tests for groundedness metric."""

    def test_uses_context(self):
        """Test answer using context terms gets high score."""
        metric = GroundednessMetric(threshold=0.7)

        test_case = TestCase(question="What is Python?")

        rag_output = RAGOutput(
            question="What is Python?",
            answer="Python is a programming language created by Guido",
            contexts=["Python is a programming language created by Guido van Rossum"],
        )

        score = metric.compute(test_case, rag_output)
        assert score > 0.5

    def test_ignores_context(self):
        """Test answer ignoring context gets low score."""
        metric = GroundednessMetric(threshold=0.7)

        test_case = TestCase(question="What is the price?")

        rag_output = RAGOutput(
            question="What is the price?",
            answer="I don't know",
            contexts=["Price: $100", "Available colors: red, blue, green"],
        )

        score = metric.compute(test_case, rag_output)
        # Should be low since answer doesn't use context terms
        assert score < 0.5


class TestContextRelevancyMetric:
    """Tests for context relevancy metric."""

    def test_relevant_context(self):
        """Test relevant context gets high score."""
        metric = ContextRelevancyMetric(threshold=0.75)

        test_case = TestCase(question="How do I reset my password?")

        rag_output = RAGOutput(
            question="How do I reset my password?",
            answer="Click forgot password",
            contexts=["To reset password, click forgot password link"],
        )

        score = metric.compute(test_case, rag_output)
        assert score > 0.5

    def test_irrelevant_context(self):
        """Test irrelevant context gets low score."""
        metric = ContextRelevancyMetric(threshold=0.75)

        test_case = TestCase(question="How do I reset my password?")

        rag_output = RAGOutput(
            question="How do I reset my password?",
            answer="Contact support",
            contexts=["We offer 24/7 customer service"],
        )

        score = metric.compute(test_case, rag_output)
        # Context doesn't mention password or reset
        assert score < 0.7
