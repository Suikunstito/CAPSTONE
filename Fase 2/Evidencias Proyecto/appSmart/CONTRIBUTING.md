# Contributing (Internal)

This repository is maintained for academic purposes and contributions are internal-only.

Guidelines:

- Follow code style: `black` and `isort` (see `pyproject.toml`).
- Run tests locally with `pytest` before pushing.
- Use feature branches and descriptive commit messages.
- Do not commit secrets; use `.env.development.local` for local secrets and ensure `.gitignore` excludes it.
