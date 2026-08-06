# Security Policy

If you discover a security vulnerability, please contact the project owner privately.

Do not open public issues for security-sensitive matters. For this repository (internal/academic), coordinate with the maintainers.

Immediate actions:

- Do not commit secrets into the repository. Use environment variables stored outside VCS.
- Rotate any secret that was committed (e.g., `DJANGO_SECRET_KEY`).
- Consider purging sensitive data from git history using `git filter-repo` or `bfg`, with appropriate backups.
