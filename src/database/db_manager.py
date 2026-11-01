"""
PROJECT RU'YA — See Beyond the Numbers
SQLite database manager for ElectroMart Chandigarh.

Uses SQLAlchemy to create tables, load existing CSV files, and run
analytical queries. Paths are resolved from the project root.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd
from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    create_engine,
    delete,
    func,
    inspect,
    select,
    text,
)
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, sessionmaker

ROOT_DIR = Path(__file__).resolve().parents[2]
RAW_DIR = ROOT_DIR / "data" / "raw"
PROCESSED_DIR = ROOT_DIR / "data" / "processed"
DB_DIR = ROOT_DIR / "database"
DB_PATH = DB_DIR / "ruya.db"

PRODUCTS_CSV = RAW_DIR / "products.csv"
CUSTOMERS_CSV = RAW_DIR / "customers.csv"
SALES_CSV = PROCESSED_DIR / "cleaned_sales.csv"
MONTHLY_CSV = PROCESSED_DIR / "monthly_sales.csv"

EXPECTED_COUNTS = {
    "products": 74,
    "customers": 5_000,
    "sales_transactions": 50_000,
    "monthly_sales": 48,
}


class Base(DeclarativeBase):
    """Declarative base for PROJECT RU'YA tables."""


class Product(Base):
    __tablename__ = "products"

    product_id: Mapped[str] = mapped_column(String(16), primary_key=True)
    product_name: Mapped[str] = mapped_column(String(120), nullable=False)
    category: Mapped[str] = mapped_column(String(60), nullable=False)
    subcategory: Mapped[str] = mapped_column(String(60), nullable=False)
    brand: Mapped[str] = mapped_column(String(60), nullable=False)
    unit_cost: Mapped[float] = mapped_column(Float, nullable=False)
    selling_price: Mapped[float] = mapped_column(Float, nullable=False)


class Customer(Base):
    __tablename__ = "customers"

    customer_id: Mapped[str] = mapped_column(String(16), primary_key=True)
    customer_name: Mapped[str] = mapped_column(String(120), nullable=False)
    age: Mapped[int] = mapped_column(Integer, nullable=False)
    gender: Mapped[str] = mapped_column(String(16), nullable=False)
    city: Mapped[str] = mapped_column(String(60), nullable=False)
    locality: Mapped[str] = mapped_column(String(60), nullable=False)
    customer_segment: Mapped[str] = mapped_column(String(30), nullable=False)


