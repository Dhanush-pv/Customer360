# Customer360 Governed Platform: Foundation & Source Integration

**Author:** Dhanush

## Features

- **Local-first stack** — PostgreSQL 16 via Docker Compose with a health check; no cloud account needed.
- **Source-aligned schemas** — separate `commerce`, `crm`, `marketing`, `support` and `ops` schemas
  that preserve each source system's own identifiers (no golden record yet).
- **Deterministic synthetic generator** — the same seed always produces byte-identical CSVs
  (default: 500 customers, 1,200 orders, 520 CRM profiles, 1,000 marketing events, 250 tickets).
- **Deliberate data messiness** for Week 2 identity resolution: email casing/whitespace differences,
  phone-format variations, missing phones and duplicate CRM profiles.
- **Structural validation** — registered column contract, duplicate headers, row width, blank rows
  and empty files are rejected *before* anything is written to the database.
- **Transactional, repeatable batch loader** — full refresh of all five tables in one transaction;
  a failure rolls back every table and is recorded as `failed` in `ops.ingestion_runs`.
- **Run audit trail** — `ops.ingestion_runs` stores start/end time, status, per-table row counts and errors.
- **Quality gates** — pytest (18 tests, ~86% coverage), Ruff lint, GitHub Actions CI.

## Architecture

```text
Synthetic generator -> CSV extracts -> structural validation -> batch loader
                                                                  |
                                       PostgreSQL: commerce / crm / marketing / support / ops
```

## Quick start

```bash
cp .env.example .env                       # optional; defaults are local-only
docker compose up -d postgres              # wait until healthy
python -m venv .venv && source .venv/bin/activate     # Windows: .venv\Scripts\Activate.ps1
pip install -e ".[dev]"
python -m customer360 generate --output data/generated --seed 42
python -m customer360 init-db
python -m customer360 load --input data/generated
pytest && ruff check customer360 tests
```

`make up | generate | init-db | load | test | lint | reset` wrap the same commands.
See `docs/runbooks/local-development.md` for troubleshooting and reset instructions.

## Repository layout

```text
.
├── .github/workflows/ci.yml   # lint + tests on push / PR
├── customer360/               # CLI, config, db, generator, validation, ingestion
├── data/generated/            # generated extracts (git-ignored, .gitkeep tracked)
├── docs/                      # architecture, data dictionary, ADR, runbook, checklist
├── sql/001_create_source_schemas.sql
├── tests/
├── docker-compose.yml  Makefile  pyproject.toml  .env.example  LICENSE
```

## Database objects

`commerce.customers`, `commerce.orders`, `crm.profiles`, `marketing.events`, `support.tickets`
and `ops.ingestion_runs`. See `docs/data-dictionary/source-tables.md` and
`docs/architecture/source-system-erd.md`.

## Configuration

`C360_DB_HOST`, `C360_DB_PORT`, `C360_DB_NAME`, `C360_DB_USER`, `C360_DB_PASSWORD`
(see `.env.example`). Defaults are for a disposable local database only; never commit `.env`
or reuse the default password elsewhere.

## Verification performed

Tested against PostgreSQL 16: schema init run twice (idempotent), full load and reload (1,200 orders,
no orphan orders), and a forced constraint violation — the load rolled back, tables stayed intact,
and the run was recorded as `failed`.

## Known limitations

- Synthetic data only; full-refresh batch loading (no CDC / incremental ingestion).
- Generated orders may pre-date the customer's `created_at`; this is a source-data quirk, not validated in Week 1.
- Identity resolution, dbt, SCD2, governance, Airflow and Terraform arrive in later weeks.
- No production-scale performance claims.

## License

MIT — see `LICENSE`. © 2026 Dhanush.
