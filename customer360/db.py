from pathlib import Path

from customer360.config import settings


def connect():
    # Import at connection time so pure transformation tests can run without
    # a local PostgreSQL driver/server installed.
    import psycopg

    return psycopg.connect(**settings.connection_kwargs())


def initialize_database():
    sql_file = Path(__file__).resolve().parents[1] / "sql" / "001_create_source_schemas.sql"
    with connect() as conn, conn.cursor() as cur:
        cur.execute(sql_file.read_text(encoding="utf-8"))
