import argparse
from pathlib import Path

from customer360.db import initialize_database
from customer360.generator import generate_dataset
from customer360.ingestion import load_sources


def main():
    parser = argparse.ArgumentParser(prog="customer360")
    sub = parser.add_subparsers(dest="command", required=True)
    gen = sub.add_parser("generate")
    gen.add_argument("--output", type=Path, default=Path("data/generated"))
    gen.add_argument("--seed", type=int, default=42)
    gen.add_argument("--customers", type=int, default=500)
    gen.add_argument("--orders", type=int, default=1200)
    sub.add_parser("init-db")
    load = sub.add_parser("load")
    load.add_argument("--input", type=Path, default=Path("data/generated"))
    args = parser.parse_args()
    if args.command == "generate":
        result = generate_dataset(args.output, args.seed, args.customers, args.orders)
        print(f"Generated extracts in {args.output.resolve()}")
        for name, count in result.items():
            print(f"{name}: {count:,}")
    elif args.command == "init-db":
        initialize_database()
        print("Database schemas initialized.")
    elif args.command == "load":
        for table, count in load_sources(args.input).items():
            print(f"{table}: {count:,} rows loaded")

if __name__ == "__main__":
    main()
