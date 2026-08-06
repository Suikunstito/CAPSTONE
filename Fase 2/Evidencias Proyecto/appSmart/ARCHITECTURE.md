# Architecture Overview

This Django project (`inventario_web`) groups domain apps under a single project: `catalog`, `inventory`, `sales`, and `users`.

Key architectural constraints:

- Production DB: Microsoft SQL Server. Models are defined with `managed=False` and specific `db_collation='Modern_Spanish_CI_AS'` to match external schema.
- Do NOT run `makemigrations` or `migrate` for business tables — schema managed externally.
- ML prediction engine lives in `inventory/services/predictions.py` and should be covered by unit tests.

Recommended docs: ADRs directory contains decisions about `managed=False` and DB collation.
