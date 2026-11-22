import argparse
import csv
import random
from datetime import UTC, date, datetime, timedelta
from pathlib import Path

FIRST = ["Alex", "Jordan", "Taylor", "Morgan", "Jamie", "Casey", "Riley", "Avery",
         "Sam", "Cameron", "Robin", "Drew", "Charlie", "Reese", "Parker", "Skyler"]
LAST = ["Miller", "Schmidt", "Fischer", "Weber", "Brown", "Wilson", "Taylor", "Martin",
        "Anderson", "Thomas", "Jackson", "White", "Harris", "Clark", "Lewis", "Walker"]
CITIES = ["Berlin", "Munich", "Hamburg", "Leipzig", "Dresden", "Cologne", "Frankfurt"]

def write_csv(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

def generate_dataset(output_dir: Path, seed=42, customers=500, orders=1200):
    if customers < 10 or orders < 1:
        raise ValueError("customers must be >= 10 and orders must be >= 1")
    rng = random.Random(seed)
    people = []
    for i in range(1, customers + 1):
        first, last = rng.choice(FIRST), rng.choice(LAST)
        people.append({
            "customer_id": f"COM-{i:06d}", "first_name": first, "last_name": last,
            "email": f"{first.lower()}.{last.lower()}{i}@example.test",
            "phone": f"+49{rng.randint(1500000000, 1799999999)}",
            "city": rng.choice(CITIES), "country_code": rng.choice(["DE", "DE", "AT", "NL"]),
            "created_at": (date(2022, 1, 1) + timedelta(days=rng.randint(0, 1400))).isoformat()
        })
    commerce_orders = []
    for i in range(1, orders + 1):
        person = rng.choice(people)
        commerce_orders.append({
            "order_id": f"ORD-{i:08d}", "customer_id": person["customer_id"],
            "order_date": (date(2024, 1, 1) + timedelta(days=rng.randint(0, 1000))).isoformat(),
            "order_status": rng.choices(["delivered", "shipped", "cancelled", "processing"],
                                        weights=[78, 10, 5, 7])[0],
            "currency": "EUR", "order_total": f"{rng.uniform(12, 650):.2f}"
        })
    crm = []
    for i, person in enumerate(people, 1):
        email, phone = person["email"], person["phone"]
        if i % 7 == 0:
            email = f" {email.upper()} "
        if i % 9 == 0:
            phone = phone[:3] + " " + phone[3:6] + "-" + phone[6:]
        if i % 13 == 0:
            phone = ""
        row = {
            "profile_id": f"CRM-{i:06d}", "external_customer_ref": person["customer_id"],
            "first_name": person["first_name"], "last_name": person["last_name"],
            "email": email, "phone": phone, "postcode": f"{rng.randint(10000, 99999)}",
            "updated_at": datetime(2025, 1, 1, tzinfo=UTC).replace(
                day=((i - 1) % 28) + 1).isoformat()
        }
        crm.append(row)
        if i % 25 == 0:
            duplicate = dict(row)
            duplicate["profile_id"] = f"CRM-DUP-{i:06d}"
            duplicate["email"] = email.strip().lower()
            crm.append(duplicate)
    marketing = []
    for i in range(1, customers * 2 + 1):
        p = rng.choice(people)
        marketing.append({
            "event_id": f"MKT-{i:08d}", "source_customer_ref": p["customer_id"],
            "campaign_id": f"CMP-{rng.randint(1, 12):03d}",
            "channel": rng.choice(["email", "paid_search", "social", "referral"]),
            "event_type": rng.choice(["impression", "click", "conversion"]),
            "event_timestamp": (datetime(2025, 1, 1, tzinfo=UTC)
                                + timedelta(minutes=rng.randint(0, 525600))).isoformat()
        })
    tickets = []
    for i in range(1, max(50, customers // 2) + 1):
        p = rng.choice(people)
        created = datetime(2025, 1, 1, tzinfo=UTC) + timedelta(days=rng.randint(0, 365))
        tickets.append({
            "ticket_id": f"TKT-{i:07d}", "source_customer_ref": p["customer_id"],
            "category": rng.choice(["delivery", "payment", "account", "product", "refund"]),
            "priority": rng.choice(["low", "normal", "high"]),
            "status": rng.choice(["open", "in_progress", "resolved", "closed"]),
            "created_at": created.isoformat(),
            "resolved_at": (created + timedelta(hours=rng.randint(1, 120))).isoformat()
                           if rng.random() > .2 else ""
        })
    datasets = {
        "commerce_customers.csv": people, "commerce_orders.csv": commerce_orders,
        "crm_profiles.csv": crm, "marketing_events.csv": marketing,
        "support_tickets.csv": tickets
    }
    for filename, rows in datasets.items():
        write_csv(output_dir / filename, rows)
    return {name.removesuffix(".csv"): len(rows) for name, rows in datasets.items()}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path("data/generated"))
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--customers", type=int, default=500)
    parser.add_argument("--orders", type=int, default=1200)
    args = parser.parse_args()
    result = generate_dataset(args.output, args.seed, args.customers, args.orders)
    for name, count in result.items():
        print(f"{name}: {count:,} rows")

if __name__ == "__main__":
    main()
