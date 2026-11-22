"""Loader tests using a fake DB connection (no PostgreSQL needed)."""

import pytest

from customer360 import ingestion
from customer360.generator import generate_dataset
from customer360.validation import DataValidationError


class FakeCursor:
    def __init__(self, log, fail_on=None):
        self.log, self.fail_on = log, fail_on

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def execute(self, sql, params=None):
        self.log.append(("execute", " ".join(sql.split())))
        if self.fail_on and self.fail_on in sql:
            raise RuntimeError("boom")

    def executemany(self, sql, values):
        self.log.append(("executemany", len(values)))

    def fetchone(self):
        return (1,)


class FakeConnection:
    def __init__(self, log, fail_on=None):
        self.log, self.fail_on = log, fail_on

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def cursor(self):
        return FakeCursor(self.log, self.fail_on)


def test_load_sources_truncates_and_inserts_every_table(tmp_path, monkeypatch):
    log = []
    generate_dataset(tmp_path, customers=20, orders=30)
    monkeypatch.setattr(ingestion, "connect", lambda: FakeConnection(log))
    counts = ingestion.load_sources(tmp_path)
    assert counts["commerce.customers"] == 20
    assert counts["commerce.orders"] == 30
    assert sum(1 for kind, sql in log if kind == "execute" and "TRUNCATE" in sql) == 5
    assert sum(1 for kind, _ in log if kind == "executemany") == 5


def test_failed_load_is_recorded_and_reraised(tmp_path, monkeypatch):
    log = []
    generate_dataset(tmp_path, customers=20, orders=30)
    monkeypatch.setattr(ingestion, "connect", lambda: FakeConnection(log, fail_on="TRUNCATE"))
    with pytest.raises(RuntimeError):
        ingestion.load_sources(tmp_path)
    assert any("status = 'failed'" in sql for kind, sql in log if kind == "execute")


def test_invalid_extract_stops_before_any_database_work(tmp_path, monkeypatch):
    def _no_connection():
        raise AssertionError("must not connect")

    monkeypatch.setattr(ingestion, "connect", _no_connection)
    with pytest.raises(DataValidationError):
        ingestion.load_sources(tmp_path)