class SalesTransaction(Base):
    __tablename__ = "sales_transactions"

    transaction_id: Mapped[str] = mapped_column(String(20), primary_key=True)
    order_id: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    transaction_date: Mapped[Any] = mapped_column(DateTime, nullable=False, index=True)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    month: Mapped[int] = mapped_column(Integer, nullable=False)
    month_name: Mapped[str] = mapped_column(String(20), nullable=False)
    quarter: Mapped[int] = mapped_column(Integer, nullable=False)
    day: Mapped[int] = mapped_column(Integer, nullable=False)
    day_of_week: Mapped[int] = mapped_column(Integer, nullable=False)
    day_name: Mapped[str] = mapped_column(String(20), nullable=False)
    is_weekend: Mapped[bool] = mapped_column(Boolean, nullable=False)
    order_month: Mapped[str] = mapped_column(String(7), nullable=False, index=True)
    customer_id: Mapped[str] = mapped_column(
        String(16), ForeignKey("customers.customer_id"), nullable=False, index=True
    )
    customer_name: Mapped[str] = mapped_column(String(120), nullable=False)
    age: Mapped[int] = mapped_column(Integer, nullable=False)
    gender: Mapped[str] = mapped_column(String(16), nullable=False)
    city: Mapped[str] = mapped_column(String(60), nullable=False)
    customer_locality: Mapped[str] = mapped_column(String(60), nullable=False)
    customer_segment: Mapped[str] = mapped_column(String(30), nullable=False)
    customer_purchase_count: Mapped[int] = mapped_column(Integer, nullable=False)
    customer_total_spending: Mapped[float] = mapped_column(Float, nullable=False)
    product_id: Mapped[str] = mapped_column(
        String(16), ForeignKey("products.product_id"), nullable=False, index=True
    )
    product_name: Mapped[str] = mapped_column(String(120), nullable=False)
    category: Mapped[str] = mapped_column(String(60), nullable=False)
    subcategory: Mapped[str] = mapped_column(String(60), nullable=False)
    brand: Mapped[str] = mapped_column(String(60), nullable=False)
    catalog_unit_cost: Mapped[float] = mapped_column(Float, nullable=False)
    catalog_selling_price: Mapped[float] = mapped_column(Float, nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    unit_price: Mapped[float] = mapped_column(Float, nullable=False)
    gross_sales: Mapped[float] = mapped_column(Float, nullable=False)
    discount_percentage: Mapped[float] = mapped_column(Float, nullable=False)
    discount_amount: Mapped[float] = mapped_column(Float, nullable=False)
    net_sales: Mapped[float] = mapped_column(Float, nullable=False)
    unit_cost: Mapped[float] = mapped_column(Float, nullable=False)
    total_cost: Mapped[float] = mapped_column(Float, nullable=False)
    gross_profit: Mapped[float] = mapped_column(Float, nullable=False)
    gst_percentage: Mapped[float] = mapped_column(Float, nullable=False)
    gst_amount: Mapped[float] = mapped_column(Float, nullable=False)
    total_amount: Mapped[float] = mapped_column(Float, nullable=False)
    revenue: Mapped[float] = mapped_column(Float, nullable=False)
    profit: Mapped[float] = mapped_column(Float, nullable=False)
    profit_margin: Mapped[float] = mapped_column(Float, nullable=True)
    payment_method: Mapped[str] = mapped_column(String(40), nullable=False)
    sales_channel: Mapped[str] = mapped_column(String(20), nullable=False)
    sale_locality: Mapped[str] = mapped_column(String(60), nullable=False)
    order_status: Mapped[str] = mapped_column(String(20), nullable=False)
    is_returned: Mapped[bool] = mapped_column(Boolean, nullable=False, index=True)
    is_valid: Mapped[bool] = mapped_column(Boolean, nullable=False)
    validation_issues: Mapped[str | None] = mapped_column(Text, nullable=True)


class MonthlySale(Base):
    __tablename__ = "monthly_sales"

    month: Mapped[str] = mapped_column(String(7), primary_key=True)
    total_orders: Mapped[int] = mapped_column(Integer, nullable=False)
    units_sold: Mapped[int] = mapped_column(Integer, nullable=False)
    gross_revenue: Mapped[float] = mapped_column(Float, nullable=False)
    realized_revenue: Mapped[float] = mapped_column(Float, nullable=False)
    total_profit: Mapped[float] = mapped_column(Float, nullable=False)
    average_order_value: Mapped[float] = mapped_column(Float, nullable=False)
    return_count: Mapped[int] = mapped_column(Integer, nullable=False)


TABLE_MODELS = {
    "products": Product,
    "customers": Customer,
    "sales_transactions": SalesTransaction,
    "monthly_sales": MonthlySale,
}


def get_database_path() -> Path:
    """Return the SQLite file path under database/."""
    return DB_PATH


def get_engine(echo: bool = False) -> Engine:
    """Create a SQLAlchemy engine for database/ruya.db."""
    DB_DIR.mkdir(parents=True, exist_ok=True)
    url = "sqlite:///" + DB_PATH.as_posix()
    engine = create_engine(url, echo=echo, future=True)
    return engine


def get_session_factory(engine: Engine | None = None) -> sessionmaker[Session]:
    """Return a session factory bound to the project engine."""
    return sessionmaker(bind=engine or get_engine(), expire_on_commit=False, future=True)


def create_tables(engine: Engine | None = None) -> list[str]:
    """Create all project tables if they do not already exist."""
    engine = engine or get_engine()
    Base.metadata.create_all(engine)
    return list(Base.metadata.tables.keys())


def table_exists(table_name: str, engine: Engine | None = None) -> bool:
    """Return True if the named table exists in SQLite."""
    engine = engine or get_engine()
    return inspect(engine).has_table(table_name)


def get_row_count(table_name: str, engine: Engine | None = None) -> int:
    """Return the number of rows in a table, or 0 if it does not exist."""
    engine = engine or get_engine()
    if not table_exists(table_name, engine):
        return 0
    with engine.connect() as conn:
        result = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
        return int(result.scalar_one())


def execute_query(sql: str, engine: Engine | None = None, params: dict[str, Any] | None = None) -> pd.DataFrame:
    """Run an analytical SQL query and return a DataFrame."""
    engine = engine or get_engine()
    with engine.connect() as conn:
        return pd.read_sql_query(text(sql), conn, params=params or {})


def _records_from_csv(path: Path, parse_dates: list[str] | None = None) -> list[dict[str, Any]]:
    """Load a CSV and convert it to Python records suitable for SQLAlchemy inserts."""
    if not path.exists():
        raise FileNotFoundError(f"CSV not found: {path.relative_to(ROOT_DIR)}")
    frame = pd.read_csv(path, parse_dates=parse_dates or [])
    if "validation_issues" in frame.columns:
        frame["validation_issues"] = frame["validation_issues"].fillna("").astype(str)
    frame = frame.astype(object).where(pd.notna(frame), None)
    return frame.to_dict(orient="records")


def replace_table_contents(
    model: type[Base],
    records: list[dict[str, Any]],
    engine: Engine | None = None,
) -> int:
    """
    Replace a table's rows in one transaction.

    Existing rows are deleted first so re-running the loader cannot duplicate keys.
    """
    engine = engine or get_engine()
    table_name = model.__tablename__
    with engine.begin() as conn:
        conn.execute(text("PRAGMA foreign_keys = OFF"))
        conn.execute(delete(model))
        if records:
            conn.execute(model.__table__.insert(), records)
        conn.execute(text("PRAGMA foreign_keys = ON"))
    return get_row_count(table_name, engine)


def load_csv_into_table(
    csv_path: Path,
    model: type[Base],
    engine: Engine | None = None,
    parse_dates: list[str] | None = None,
) -> int:
    """Load a CSV into a table, replacing any previous contents."""
    records = _records_from_csv(csv_path, parse_dates=parse_dates)
    return replace_table_contents(model, records, engine=engine)


def load_all_tables(engine: Engine | None = None) -> dict[str, int]:
    """Create schema and load products, customers, sales, and monthly tables."""
    engine = engine or get_engine()
    create_tables(engine)

    counts = {
        "products": load_csv_into_table(PRODUCTS_CSV, Product, engine),
        "customers": load_csv_into_table(CUSTOMERS_CSV, Customer, engine),
        "sales_transactions": load_csv_into_table(
            SALES_CSV,
            SalesTransaction,
            engine,
            parse_dates=["transaction_date"],
        ),
        "monthly_sales": load_csv_into_table(MONTHLY_CSV, MonthlySale, engine),
    }
    return counts


def csv_metrics() -> dict[str, float | int]:
    """Compute validation metrics from processed sales CSV for cross-checks."""
    sales = pd.read_csv(SALES_CSV)
    realized = ~sales["is_returned"].astype(bool)
    return {
        "total_revenue": float(sales["revenue"].sum()),
        "realized_revenue": float(sales.loc[realized, "revenue"].sum()),
        "total_profit": float(sales.loc[realized, "profit"].sum()),
        "total_orders": int(sales["order_id"].nunique()),
        "units_sold": int(sales["quantity"].sum()),
        "return_count": int(sales["is_returned"].astype(bool).sum()),
    }


def sql_metrics(engine: Engine | None = None) -> dict[str, float | int]:
    """Compute the same validation metrics from SQLite."""
    engine = engine or get_engine()
    query = """
        SELECT
            SUM(revenue) AS total_revenue,
            SUM(CASE WHEN is_returned = 0 THEN revenue ELSE 0 END) AS realized_revenue,
            SUM(CASE WHEN is_returned = 0 THEN profit ELSE 0 END) AS total_profit,
            COUNT(DISTINCT order_id) AS total_orders,
            SUM(quantity) AS units_sold,
            SUM(CASE WHEN is_returned = 1 THEN 1 ELSE 0 END) AS return_count
        FROM sales_transactions
    """
    row = execute_query(query, engine).iloc[0]
    return {
        "total_revenue": float(row["total_revenue"]),
        "realized_revenue": float(row["realized_revenue"]),
        "total_profit": float(row["total_profit"]),
        "total_orders": int(row["total_orders"]),
        "units_sold": int(row["units_sold"]),
        "return_count": int(row["return_count"]),
    }


def validate_database(engine: Engine | None = None, loaded_counts: dict[str, int] | None = None) -> dict[str, Any]:
    """Check row counts against expected values and cross-check SQL vs CSV metrics."""
    engine = engine or get_engine()
    counts = loaded_counts or {name: get_row_count(name, engine) for name in EXPECTED_COUNTS}
    count_ok = {name: counts[name] == expected for name, expected in EXPECTED_COUNTS.items()}

    from_csv = csv_metrics()
    from_sql = sql_metrics(engine)
    metric_ok = {
        key: abs(float(from_sql[key]) - float(from_csv[key])) < 0.05
        for key in from_csv
    }

    return {
        "counts": counts,
        "count_ok": count_ok,
        "csv_metrics": from_csv,
        "sql_metrics": from_sql,
        "metric_ok": metric_ok,
        "all_ok": all(count_ok.values()) and all(metric_ok.values()),
    }
