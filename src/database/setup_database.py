"""
PROJECT RU'YA — See Beyond the Numbers
Create SQLite tables and load existing raw/processed CSV files.

Run from the project root:

    .venv/Scripts/python.exe src/database/setup_database.py
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.database.db_manager import (  # noqa: E402
    EXPECTED_COUNTS,
    get_database_path,
    get_engine,
    load_all_tables,
    table_exists,
    validate_database,
)


def main() -> int:
    print("=" * 64)
    print("PROJECT RU'YA — DATABASE SETUP")
    print("Source data is SYNTHETIC / fictional.")
    print("=" * 64)

    db_path = get_database_path()
    print(f"Database location: {db_path.relative_to(ROOT_DIR)}")

    try:
        engine = get_engine()
        loaded = load_all_tables(engine)
        tables = [name for name in EXPECTED_COUNTS if table_exists(name, engine)]
        report = validate_database(engine, loaded_counts=loaded)
    except (OSError, FileNotFoundError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:  # unexpected SQLAlchemy / IO failures
        print(f"ERROR: database setup failed: {exc}", file=sys.stderr)
        return 1

    print("Tables created:")
    for name in tables:
        print(f"  - {name}")

    print("Records loaded:")
    for name, count in report["counts"].items():
        expected = EXPECTED_COUNTS[name]
        status = "OK" if report["count_ok"][name] else "MISMATCH"
        print(f"  - {name}: {count:,} (expected {expected:,}) [{status}]")

    sql = report["sql_metrics"]
    csv = report["csv_metrics"]
    print("SQL validation results:")
    labels = {
        "total_revenue": "Total revenue",
        "realized_revenue": "Realized revenue (ex-returns)",
        "total_profit": "Total profit (ex-returns)",
        "total_orders": "Total orders",
        "units_sold": "Total units sold",
        "return_count": "Return count",
    }
    for key, label in labels.items():
        sql_value = sql[key]
        csv_value = csv[key]
        matched = "MATCH" if report["metric_ok"][key] else "MISMATCH"
        if isinstance(sql_value, float):
            print(f"  - {label}: SQL {sql_value:,.2f} | CSV {csv_value:,.2f} [{matched}]")
        else:
            print(f"  - {label}: SQL {sql_value:,} | CSV {csv_value:,} [{matched}]")

    if report["all_ok"]:
        print("Validation: PASSED")
        print("=" * 64)
        return 0

    print("Validation: FAILED")
    print("=" * 64)
    return 1


if __name__ == "__main__":
    sys.exit(main())
