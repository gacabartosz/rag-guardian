# Pull Request

## Co zmienia ten PR?

Jasny opis w 1-2 zdaniach.

## Typ zmiany

- [ ] Bug fix (non-breaking change)
- [ ] New feature (non-breaking change)
- [ ] Breaking change (fix lub feature które zmienia existing functionality)
- [ ] Documentation update

## Jak to przetestować?

```bash
# Kroki do sprawdzenia że działa
poetry install
poetry run pytest
```

## Checklist

- [ ] Kod jest zgodny z style guide (black, ruff, isort)
- [ ] Dodałem/zaktualizowałem testy
- [ ] Wszystkie testy przechodzą (`poetry run pytest`)
- [ ] Zaktualizowałem dokumentację (jeśli trzeba)
- [ ] Dodałem wpis do CHANGELOG.md (jeśli user-facing change)
- [ ] Kod nie ma hardcoded secrets/credentials
- [ ] Commit messages są jasne

## Related Issues

Closes #123
Fixes #456

## Screenshots (jeśli applicable)

Dodaj screenshots jeśli zmienia UI/reporty.

## Performance impact

- [ ] No impact
- [ ] Improves performance
- [ ] Might slow down (opisz dlaczego jest worth it)

## Breaking changes

Jeśli to breaking change, opisz:
- Co się zmienia w API
- Migration guide dla użytkowników
- Czy bump'nąłem major version?

---

**Thanks for contributing!** 🚀
