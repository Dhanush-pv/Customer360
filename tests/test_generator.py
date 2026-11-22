from customer360.generator import generate_dataset


def test_generator_outputs_expected_files_and_counts(tmp_path):
    counts = generate_dataset(tmp_path, seed=7, customers=20, orders=35)
    assert counts["commerce_customers"] == 20
    assert counts["commerce_orders"] == 35
    assert counts["crm_profiles"] == 20
    assert counts["marketing_events"] == 40
    assert counts["support_tickets"] == 50

def test_generator_is_reproducible(tmp_path):
    a, b = tmp_path / "a", tmp_path / "b"
    generate_dataset(a, seed=123, customers=30, orders=40)
    generate_dataset(b, seed=123, customers=30, orders=40)
    for name in ["commerce_customers.csv", "commerce_orders.csv", "crm_profiles.csv",
                 "marketing_events.csv", "support_tickets.csv"]:
        assert (a / name).read_bytes() == (b / name).read_bytes()
