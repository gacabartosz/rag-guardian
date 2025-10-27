# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

**WAŻNE:** Nie zgłaszaj security issues jako public GitHub issues!

### Jak zgłosić:

1. **Email:** Wyślij na gaca.bartosz@gmail.com z tematem "[SECURITY] RAG Guardian"
2. **Treść:** Opisz vulnerability jasno i dokładnie
3. **Response time:** Odpowiem w ciągu 48h

### Co zawrzeć:

- Typ vulnerability (np. code injection, data leak)
- Kroki do reprodukcji
- Potencjalny impact
- Sugerowany fix (jeśli masz)

### Proces:

1. Potwierdzam receipt w 48h
2. Analizuję i weryfikuję (2-7 dni)
3. Pracuję nad fixem
4. Wypuszczam patch
5. Publikujemy advisory (po wydaniu patcha)

### Security best practices dla użytkowników:

- **Nie hardcoduj secrets** w test cases (używaj .env)
- **Validateuj inputs** przed przekazaniem do RAG
- **Używaj HTTPS** dla HTTP adapters
- **Limituj rate** w production (żeby nie wyciekły klucze API)
- **Review HTML reports** przed udostępnieniem (mogą zawierać sensitive data)

## Known security considerations

### API Keys w testach

RAG Guardian **nie loguje** ani nie zapisuje API keys. Ale:
- Test results mogą zawierać fragmenty odpowiedzi z LLM
- HTML reports są self-contained - przechowuj je bezpiecznie
- JSON exports mogą mieć PII - filtuj przed sharowaniem

### HTTP Adapter

- Domyślnie używa retry logic (może expose credentials przy logs)
- Timeout jest 30s (zapobiega długim połączeniom)
- Nie followuje redirects automatycznie

## Changelog security fixes

Wszystkie security fixes są oznaczone w CHANGELOG.md jako `[SECURITY]`.

## Credits

Zgłaszający security issues będą uznani publicznie (jeśli chcą) po wydaniu patcha.

---

**Pytania?** gaca.bartosz@gmail.com
