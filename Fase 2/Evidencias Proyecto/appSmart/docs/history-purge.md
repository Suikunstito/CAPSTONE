# History purge guidance

If sensitive data (secrets) were committed to the repository, consider purging the history using `git filter-repo` or `bfg`. This is a destructive operation that rewrites history and requires coordination with all collaborators.

High-level steps:

1. Backup repository (clone --mirror).
2. Use `git filter-repo --path .env.development --invert-paths` or BFG to remove the file.
3. Force-push the rewritten history to remote and notify collaborators to reclone.

Do not perform history rewrites without explicit authorization and coordination.
