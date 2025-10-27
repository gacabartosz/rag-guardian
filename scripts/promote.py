#!/usr/bin/env python3
"""
RAG Guardian - Automated Promotion Script
Generuje content do promocji projektu na różnych platformach.

Usage:
    python scripts/promote.py --platform twitter
    python scripts/promote.py --platform all
    python scripts/promote.py --submit  # Lista miejsc do zgłoszenia
"""

import argparse
import json
from datetime import datetime
from pathlib import Path


class PromotionGenerator:
    """Generator contentу promocyjnego dla RAG Guardian."""

    def __init__(self):
        self.project_name = "RAG Guardian"
        self.tagline = "Przestań zgadywać czy twój RAG działa. Przetestuj go."
        self.repo_url = "https://github.com/gacabartosz/rag-guardian"
        self.pypi_url = "https://pypi.org/project/rag-guardian/"
        self.website = "https://bartoszgaca.pl"

        # Metryki projektu
        self.stats = {
            "tests": 119,
            "coverage": 68,
            "frameworks": ["LangChain", "LlamaIndex"],
            "metrics": 4,
            "version": "1.0.0"
        }

    def generate_twitter_thread(self):
        """Thread na Twitter/X (seria tweetów)."""
        tweets = [
            # Tweet 1 - Hook
            f"""🚀 RAG Guardian v1.0 - pytest dla systemów RAG

Wdrażasz RAG do produkcji i zastanawiasz się "czy to czasem nie halucynuje?"

Teraz możesz to PRZETESTOWAĆ zanim klient zobaczy błąd.

Thread 🧵👇""",

            # Tweet 2 - Problem
            """Problem który znam z autopsji:

❌ 2h ręcznego sprawdzania przed każdym release
❌ "Coś nie gra" ale nie wiesz co
❌ Klient zgłasza bug na prodzie

Brzmi znajomo?""",

            # Tweet 3 - Rozwiązanie
            f"""Rozwiązanie → automatyczne testy RAG:

✅ 4 metryki (faithfulness, groundedness, relevancy, correctness)
✅ 5 minut zamiast 2h
✅ Raport HTML do pokazania szefowi
✅ CI/CD - blokuje merge jak testy failują

{self.repo_url}""",

            # Tweet 4 - Jak działa
            """Jak to działa? 3 komendy:

```bash
pip install rag-guardian
rag-guardian init
rag-guardian test --dataset tests.jsonl
```

Dostajesz DOKŁADNIE co się zepsuło.
Nie "coś nie gra" - konkretne "context_relevancy: 0.68 < 0.75" ⬅️ FIX THIS""",

            # Tweet 5 - Integracje
            """Działa z:
• LangChain (3 linijki kodu)
• LlamaIndex (3 adaptery)
• Custom RAG (dziedzicz CustomRAGAdapter)
• HTTP API (adapter z auto-retry)

Nie musisz zmieniać swojego kodu.
Opakowujesz w adapter, uruchamiasz testy. Done.""",

            # Tweet 6 - Stats
            f"""Stats które pokazują że to działa:

• {self.stats['tests']} testów passing
• {self.stats['coverage']}% code coverage
• Battle-tested w prawdziwych projektach
• Open-source, MIT, free forever

{self.repo_url}""",

            # Tweet 7 - CTA
            f"""Jeśli budujesz systemy RAG i masz dość zgadywania:

⭐ Star na GitHubie jeśli to ma sens
📦 pip install rag-guardian
💬 Issues/PRs welcome

Real-world ROI: 1 bug złapany przed prod = kilka godzin saved.

{self.repo_url}"""
        ]

        return tweets

    def generate_linkedin_post(self):
        """Post na LinkedIn (długi format)."""
        return f"""🚀 Czy Twój system RAG faktycznie działa? A może halucynuje i nie wiesz o tym?

Właśnie wypuściłem RAG Guardian v1.0 - open-source narzędzie do testowania jakości systemów RAG.

🎯 PROBLEM KTÓRY TO ROZWIĄZUJE:

Wdrażasz RAG do produkcji. Wszystko działa... ale:
• Czy model czasami nie halucynuje?
• Czy używa właściwych dokumentów?
• Czy retrieval znajduje to co powinien?

Dotychczas: ręczne sprawdzanie, 2h przed każdym release, modlitwa 🙏

💡 ROZWIĄZANIE:

Automatyczne testy jakości - tak jak pytest dla kodu, ale dla RAG-ów.

Setup w 3 komendy:
```
pip install rag-guardian
rag-guardian init
rag-guardian test --dataset tests.jsonl
```

Dostajesz:
✅ 4 metryki (faithfulness, groundedness, relevancy, correctness)
✅ Raport HTML który możesz pokazać szefowi
✅ Integracja CI/CD - testy blokują merge
✅ Oszczędność czasu: 2h → 5 minut

📊 METRYKI:

• {self.stats['tests']} testów passing
• {self.stats['coverage']}% code coverage
• LangChain + LlamaIndex support out-of-the-box
• Custom RAG? 3 metody do implementacji

🔧 REAL-WORLD EXAMPLE:

E-commerce customer support RAG (100+ FAQs):
1. Developer zmienia prompt template
2. Push do GitHub
3. GitHub Actions uruchamia rag-guardian test
4. Test failuje - faithfulness spadło 0.91 → 0.78
5. PR dostaje ❌ - nie można merge'ować
6. Developer poprawia
7. Test pass → merge → deploy

ROI: Jeden bug złapany przed prod = kilka godzin saved na debugging i hotfix.

🌟 DOSTĘPNE TERAZ:

• GitHub: {self.repo_url}
• PyPI: pip install rag-guardian
• Open-source, MIT license
• Dokumentacja + examples included

Jeśli budujesz systemy RAG i chcesz przestać zgadywać czy działają - sprawdź to.

#AI #MachineLearning #RAG #Python #OpenSource #Testing #DevOps #LLM

---

Made by Bartosz Gaca | AI & Automation Strategist | {self.website}
"""

    def generate_reddit_posts(self):
        """Posty na różne subreddity."""
        posts = {
            "r/MachineLearning": {
                "title": "[P] RAG Guardian - Automated Testing Framework for RAG Systems",
                "body": f"""**TL;DR:** Open-source tool to test RAG quality before production. Like pytest but for RAG systems. {self.stats['tests']} tests, {self.stats['coverage']}% coverage, LangChain + LlamaIndex support.

**Problem:**

Deploying RAG systems is scary. You test manually, push to prod, and hope it doesn't hallucinate. When it does, you find out from users.

**Solution:**

Automated RAG quality tests with clear metrics:
- **Faithfulness** - Is the model making stuff up?
- **Groundedness** - Is it using retrieved context?
- **Context Relevancy** - Is retrieval finding the right docs?
- **Answer Correctness** - Does it match expected answers?

**Quick Start:**

```bash
pip install rag-guardian
rag-guardian init
rag-guardian test --dataset tests.jsonl
```

**Features:**

- Works with LangChain, LlamaIndex, or custom RAG
- HTML + JSON reports
- CI/CD integration (GitHub Actions examples included)
- {self.stats['tests']} passing tests, {self.stats['coverage']}% coverage

**Example Output:**

```
✅ faithfulness        : 0.92 (threshold: 0.85)
✅ groundedness        : 0.88 (threshold: 0.80)
❌ context_relevancy   : 0.68 (threshold: 0.75)  ← FIX THIS
✅ answer_correctness  : 0.90 (threshold: 0.80)
```

**Links:**

- GitHub: {self.repo_url}
- PyPI: {self.pypi_url}
- License: MIT (free forever)

**Looking for feedback** on the metrics implementation and what features would be most useful for v1.1.

Currently using keyword matching (fast, ~80-85% accuracy). Planning semantic similarity with embeddings for v1.1 (~90-95% accuracy but slower).

What would you prioritize?
"""
            },

            "r/Python": {
                "title": "RAG Guardian - Testing framework for RAG systems (LangChain, LlamaIndex)",
                "body": f"""Built this tool to solve a problem I had: testing RAG quality before production.

**What it does:**

Tests your RAG system like pytest tests your code. You give it test cases (questions + expected answers), it runs them, gives you pass/fail with metrics.

**Example:**

```python
from rag_guardian import Evaluator, TestCase

tests = [
    TestCase(
        question="What's your return policy?",
        expected_answer="30 days, no questions asked"
    )
]

evaluator = Evaluator.from_config(".rag-guardian.yml")
results = evaluator.evaluate_dataset(tests)

if not results.passed:
    print(f"Failed {{results.failed_tests}} tests")
    exit(1)
```

**Integrations:**

Works with LangChain and LlamaIndex out of the box. Custom RAG? Implement 2 methods (`retrieve` and `generate`).

**Stats:**

- {self.stats['tests']} tests passing
- {self.stats['coverage']}% code coverage
- Full CI/CD support
- HTML + JSON reports

**Links:**

- Repo: {self.repo_url}
- Install: `pip install rag-guardian`

Open to feedback and PRs!
"""
            },

            "r/LangChain": {
                "title": "Testing RAG quality with LangChain - automated framework",
                "body": f"""If you're building RAG with LangChain and wondering how to test it before production, check this out.

**Problem:** Manual testing is time-consuming and you still miss edge cases.

**Solution:** Automated tests with metrics (faithfulness, groundedness, etc.)

**Integration (3 lines):**

```python
from langchain.chains import RetrievalQA
from rag_guardian.integrations import LangChainAdapter

qa_chain = RetrievalQA.from_chain_type(...)  # Your existing chain

adapter = LangChainAdapter(qa_chain)
evaluator = Evaluator(adapter)
results = evaluator.evaluate_dataset("tests.jsonl")
```

**What it tests:**

- Faithfulness (hallucinations)
- Groundedness (using context)
- Context relevancy (retrieval quality)
- Answer correctness (vs expected)

**Output:** HTML report + JSON for CI/CD

GitHub: {self.repo_url}
PyPI: `pip install rag-guardian`

{self.stats['tests']} tests, {self.stats['coverage']}% coverage, MIT license.

Feedback welcome!
"""
            }
        }

        return posts

    def generate_devto_article(self):
        """Artykuł na Dev.to (długi format)."""
        return f"""---
title: Stop Guessing if Your RAG Works - Test It Like Code
published: true
description: Open-source framework to automatically test RAG system quality before production
tags: ai, python, testing, opensource
cover_image: https://github.com/gacabartosz/rag-guardian/raw/main/assets/cover.png
---

## The Problem

You've built a RAG system. It answers questions. Sometimes it hallucinates. Sometimes retrieval finds wrong docs. You test manually before each release.

**2 hours of manual testing. Every. Single. Time.**

And you still miss bugs. Clients report "weird answers" in production.

Sound familiar?

## The Solution

**Automated RAG quality tests.** Like pytest for your code, but for RAG systems.

## RAG Guardian - Quick Start

```bash
pip install rag-guardian
rag-guardian init
rag-guardian test --dataset tests/cases.jsonl
```

**Output:**

```
============================================================
RAG GUARDIAN - EVALUATION SUMMARY
============================================================

Overall Status: ❌ FAILED (2/20 tests failed)
Pass Rate: 90.0%

METRICS:
✅ faithfulness        : 0.92 (threshold: 0.85)
✅ groundedness        : 0.88 (threshold: 0.80)
❌ context_relevancy   : 0.68 (threshold: 0.75)  ← FIX THIS
✅ answer_correctness  : 0.90 (threshold: 0.80)

FAILED TESTS:
1. "What's the shipping time?" - retrieval failed (score: 0.68)
2. "Can I cancel my order?" - wrong answer (score: 0.65)
============================================================
```

**Now you know EXACTLY what to fix.**

No more "something's off but I don't know what."

## What It Tests (4 Metrics)

### 1. Faithfulness (0-1)

Is your RAG making stuff up? Or is the answer grounded in the context?

**Example fail:** RAG says "free shipping worldwide" but context only mentions "free shipping in US."

### 2. Groundedness (0-1)

Is it actually using the retrieved documents? Or improvising?

**Example fail:** Retrieved 5 docs about returns, but answer talks about shipping.

### 3. Context Relevancy (0-1)

Is retrieval finding the RIGHT documents?

**Example fail:** Question "What's your return policy?" retrieves docs about shipping policy.

### 4. Answer Correctness (0-1)

Does the answer match your expected answer?

**Example fail:** Expected "30 days" got "14 days"

## Real-World Example: E-commerce Support

**Setup:**
- RAG on 100+ FAQ docs
- 50 test cases with expected answers
- Threshold: 0.85 for all metrics

**Workflow:**

1. Developer changes prompt template
2. Push to GitHub
3. GitHub Actions runs `rag-guardian test`
4. Test fails - faithfulness drops 0.91 → 0.78
5. PR gets ❌ - can't merge
6. Developer fixes prompt
7. Test passes → merge → deploy

**ROI:** One bug caught before prod = hours saved on debugging and hotfix.

## Integrations

### LangChain (3 lines)

```python
from langchain.chains import RetrievalQA
from rag_guardian.integrations import LangChainAdapter

qa_chain = RetrievalQA.from_chain_type(...)  # Your existing chain

adapter = LangChainAdapter(qa_chain)
evaluator = Evaluator(adapter)
results = evaluator.evaluate_dataset("tests.jsonl")
```

### LlamaIndex (3 adapters)

```python
from rag_guardian.integrations import LlamaIndexVectorStoreAdapter

index = VectorStoreIndex.from_documents(documents)

adapter = LlamaIndexVectorStoreAdapter(index, similarity_top_k=3)
evaluator = Evaluator(adapter)
results = evaluator.evaluate_dataset("tests.jsonl")
```

**Other adapters:**
- `LlamaIndexAdapter` - for any QueryEngine
- `LlamaIndexChatEngineAdapter` - for chat RAG

### Custom RAG

```python
from rag_guardian.integrations import CustomRAGAdapter

class MyRAG(CustomRAGAdapter):
    def retrieve(self, query: str) -> List[str]:
        return self.vector_db.search(query, top_k=5)

    def generate(self, query: str, contexts: List[str]) -> str:
        return self.llm.generate(f"Context: {{contexts}}\\n\\nQ: {{query}}")

evaluator = Evaluator(MyRAG())
```

## Python API (10 lines)

```python
from rag_guardian import Evaluator, TestCase

tests = [
    TestCase(
        question="What's your return policy?",
        expected_answer="30 days, no questions asked"
    ),
    TestCase(
        question="Do you ship internationally?",
        expected_answer="Yes, to 50+ countries"
    )
]

evaluator = Evaluator.from_config(".rag-guardian.yml")
results = evaluator.evaluate_dataset(tests)

if results.passed:
    print("✅ All good - ship it!")
else:
    print(f"❌ {{results.failed_tests}} tests failed - fix before deploy")
```

## CI/CD Integration

GitHub Actions example:

```yaml
name: RAG Quality Tests

on:
  pull_request:
    branches: [ main ]

jobs:
  test-rag:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install RAG Guardian
        run: pip install rag-guardian

      - name: Run tests
        run: rag-guardian test --dataset tests/cases.jsonl
```

**Result:** Every PR automatically tested. Can't merge until RAG passes tests.

## Stats

- ✅ {self.stats['tests']} tests passing
- ✅ {self.stats['coverage']}% code coverage
- ✅ LangChain + LlamaIndex support
- ✅ HTML + JSON reports
- ✅ Battle-tested in real projects
- ✅ Open-source, MIT license

## Roadmap

**v1.1 (January 2025):**
- Semantic similarity with embeddings (better accuracy)
- Baseline comparison (track changes over time)
- Slack notifications

**v1.5 (Q1 2025):**
- Performance metrics (latency, token usage)
- Batch processing (500+ cases in parallel)
- SQL storage

**v2.0 (Q2 2025):**
- Production monitoring
- Web dashboard
- LLM-as-judge evaluation

## Links

- **GitHub:** {self.repo_url}
- **PyPI:** `pip install rag-guardian`
- **Docs:** Full README with examples
- **License:** MIT - free forever

## Conclusion

If you're building RAG systems and tired of guessing if they work - try this.

**Time saved:** 2h manual testing → 5 min automated tests.

**Bugs caught:** Before production, not after.

**Cost:** €0. Open-source.

⭐ Star on GitHub if this makes sense: {self.repo_url}

---

*Made by [Bartosz Gaca]({self.website}) | AI & Automation Strategist*
"""

    def generate_submission_list(self):
        """Lista miejsc gdzie zgłosić projekt."""
        submissions = {
            "Agregatory projektów": [
                {
                    "name": "Hacker News (Show HN)",
                    "url": "https://news.ycombinator.com/submit",
                    "title": "Show HN: RAG Guardian – pytest for RAG systems",
                    "tips": "Post rano US time (9-11am EST). Odpowiadaj na komentarze szybko.",
                    "priority": "🔥 HIGH"
                },
                {
                    "name": "Product Hunt",
                    "url": "https://www.producthunt.com/posts/new",
                    "title": "RAG Guardian - Test your RAG before production",
                    "tips": "Launch w środę/czwartek. Przygotuj tagline, screenshots, demo video.",
                    "priority": "🔥 HIGH"
                },
                {
                    "name": "Indie Hackers",
                    "url": "https://www.indiehackers.com/post/new",
                    "title": "Built RAG Guardian - testing framework for RAG systems",
                    "tips": "Share journey, numbers, lessons learned. Community lubi personal stories.",
                    "priority": "⭐ MEDIUM"
                },
                {
                    "name": "Lobsters",
                    "url": "https://lobste.rs/",
                    "title": "RAG Guardian: Testing framework for RAG systems",
                    "tips": "Tag: 'python', 'ai'. Technical audience, appreciate quality code.",
                    "priority": "⭐ MEDIUM"
                }
            ],

            "Reddit": [
                {
                    "name": "r/MachineLearning",
                    "url": "https://reddit.com/r/MachineLearning/submit",
                    "title": "[P] RAG Guardian - Testing framework for RAG systems",
                    "tips": "Tag [P] for Project. Technical details, benchmarks. Monday-Wednesday best.",
                    "priority": "🔥 HIGH"
                },
                {
                    "name": "r/Python",
                    "url": "https://reddit.com/r/Python/submit",
                    "title": "RAG Guardian - Testing framework for RAG systems",
                    "tips": "Show code examples, API design. Community values Pythonic code.",
                    "priority": "🔥 HIGH"
                },
                {
                    "name": "r/LangChain",
                    "url": "https://reddit.com/r/LangChain/submit",
                    "title": "Testing RAG quality with LangChain - automated framework",
                    "tips": "Focus na LangChain integration. Show real examples.",
                    "priority": "⭐ MEDIUM"
                },
                {
                    "name": "r/LocalLLaMA",
                    "url": "https://reddit.com/r/LocalLLaMA/submit",
                    "title": "RAG Guardian - test your local RAG systems",
                    "tips": "Mention że działa z local models, nie tylko API.",
                    "priority": "⭐ MEDIUM"
                },
                {
                    "name": "r/opensource",
                    "url": "https://reddit.com/r/opensource/submit",
                    "title": "RAG Guardian - open-source RAG testing framework",
                    "tips": "Highlight MIT license, contribution guidelines, community aspect.",
                    "priority": "⚡ LOW"
                }
            ],

            "Dev Communities": [
                {
                    "name": "Dev.to",
                    "url": "https://dev.to/new",
                    "title": "Stop Guessing if Your RAG Works - Test It Like Code",
                    "tips": "Long-form article. Tutorial style. Use code examples.",
                    "priority": "🔥 HIGH"
                },
                {
                    "name": "Hashnode",
                    "url": "https://hashnode.com/create/story",
                    "title": "Building RAG Guardian: Testing RAG Systems Automatically",
                    "tips": "Technical deep-dive. Behind the scenes, architecture.",
                    "priority": "⭐ MEDIUM"
                },
                {
                    "name": "Medium",
                    "url": "https://medium.com/new-story",
                    "title": "How to Test RAG Systems Before Production",
                    "tips": "Cross-post from Dev.to. Tag: Python, AI, Testing.",
                    "priority": "⚡ LOW"
                }
            ],

            "AI/ML Communities": [
                {
                    "name": "Papers with Code",
                    "url": "https://paperswithcode.com/",
                    "title": "Add to RAG evaluation tools",
                    "tips": "Jeśli masz benchmarks/metrics comparison.",
                    "priority": "⚡ LOW"
                },
                {
                    "name": "Hugging Face Hub",
                    "url": "https://huggingface.co/new-space",
                    "title": "RAG Guardian Demo Space",
                    "tips": "Stwórz interactive demo. Streamlit app showing evaluation.",
                    "priority": "⭐ MEDIUM"
                },
                {
                    "name": "AI Discord servers",
                    "url": "LangChain, LlamaIndex official Discords",
                    "title": "Share in #show-and-tell channels",
                    "tips": "Don't spam. Share value, help others.",
                    "priority": "⭐ MEDIUM"
                }
            ],

            "Twitter/X": [
                {
                    "name": "Tweet thread",
                    "url": "https://twitter.com/compose/tweet",
                    "title": "Use generated thread from this script",
                    "tips": "Post 10-11am US Eastern. Tag @langchainai @llama_index. Use hashtags.",
                    "priority": "🔥 HIGH"
                },
                {
                    "name": "Tag influencers",
                    "url": "In replies",
                    "title": "@swyx @GergelyOrosz @llama_index @LangChainAI",
                    "tips": "Don't spam. Genuinely ask for feedback if relevant.",
                    "priority": "⚡ LOW"
                }
            ],

            "Newsletters": [
                {
                    "name": "TLDR AI",
                    "url": "https://tldr.tech/ai/submit",
                    "title": "Submit via form",
                    "tips": "Newsletter z 500k+ subscribers. Worth a shot.",
                    "priority": "⭐ MEDIUM"
                },
                {
                    "name": "Python Weekly",
                    "url": "https://www.pythonweekly.com/submit",
                    "title": "Submit your project",
                    "tips": "Quality threshold high. Highlight testing aspect.",
                    "priority": "⭐ MEDIUM"
                }
            ]
        }

        return submissions

    def save_all_content(self, output_dir: Path):
        """Zapisz wszystkie wygenerowane content do plików."""
        output_dir.mkdir(exist_ok=True)

        # Twitter thread
        twitter = self.generate_twitter_thread()
        with open(output_dir / "twitter_thread.txt", "w", encoding="utf-8") as f:
            for i, tweet in enumerate(twitter, 1):
                f.write(f"=== TWEET {i}/{len(twitter)} ===\n")
                f.write(f"{tweet}\n\n")
                f.write(f"Characters: {len(tweet)}\n")
                f.write("="*60 + "\n\n")

        # LinkedIn
        linkedin = self.generate_linkedin_post()
        with open(output_dir / "linkedin_post.md", "w", encoding="utf-8") as f:
            f.write(linkedin)

        # Reddit
        reddit = self.generate_reddit_posts()
        for subreddit, content in reddit.items():
            filename = subreddit.replace("/", "_") + ".md"
            with open(output_dir / filename, "w", encoding="utf-8") as f:
                f.write(f"# {content['title']}\n\n")
                f.write(content['body'])

        # Dev.to
        devto = self.generate_devto_article()
        with open(output_dir / "devto_article.md", "w", encoding="utf-8") as f:
            f.write(devto)

        # Submission list
        submissions = self.generate_submission_list()
        with open(output_dir / "submission_list.json", "w", encoding="utf-8") as f:
            json.dump(submissions, f, indent=2, ensure_ascii=False)

        # Checklist markdown
        with open(output_dir / "PROMOTION_CHECKLIST.md", "w", encoding="utf-8") as f:
            f.write("# RAG Guardian - Promotion Checklist\n\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")

            for category, items in submissions.items():
                f.write(f"## {category}\n\n")
                for item in items:
                    f.write(f"- [ ] **{item['name']}** ({item['priority']})\n")
                    f.write(f"  - URL: {item['url']}\n")
                    f.write(f"  - Title: {item['title']}\n")
                    f.write(f"  - Tips: {item['tips']}\n\n")

        print(f"✅ Generated content saved to {output_dir}/")
        print(f"\nFiles created:")
        print(f"  - twitter_thread.txt")
        print(f"  - linkedin_post.md")
        print(f"  - r_MachineLearning.md")
        print(f"  - r_Python.md")
        print(f"  - r_LangChain.md")
        print(f"  - devto_article.md")
        print(f"  - submission_list.json")
        print(f"  - PROMOTION_CHECKLIST.md")


