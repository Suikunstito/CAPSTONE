# ADR 0001 — Keep Django models as managed=False and external DB schema

Status: Accepted

Context
-------

The organization provides a canonical SQL Server schema managed outside this repository. Several models require specific collation and column types which must be preserved.

Decision
--------

We will keep business models defined with `Meta.managed = False` and avoid running `makemigrations`/`migrate` against those tables. Any schema changes must go through the database owners and be reflected in this codebase as model adjustments only.

Consequences
------------

- Simpler integration with existing DB, but less convenient local migrations.
- Developer workflow must use `init_sqlite_db.py` for local testing where applicable.
