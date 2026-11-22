"""Structural validation for the five Week 1 source extracts."""

import csv
from pathlib import Path

SOURCE_COLUMNS = {
    "commerce_customers.csv": (
        "customer_id", "first_name", "last_name", "email", "phone", "city",
        "country_code", "created_at",
    ),
    "commerce_orders.csv": (
        "order_id", "customer_id", "order_date", "order_status", "currency", "order_total",
    ),
    "crm_profiles.csv": (
        "profile_id", "external_customer_ref", "first_name", "last_name", "email",
        "phone", "postcode", "updated_at",
    ),
    "marketing_events.csv": (
        "event_id", "source_customer_ref", "campaign_id", "channel", "event_type",
        "event_timestamp",
    ),
    "support_tickets.csv": (
        "ticket_id", "source_customer_ref", "category", "priority", "status",
        "created_at", "resolved_at",
    ),
}


class DataValidationError(ValueError):
    """An input extract does not satisfy its registered source contract."""


def validate_csv(path: Path) -> int:
    """Validate a CSV header and basic row structure; return its data-row count."""
    if not path.is_file():
        raise DataValidationError(f"Required source file does not exist: {path}")

    expected = SOURCE_COLUMNS.get(path.name)
    if expected is None:
        raise DataValidationError(f"No source contract registered for {path.name}")

    with path.open("r", newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        actual = reader.fieldnames or []
        if len(actual) != len(set(actual)):
            raise DataValidationError(f"{path.name}: duplicate column names are not allowed")

        missing = sorted(set(expected) - set(actual))
        unexpected = sorted(set(actual) - set(expected))
        if missing or unexpected:
            details = []
            if missing:
                details.append(f"missing required columns: {', '.join(missing)}")
            if unexpected:
                details.append(f"unexpected columns: {', '.join(unexpected)}")
            raise DataValidationError(f"{path.name}: {'; '.join(details)}")

        count = 0
        for line_no, row in enumerate(reader, start=2):
            if None in row:
                raise DataValidationError(
                    f"{path.name}:{line_no}: row has more values than the header"
                )
            if any(value is None for value in row.values()):
                raise DataValidationError(
                    f"{path.name}:{line_no}: row has fewer values than the header"
                )
            if not any((value or "").strip() for value in row.values()):
                raise DataValidationError(f"{path.name}:{line_no}: blank row")
            count += 1

        if count == 0:
            raise DataValidationError(f"{path.name}: file contains no data rows")
        return count


def validate_directory(directory: Path) -> dict[str, int]:
    """Validate every registered extract in a directory."""
    return {
        filename: validate_csv(directory / filename)
        for filename in SOURCE_COLUMNS
    }
