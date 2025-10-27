# RAG Guardian

**Przestań zgadywać czy twój RAG działa. Przetestuj go.**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Tests](https://img.shields.io/badge/tests-119%20passed-brightgreen.svg)](https://github.com/gacabartosz/rag-guardian)
[![Coverage](https://img.shields.io/badge/coverage-68%25-yellow.svg)](https://github.com/gacabartosz/rag-guardian)

---

## Problem który rozwiązuje

**Scenariusz:** Wdrażasz system RAG do produkcji. Wszystko działa... ale:
- Czy model czasami halucynuje?
- Czy używa właściwych dokumentów?
- Czy retrieval faktycznie znajduje to co powinien?
- Jak to sprawdzić **zanim** klient zobaczy błędną odpowiedź?

**Dotychczasowe rozwiązanie:** Ręczne sprawdzanie, modlitwa, nadzieja 🙏

**Lepsze rozwiązanie:** Automatyczne testy jakości RAG. Tak jak pytest dla kodu, RAG Guardian dla systemów RAG.

## Co to daje w praktyce

Po 30 minutach setupu masz:
- ✅ Automatyczne testy przed każdym wdrożeniem
- ✅ Metryki które pokazują **dokładnie** co się zepsuło
- ✅ HTML raporty które możesz pokazać szefowi/klientowi
- ✅ Integracja z CI/CD - testy blokują merge jak coś poszło nie tak

**Oszczędność czasu:** Zamiast 2h ręcznego sprawdzania przed każdym release → 5 minut automatycznych testów.

## Jak to działa - 3 komendy

```bash
# 1. Instalacja
pip install rag-guardian

# 2. Wygeneruj config
rag-guardian init

# 3. Uruchom testy
rag-guardian test --dataset tests/my_test_cases.jsonl
```

**Output:**
```
🚀 RAG Guardian - Starting Evaluation

✅ Loaded 20 test cases
🔄 Running evaluation...

============================================================
RAG GUARDIAN - EVALUATION SUMMARY
============================================================

Overall Status: ❌ FAILED (3/20 tests failed)
Pass Rate: 85.0%

METRICS:
✅ faithfulness        : 0.92 (threshold: 0.85)
✅ groundedness        : 0.88 (threshold: 0.80)
❌ context_relevancy   : 0.68 (threshold: 0.75)  ← FIX THIS
✅ answer_correctness  : 0.90 (threshold: 0.80)

FAILED TESTS:
1. "What's the shipping time?" - retrieval failed (score: 0.68)
2. "Can I cancel my order?" - wrong answer (score: 0.65)
3. "What's your phone number?" - hallucinated (score: 0.71)
============================================================
```

**Wniosek:** Wiesz dokładnie co naprawić. Nie zgadywanie "coś nie gra".

## API w 10 liniach kodu

```python
from rag_guardian import Evaluator, TestCase

# Test cases (lub załaduj z JSONL)
tests = [
    TestCase(
        question="Jaka jest polityka zwrotów?",
        expected_answer="30 dni, bez pytań"
    ),
    TestCase(
        question="Czy wysyłacie za granicę?",
        expected_answer="Tak, do 50+ krajów"
    )
]

# Run
evaluator = Evaluator.from_config(".rag-guardian.yml")
results = evaluator.evaluate_dataset(tests)

# Check
if results.passed:
    print("✅ All good - ship it!")
else:
    print(f"❌ {results.failed_tests} tests failed - fix before deploy")
    for fail in results.failures:
        print(f"  - {fail.test_case.question}: {fail.failure_reasons}")
```

## Co testuje (4 metryki)

1. **Faithfulness (0-1)** - Czy model się nie dopycha? Czy odpowiedź opiera się na kontekście?
2. **Groundedness (0-1)** - Czy faktycznie używa retrieved docs, czy improwizuje?
3. **Context Relevancy (0-1)** - Czy retrieval znajduje właściwe dokumenty?
4. **Answer Correctness (0-1)** - Czy odpowiedź zgadza się z expected answer?

**Każda metryka** ma threshold (np. 0.80). Jak nie przejdzie → test failuje → CI/CD się wysypuje → musisz naprawić **zanim** wejdzie na prod.

Prosto. Skutecznie.

## Integracje - działa z tym co masz

### LangChain (3 linijki)

```python
from langchain.chains import RetrievalQA
from rag_guardian.integrations import LangChainAdapter

qa_chain = RetrievalQA.from_chain_type(...)  # Twój istniejący chain

adapter = LangChainAdapter(qa_chain)
evaluator = Evaluator(adapter)
results = evaluator.evaluate_dataset("tests.jsonl")
```

### LlamaIndex (3 adaptery)

```python
from rag_guardian.integrations import LlamaIndexVectorStoreAdapter

index = VectorStoreIndex.from_documents(documents)  # Twój index

adapter = LlamaIndexVectorStoreAdapter(index, similarity_top_k=3)
evaluator = Evaluator(adapter)
results = evaluator.evaluate_dataset("tests.jsonl")
```

**Inne adaptery:**
- `LlamaIndexAdapter` - dla dowolnego QueryEngine
- `LlamaIndexChatEngineAdapter` - dla chat RAG

### Custom RAG (własna implementacja)

```python
from rag_guardian.integrations import CustomRAGAdapter

class MyRAG(CustomRAGAdapter):
    def retrieve(self, query: str) -> List[str]:
        return self.vector_db.search(query, top_k=5)

    def generate(self, query: str, contexts: List[str]) -> str:
        return self.llm.generate(f"Context: {contexts}\n\nQ: {query}")

evaluator = Evaluator(MyRAG())
```

**Lub HTTP API:**

```python
from rag_guardian.integrations import CustomHTTPAdapter

adapter = CustomHTTPAdapter(
    endpoint="http://twoj-rag-api.com/query",
    headers={"Authorization": "Bearer token"},
    timeout=30,
    max_retries=3
)
```

## Real-world example - e-commerce customer support

**Setup:**
- RAG na dokumentacji support (100+ FAQs)
- 50 test cases z expected answers
- Threshold: 0.85 dla wszystkich metryk

**Workflow:**
1. Developer zmienia prompt template
2. Push do GitHub
3. GitHub Actions uruchamia `rag-guardian test`
4. Test failuje - faithfulness spadło z 0.91 → 0.78
5. PR dostaje ❌ - nie można zmerge'ować
6. Developer poprawia prompt
7. Test pass → merge → deploy

**Oszczędność:** Zamiast klient zgłasza "coś nie działa" na produkcji → łapiesz błąd **przed** deployem.

**ROI:** Jeden taki bug złapany przed prod = kilka godzin oszczędności na debugging i hotfix.

## Reporty które możesz pokazać

### HTML Report (do pokazania szefowi)

```python
from rag_guardian import HTMLReporter

results = evaluator.evaluate_dataset("tests.jsonl")
HTMLReporter.generate(results, "report.html")
```

**Dostajesz:**
- 📊 Kolorowe wykresy metryk
- 📈 Pass rate w %
- ❌ Lista failed testów z dokładnym powodem
- ✅ Lista passed testów
- 📱 Działa na telefonie

Otwierasz w przeglądarce, pokazujesz, wszyscy wiedzą co się dzieje.

### JSON (do CI/CD)

```python
from rag_guardian import JSONReporter

JSONReporter.save(results, "results.json")
```

Albo z CLI:
```bash
rag-guardian test --dataset tests.jsonl --output-format json
```

Idealnie do parsowania w skryptach, wysyłania do Slack, whatever.

## CI/CD - GitHub Actions example

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
        run: |
          rag-guardian test \
            --config .rag-guardian.yml \
            --dataset tests/rag_test_cases.jsonl

      - name: Upload results
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: rag-test-results
          path: results/
```

**Result:** Każdy PR automatycznie testowany. Nie mergujesz dopóki RAG nie przejdzie testów.

## Co dostajesz (v1.0.0)

- ✅ **4 metryki** - faithfulness, groundedness, context relevancy, answer correctness
- ✅ **CLI + Python API** - używaj jak ci wygodnie
- ✅ **LangChain + LlamaIndex** - działa out-of-the-box
- ✅ **Custom integrations** - HTTP adapter lub dziedzicz CustomRAGAdapter
- ✅ **HTML + JSON reports** - dla ludzi i dla maszyn
- ✅ **119 testów (68% coverage)** - battle-tested
- ✅ **CI/CD ready** - GitHub Actions examples included
- ✅ **Reproducible builds** - poetry.lock commitowany

## Roadmap (co będzie)

### v1.1 (styczeń 2025)
- 🎯 **Semantic similarity** - embeddingi zamiast keyword matching (lepsza accuracy)
- 📊 **Baseline comparison** - porównuj metryki przed/po zmianach
- 💬 **Slack notifications** - alert jak testy failują

### v1.5 (Q1 2025)
- ⚡ **Performance metrics** - latency, token usage, koszty API
- 🚀 **Batch processing** - testuj 500+ cases równolegle
- 💾 **SQL storage** - zapisuj resulaty do bazy, analizuj trendy

### v2.0 (Q2 2025)
- 📡 **Production monitoring** - sample i testuj real user queries
- 🎨 **Web dashboard** - wizualizuj metryki over time
- 🤖 **LLM-as-judge** - GPT-4 do evaluation (dla complex cases)

## Instalacja

### From PyPI
```bash
pip install rag-guardian
```

### From source (deweloperzy)
```bash
git clone https://github.com/gacabartosz/rag-guardian.git
cd rag-guardian

poetry install
poetry run pytest  # 119 testów powinno przejść
```

**Requirements:** Python 3.10+ (testowane na 3.12)

## FAQ - pytania które dostaję

**Q: Jak to się różni od Ragas?**

A: Ragas → research-oriented, sporo theory. RAG Guardian → pytest dla RAG, praktyczne testy w CI/CD. Plus mamy first-class LangChain/LlamaIndex support i ładne reporty HTML.

**Q: Muszę mieć running RAG żeby testować?**

A: Tak, RAG Guardian testuje live systems. Ale możesz mockować responses w testach (jak w unit testach).

**Q: Jakie LLM działa?**

A: Wszystkie. RAG Guardian testuje **system RAG**, nie konkretny model. OpenAI, Anthropic, local Llama - dowolny. Byleby dało się opakować w adapter.

**Q: Jak dokładne są metryki?**

A: W v1.0 → keyword matching. Szybkie, ok accuracy (~80-85%). W v1.1 → semantic similarity z embeddings. Wolniejsze, lepsza accuracy (~90-95%).

**Q: Czy mogę dodać własną metrykę?**

A: Jasne. Dziedzicz `BaseMetric`, implementuj `evaluate()`. Zobacz [examples/](examples/) jak to zrobić.

**Q: Production-ready?**

A: Tak. v1.0 stable, 119 testów, używane w prawdziwych projektach. Śmiało wrzucaj do CI/CD. Production monitoring (v2.0) to już extra features typu real-time dashboardy.

**Q: Ile to kosztuje?**

A: €0. Open-source, MIT license. Rob co chcesz.

## Contributing

Znalazłeś bug? Masz pomysł na feature? PRy mile widziane!

```bash
git clone https://github.com/gacabartosz/rag-guardian.git
cd rag-guardian
poetry install

# Run tests
poetry run pytest

# Format
poetry run black .
poetry run isort .

# Lint
poetry run ruff check .
poetry run mypy rag_guardian
```

## Tech stack

**Built with:**
- [LangChain](https://github.com/langchain-ai/langchain) - RAG framework
- [LlamaIndex](https://github.com/jerryjliu/llama_index) - RAG framework
- [httpx](https://github.com/encode/httpx) - HTTP client with retries

**Inspired by:**
- [Ragas](https://github.com/explodinggradients/ragas) - metrics ideas
- [pytest](https://github.com/pytest-dev/pytest) - testing philosophy

---

## Author

**Made by [Bartosz Gaca](https://bartoszgaca.pl)**

AI & Automation Strategist | Buduję systemy które oszczędzają czas

*Zbudowałem RAG Guardian bo miałem dość ręcznego sprawdzania czy RAG nie halucynuje przed każdym deployem. Teraz 5 minut `pytest`, raport HTML, git push. Done.*

*Jeśli budujesz systemy RAG i chcesz przestać zgadywać czy działają - spróbuj. Zaoszczędzi ci to godzin.*

---

**License:** MIT - do whatever you want

**Links:**
- 📦 [PyPI](https://pypi.org/project/rag-guardian/)
- 💻 [GitHub](https://github.com/gacabartosz/rag-guardian)
- 🌐 [Website](https://bartoszgaca.pl)
- 📧 Contact: [GitHub Issues](https://github.com/gacabartosz/rag-guardian/issues)
