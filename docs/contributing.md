# Contributing

Contributions are welcome! Follow these steps:

1. Fork the repo on GitHub.
2. Create a feature branch: `git checkout -b feature/my-new-feature`.
3. Commit changes: `git commit -am 'Add my new feature'`.
4. Push: `git push origin feature/my-new-feature`.
5. Open a Pull Request.

## Guidelines
- Follow PEP 8 style.
- Add tests for new features (use pytest).
- Update docs in `docs/` for changes.
- Target Windows for v0.1.x; add platform checks for cross-platform.

## Development Setup
- Install editable: `pip install -e .[dev]`.
- Run tests: `pytest`.
- Build docs: `mkdocs serve`.

Report issues on GitHub.