def main():
    parser = argparse.ArgumentParser(
        description="RAG Guardian Promotion Content Generator"
    )
    parser.add_argument(
        "--platform",
        choices=["twitter", "linkedin", "reddit", "devto", "all"],
        help="Generate content for specific platform"
    )
    parser.add_argument(
        "--submit",
        action="store_true",
        help="Show submission checklist"
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("promotion_content"),
        help="Output directory for generated content"
    )

    args = parser.parse_args()
    gen = PromotionGenerator()

    if args.submit:
        submissions = gen.generate_submission_list()
        print("\n" + "="*70)
        print("RAG GUARDIAN - SUBMISSION CHECKLIST")
        print("="*70 + "\n")

        for category, items in submissions.items():
            print(f"\n### {category}")
            print("-" * 70)
            for item in items:
                print(f"\n{item['priority']} {item['name']}")
                print(f"    URL: {item['url']}")
                print(f"    Title: {item['title']}")
                print(f"    Tips: {item['tips']}")

        print("\n" + "="*70)
        print("Run with --platform all to generate content for all platforms")
        print("="*70 + "\n")

    elif args.platform:
        if args.platform == "all":
            gen.save_all_content(args.output_dir)
        elif args.platform == "twitter":
            tweets = gen.generate_twitter_thread()
            for i, tweet in enumerate(tweets, 1):
                print(f"\n=== TWEET {i}/{len(tweets)} ===")
                print(tweet)
                print(f"Characters: {len(tweet)}")
        elif args.platform == "linkedin":
            print(gen.generate_linkedin_post())
        elif args.platform == "reddit":
            posts = gen.generate_reddit_posts()
            for sub, content in posts.items():
                print(f"\n{'='*70}")
                print(f"{sub}")
                print('='*70)
                print(f"\nTitle: {content['title']}\n")
                print(content['body'])
        elif args.platform == "devto":
            print(gen.generate_devto_article())
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
