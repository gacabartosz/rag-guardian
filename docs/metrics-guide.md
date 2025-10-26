# Metrics Guide

This guide explains each metric in RAG Guardian and how to interpret results.

## Overview

RAG Guardian measures four core aspects of your RAG system:

1. **Faithfulness** - No hallucinations
2. **Groundedness** - Context usage
3. **Context Relevancy** - Retrieval quality
4. **Answer Correctness** - Accuracy

## Faithfulness

### What it measures
Are answers based only on retrieved context, or is the system making things up?

### How it works
1. Extract claims from the answer
2. Check each claim against retrieved contexts
3. Score = (supported claims) / (total claims)

### Example

**Context:** "Product costs $100"

**Answer:** "Product costs $100 and comes in 3 colors"

**Claims:**
- "costs $100" ✅ (supported)
- "comes in 3 colors" ❌ (not in context)

**Score:** 1/2 = 0.5

### Interpretation

- **0.9-1.0** - Excellent, no hallucinations
- **0.8-0.9** - Good, minor issues
- **0.6-0.8** - Fair, some hallucinations
- **< 0.6** - Poor, significant hallucinations

### Common issues

**Low score causes:**
- LLM adding information not in context
- Prompts encouraging elaboration
- Context missing key information

**How to fix:**
- Add "only use provided context" to prompt
- Improve retrieval to get complete context
- Use stricter generation temperature

## Groundedness

### What it measures
Does the answer actually use the context it retrieved?

### How it works
1. Identify key facts in retrieved contexts
2. Check which facts appear in answer
3. Score = (used facts) / (total relevant facts)

### Example

**Context:** "Company founded 1990. 500 employees. Located in Warsaw."

**Answer:** "Company was founded in 1990"

**Facts:**
- Founded 1990 ✅ (used)
- 500 employees ❌ (not used)
- Warsaw location ❌ (not used)

**Score:** 1/3 = 0.33

### Interpretation

- **0.8-1.0** - Excellent, comprehensive answers
- **0.6-0.8** - Good, uses most context
- **0.4-0.6** - Fair, misses some context
- **< 0.4** - Poor, ignores most context

### Common issues

**Low score causes:**
- Too much retrieved context
- Answer too brief
- Irrelevant context retrieved

**How to fix:**
- Improve retrieval precision
- Adjust answer length requirements
- Use reranking to filter context

## Context Relevancy

### What it measures
Is retrieval finding the right documents for the question?

### How it works
1. Measure similarity between question and each retrieved context
2. Score = average relevancy across all contexts

### Example

**Question:** "How do I reset my password?"

**Retrieved contexts:**
1. "Password reset: click forgot password" - Relevancy: 0.95
2. "Contact support at support@company.com" - Relevancy: 0.3
3. "Security best practices" - Relevancy: 0.4

**Score:** (0.95 + 0.3 + 0.4) / 3 = 0.55

### Interpretation

- **0.8-1.0** - Excellent retrieval
- **0.6-0.8** - Good, mostly relevant
- **0.4-0.6** - Fair, mixed results
- **< 0.4** - Poor, wrong documents

### Common issues

**Low score causes:**
- Poor embedding model
- Bad chunk size
- Sparse knowledge base

**How to fix:**
- Try better embedding model
- Adjust chunking strategy
- Improve document metadata
- Add hybrid search (keyword + semantic)

## Answer Correctness

### What it measures
Does the answer match what you expect (ground truth)?

### How it works
1. Compare semantic similarity with expected answer
2. Check factual overlap
3. Assess completeness

Formula: 0.5 × semantic + 0.3 × factual + 0.2 × completeness

### Example

**Expected:** "Returns accepted within 30 days"

**Generated:** "You can return items in 30 days"

- Semantic similarity: 0.92
- Factual overlap: 0.85
- Completeness: 0.90

**Score:** 0.5×0.92 + 0.3×0.85 + 0.2×0.90 = 0.895

### Interpretation

- **0.9-1.0** - Excellent match
- **0.8-0.9** - Good, minor differences
- **0.6-0.8** - Fair, some discrepancies
- **< 0.6** - Poor, wrong answer

### Common issues

**Low score causes:**
- Different wording (but same meaning)
- Incomplete answers
- Wrong information

**How to fix:**
- Enable fuzzy matching in config
- Provide multiple acceptable answers
- Improve generation prompt
- Fine-tune if using custom model

## Setting Thresholds

### Conservative (high quality requirements)
```yaml
metrics:
  faithfulness:
    threshold: 0.90
  groundedness:
    threshold: 0.85
  context_relevancy:
    threshold: 0.80
  answer_correctness:
    threshold: 0.85
```

### Balanced (production default)
```yaml
metrics:
  faithfulness:
    threshold: 0.85
  groundedness:
    threshold: 0.80
  context_relevancy:
    threshold: 0.75
  answer_correctness:
    threshold: 0.80
```

### Lenient (development/experimentation)
```yaml
metrics:
  faithfulness:
    threshold: 0.75
  groundedness:
    threshold: 0.70
  context_relevancy:
    threshold: 0.65
  answer_correctness:
    threshold: 0.70
```

## Metric Priority

Not all metrics are equally important. Suggested priorities:

1. **Faithfulness** (Critical) - Hallucinations are unacceptable
2. **Answer Correctness** (High) - Wrong answers hurt users
3. **Context Relevancy** (Medium) - Affects quality and cost
4. **Groundedness** (Medium) - Good to have, less critical

Configure in `.rag-guardian.yml`:

```yaml
metrics:
  faithfulness:
    threshold: 0.85
    required: true  # Fail if below threshold

  answer_correctness:
    threshold: 0.80
    required: true

  context_relevancy:
    threshold: 0.75
    required: false  # Warning only

  groundedness:
    threshold: 0.80
    required: false
```

## Debugging Low Scores

### Faithfulness issues
```bash
# Check which claims failed
rag-guardian test --dataset tests/cases.jsonl --verbose

# Review specific failure
rag-guardian report show results.json --failures-only
```

### Context Relevancy issues
```bash
# Inspect retrieved contexts
rag-guardian test --show-contexts

# Compare different embedding models
rag-guardian compare \
  --baseline results_minilm.json \
  --current results_openai.json \
  --metric context_relevancy
```

## Best Practices

1. **Start with smoke tests** - Small dataset, quick validation
2. **Set realistic thresholds** - Based on your baseline
3. **Monitor trends** - Watch for degradation over time
4. **Prioritize faithfulness** - Hallucinations are the worst
5. **Test incrementally** - After each change to embeddings/prompts

## Next Steps

- [Custom Metrics](custom-metrics.md) - Create domain-specific metrics
- [API Reference](api-reference.md) - Programmatic access
- [Getting Started](getting-started.md) - Setup guide
