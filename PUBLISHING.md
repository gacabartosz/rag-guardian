# Publishing RAG Guardian to PyPI

## Instrukcja publikacji na PyPI

### Prerequisites

1. **Konto na PyPI**
   - Zarejestruj się na https://pypi.org/account/register/
   - Potwierdź email

2. **API Token**
   - Idź do https://pypi.org/manage/account/token/
   - Stwórz nowy token ("Add API token")
   - Scope: "Entire account" (przy pierwszej publikacji)
   - Zapisz token (dostaniesz go tylko raz!)

### Krok 1: Przygotowanie

```bash
# Upewnij się że wszystko działa
poetry run pytest  # Wszystkie testy muszą przejść

# Sprawdź wersję w pyproject.toml
grep version pyproject.toml
# Powinna być 1.0.0 (lub nowsza)

# Zbuduj package
poetry build
```

To stworzy:
- `dist/rag_guardian-1.0.0.tar.gz` - source distribution
- `dist/rag_guardian-1.0.0-py3-none-any.whl` - wheel

### Krok 2: Test publication (opcjonalnie)

Przed prawdziwą publikacją możesz przetestować na Test PyPI:

```bash
# Configure test PyPI
poetry config repositories.test-pypi https://test.pypi.org/legacy/

# Publish to test PyPI
poetry publish -r test-pypi --username __token__ --password YOUR_TEST_PYPI_TOKEN

# Test installation
pip install --index-url https://test.pypi.org/simple/ rag-guardian
```

### Krok 3: Prawdziwa publikacja

```bash
# Publish to PyPI
poetry publish --username __token__ --password YOUR_PYPI_TOKEN
```

Albo jeśli masz token zapisany w poetry:

```bash
# Zapisz token (raz)
poetry config pypi-token.pypi YOUR_PYPI_TOKEN

# Publish (później wystarczy to)
poetry publish
```

### Krok 4: Weryfikacja

Po publikacji:

1. **Sprawdź na PyPI**
   - Idź do https://pypi.org/project/rag-guardian/
   - Sprawdź czy README się wyświetla poprawnie
   - Sprawdź metadata (wersja, opis, classifiers)

2. **Test instalacji**
   ```bash
   # W nowym virtualenv
   pip install rag-guardian
   rag-guardian --version  # Powinno pokazać 1.0.0
   ```

3. **Test CLI**
   ```bash
   rag-guardian init
   # Powinno stworzyć .rag-guardian.yml
   ```

### Krok 5: Update README badges (opcjonalnie)

Po publikacji możesz dodać badge z wersją:

```markdown
[![PyPI version](https://badge.fury.io/py/rag-guardian.svg)](https://pypi.org/project/rag-guardian/)
[![Downloads](https://pepy.tech/badge/rag-guardian)](https://pepy.tech/project/rag-guardian)
```

## Publikacja nowej wersji

Przy każdym update:

1. **Update wersji** w `pyproject.toml`:
   ```toml
   version = "1.0.1"  # Bump version
   ```

2. **Update CHANGELOG.md** - dodaj co się zmieniło

3. **Commit i tag**:
   ```bash
   git add pyproject.toml CHANGELOG.md
   git commit -m "chore: bump version to 1.0.1"
   git tag v1.0.1
   git push origin main --tags
   ```

4. **Rebuild i publish**:
   ```bash
   poetry build
   poetry publish
   ```

## Semantic Versioning

Używamy [SemVer](https://semver.org/):

- **MAJOR** (1.0.0 → 2.0.0): Breaking changes
- **MINOR** (1.0.0 → 1.1.0): New features, backward compatible
- **PATCH** (1.0.0 → 1.0.1): Bug fixes, backward compatible

### Examples:

- `1.0.0 → 1.0.1` - Fixed bug in HTML reporter
- `1.0.0 → 1.1.0` - Added semantic similarity metrics
- `1.0.0 → 2.0.0` - Changed API, renamed `Evaluator.run()` to `Evaluator.evaluate()`

## Troubleshooting

### Error: "File already exists"

PyPI nie pozwala na upload tej samej wersji dwa razy. Musisz bump'nąć wersję.

```bash
# Edit pyproject.toml - zmień version
poetry build
poetry publish
```

### Error: "Invalid token"

Token wygasł lub źle skopiowałeś. Wygeneruj nowy na PyPI.

### Package nie wyświetla README

README musi być w Markdown i określony w `pyproject.toml`:

```toml
readme = "README.md"
```

Jeśli nadal nie działa, przebuduj package:

```bash
rm -rf dist/
poetry build
poetry publish
```

## Security

**WAŻNE:**
- ❌ Nigdy nie commituj API tokenów do repo
- ❌ Nie udostępniaj tokenów nikomu
- ✅ Używaj tokenów tylko przez poetry config lub zmienne środowiskowe
- ✅ Możesz dodać `.pypirc` do `.gitignore` jeśli go używasz

## Checklist przed publikacją

- [ ] Wszystkie testy przechodzą (`poetry run pytest`)
- [ ] README jest aktualny i poprawnie sformatowany
- [ ] CHANGELOG.md ma wpis dla nowej wersji
- [ ] Wersja w pyproject.toml jest bump'nięta
- [ ] LICENSE jest MIT
- [ ] poetry.lock jest commitowany
- [ ] Brak wrażliwych danych w kodzie (.env w .gitignore)
- [ ] Keywords w pyproject.toml są dobre (dla SEO na PyPI)
- [ ] Classifiers są poprawne (Development Status, Python versions)

## First-time setup command sequence

Całość w jednym ciągu (po skonfigurowaniu tokena):

```bash
# Test that everything works
poetry run pytest

# Build
poetry build

# Publish
poetry publish

# Verify
pip install rag-guardian
rag-guardian --version
```

---

**After publication:** Remember to update README.md with:
- Link to PyPI package
- Installation command (`pip install rag-guardian`)
- Version badge

Good luck! 🚀
