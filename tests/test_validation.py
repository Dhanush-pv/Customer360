import pytest

from customer360.generator import generate_dataset
from customer360.validation import DataValidationError, validate_csv, validate_directory


def test_generated_data_passes_validation(tmp_path):
    generate_dataset(tmp_path, customers=25, orders=60)
    result = validate_directory(tmp_path)
    assert result["commerce_customers.csv"] == 25
    assert result["commerce_orders.csv"] == 60

def test_missing_column_is_rejected(tmp_path):
    path = tmp_path / "commerce_customers.csv"
    path.write_text("customer_id,first_name\nC1,Ada\n", encoding="utf-8")
    with pytest.raises(DataValidationError, match="missing required columns"):
        validate_csv(path)

def test_empty_file_is_rejected(tmp_path):
    path = tmp_path / "commerce_orders.csv"
    path.write_text(
        "order_id,customer_id,order_date,order_status,currency,order_total\n",
        encoding="utf-8",
    )
    with pytest.raises(DataValidationError, match="no data rows"):
        validate_csv(path)


def test_unexpected_column_is_rejected(tmp_path):
    path = tmp_path / "commerce_customers.csv"
    path.write_text(
        "customer_id,first_name,last_name,email,phone,city,country_code,created_at,extra\n"
        "C1,Ada,Lovelace,a@example.test,,Berlin,DE,2024-01-01,unexpected\n",
        encoding="utf-8",
    )
    with pytest.raises(DataValidationError, match="unexpected columns: extra"):
        validate_csv(path)


def test_row_with_more_values_than_header_is_rejected(tmp_path):
    path = tmp_path / "commerce_customers.csv"
    path.write_text(
        "customer_id,first_name,last_name,email,phone,city,country_code,created_at\n"
        "C1,Ada,Lovelace,a@example.test,,Berlin,DE,2024-01-01,extra\n",
        encoding="utf-8",
    )
    with pytest.raises(DataValidationError, match="more values than the header"):
        validate_csv(path)


def test_row_with_too_few_values_is_rejected(tmp_path):
    path = tmp_path / "commerce_customers.csv"
    path.write_text(
        "customer_id,first_name,last_name,email,phone,city,country_code,created_at\n"
        "C1,Ada,Lovelace,a@example.test,,Berlin,DE\n",
        encoding="utf-8",
    )
    with pytest.raises(DataValidationError, match="fewer values than the header"):
        validate_csv(path)


def test_duplicate_header_is_rejected(tmp_path):
    path = tmp_path / "commerce_customers.csv"
    path.write_text(
        "customer_id,first_name,last_name,email,phone,city,country_code,created_at,created_at\n"
        "C1,Ada,Lovelace,a@example.test,,Berlin,DE,2024-01-01,2024-01-01\n",
        encoding="utf-8",
    )
    with pytest.raises(DataValidationError, match="duplicate column names"):
        validate_csv(path)
