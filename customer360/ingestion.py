import csv
import json
from datetime import UTC, date, datetime
from decimal import Decimal
from pathlib import Path

from customer360.db import connect
from customer360.validation import SOURCE_COLUMNS, validate_directory

TABLES = {
    "commerce_customers.csv": ("commerce", "customers"),
    "commerce_orders.csv": ("commerce", "orders"),
    "crm_profiles.csv": ("crm", "profiles"),
    "marketing_events.csv": ("marketing", "events"),
    "support_tickets.csv": ("support", "tickets"),
}

DATE_COLUMNS = {
    ("commerce", "customers"): {"created_at"},
    ("commerce", "orders"): {"order_date"},
}
TIMESTAMP_COLUMNS = {
    ("crm", "profiles"): {"updated_at"},
    ("marketing", "events"): {"event_timestamp"},
    ("support", "tickets"): {"created_at", "resolved_at"},
}
DECIMAL_COLUMNS = {"order_total"}


def _convert(schema: str, table: str, column: str, value: str):
    if value == "" and column in {"resolved_at"}:
        return None
    if value == "":
        return None
    if column in DATE_COLUMNS.get((schema, table), set()):
        return date.fromisoformat(value)
    if column in TIMESTAMP_COLUMNS.get((schema, table), set()):
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    if column in DECIMAL_COLUMNS:
        return Decimal(value)
    return value


def _record_failed_run(run_id: int, error: Exception) -> None:
    # This uses a separate transaction so the failure record survives the
    # rollback of the source-table load transaction.
    with connect() as conn, conn.cursor() as cur:
        cur.execute(
            """
                UPDATE ops.ingestion_runs
                SET finished_at = %s, status = 'failed', error_message = %s
                WHERE ingestion_run_id = %s
                """,
            (datetime.now(UTC), str(error)[:2000], run_id),
        )


def load_sources(input_dir: Path) -> dict[str, int]:
    validate_directory(input_dir)
    counts: dict[str, int] = {}

    # Commit the run record first. It remains available even if the data
    # load transaction fails later.
    with connect() as conn, conn.cursor() as cur:
        cur.execute(
            """
                INSERT INTO ops.ingestion_runs (started_at, status)
                VALUES (%s, 'running')
                RETURNING ingestion_run_id
                """,
            (datetime.now(UTC),),
        )
        run_id = cur.fetchone()[0]

    try:
        with connect() as conn, conn.cursor() as cur:
            for filename, (schema, table) in TABLES.items():
                with (input_dir / filename).open(
                    "r", newline="", encoding="utf-8-sig"
                ) as handle:
                    reader = csv.DictReader(handle)
                    rows = list(reader)

                # Column identifiers come from the local, reviewed source contract,
                # never directly from a CSV header.
                columns = SOURCE_COLUMNS[filename]
                cur.execute(f"TRUNCATE TABLE {schema}.{table}")
                if rows:
                    column_sql = ", ".join(f'"{column}"' for column in columns)
                    placeholders = ", ".join(["%s"] * (len(columns) + 1))
                    statement = (
                        f"INSERT INTO {schema}.{table} ({column_sql}, loaded_at) "
                        f"VALUES ({placeholders})"
                    )
                    loaded_at = datetime.now(UTC)
                    values = [
                        tuple(_convert(schema, table, col, row[col]) for col in columns)
                        + (loaded_at,)
                        for row in rows
                    ]
                    cur.executemany(statement, values)

                counts[f"{schema}.{table}"] = len(rows)

            cur.execute(
                """
                    UPDATE ops.ingestion_runs
                    SET finished_at = %s, status = 'succeeded', row_counts = %s::jsonb
                    WHERE ingestion_run_id = %s
                    """,
                (datetime.now(UTC), json.dumps(counts), run_id),
            )
    except Exception as exc:
        _record_failed_run(run_id, exc)
        raise

    return counts
