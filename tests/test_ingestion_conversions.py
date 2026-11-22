from datetime import UTC, date, datetime
from decimal import Decimal

from customer360.ingestion import _convert


def test_commerce_customer_created_at_is_a_date():
    result = _convert("commerce", "customers", "created_at", "2024-03-15")
    assert result == date(2024, 3, 15)
    assert not isinstance(result, datetime)


def test_support_ticket_created_at_preserves_timestamp():
    result = _convert("support", "tickets", "created_at", "2025-02-03T12:45:00+00:00")
    assert result == datetime(2025, 2, 3, 12, 45, tzinfo=UTC)


def test_order_total_is_decimal():
    assert _convert("commerce", "orders", "order_total", "19.95") == Decimal("19.95")


def test_optional_resolved_timestamp_becomes_null():
    assert _convert("support", "tickets", "resolved_at", "") is None
