# Building Docker images with ODBC Driver for SQL Server

The project's Dockerfile installs the Microsoft ODBC Driver 17 for SQL Server which requires package installation and may require accepting licensing terms. When building images in CI, ensure the runner has apt support (Linux) and that the Dockerfile's commands run non-interactively.

Recommendations:

- Use a build stage that downloads and installs the ODBC driver using Microsoft package repository guidance.
- Cache apt lists and clean up to reduce image size.
- Do not store DB passwords in the image; read at runtime via env vars or secrets manager.
- Document any required environment variables in `README.md`.
