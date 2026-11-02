"""
PROJECT RU'YA — See Beyond the Numbers
Data preprocessing and feature engineering for ElectroMart Chandigarh.

Reads synthetic raw CSVs, validates them, enriches line items, and writes
analysis-ready tables. Invalid rows are flagged and retained, never dropped
silently.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT_DIR = Path(__file__).resolve().parents[2]
RAW_DIR = ROOT_DIR / "data" / "raw"
PROCESSED_DIR = ROOT_DIR / "data" / "processed"

TRANSACTIONS_FILE = RAW_DIR / "sales_transactions.csv"
PRODUCTS_FILE = RAW_DIR / "products.csv"
CUSTOMERS_FILE = RAW_DIR / "customers.csv"
CLEANED_SALES_FILE = PROCESSED_DIR / "cleaned_sales.csv"
MONTHLY_SALES_FILE = PROCESSED_DIR / "monthly_sales.csv"

MONEY_TOLERANCE = 0.02

TRANSACTION_COLUMNS = [
    "transaction_id",
    "order_id",
    "transaction_date",
    "customer_id",
    "product_id",
    "quantity",
    "unit_price",
    "gross_sales",
    "discount_percentage",
    "discount_amount",
    "net_sales",
    "unit_cost",
    "total_cost",
    "gross_profit",
    "gst_percentage",
    "gst_amount",
    "total_amount",
    "payment_method",
    "sales_channel",
    "locality",
    "order_status",
    "is_returned",
]


def money(values: pd.Series | np.ndarray) -> np.ndarray:
    """Round currency values to two decimal places."""
    return np.round(values, 2)


def load_raw_tables() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Load the three raw CSVs from data/raw/."""
    missing = [path for path in (TRANSACTIONS_FILE, PRODUCTS_FILE, CUSTOMERS_FILE) if not path.exists()]
    if missing:
        names = ", ".join(str(path.relative_to(ROOT_DIR)) for path in missing)
        raise FileNotFoundError(f"Missing raw data file(s): {names}")

    try:
        transactions = pd.read_csv(TRANSACTIONS_FILE)
        products = pd.read_csv(PRODUCTS_FILE)
        customers = pd.read_csv(CUSTOMERS_FILE)
    except OSError as exc:
        raise OSError(f"Failed to read raw CSV files: {exc}") from exc

    return transactions, products, customers


def parse_dates(transactions: pd.DataFrame) -> pd.DataFrame:
    """Parse transaction_date and flag rows that cannot be converted."""
    transactions = transactions.copy()
    parsed = pd.to_datetime(transactions["transaction_date"], errors="coerce")
    transactions["transaction_date"] = parsed
    return transactions


def _flag(issues: list[list[str]], mask: pd.Series, label: str) -> None:
    """Append a validation label to each True row in mask."""
    if not mask.any():
        return
    for idx in np.flatnonzero(mask.to_numpy()):
        issues[idx].append(label)


def validate_and_flag(
    transactions: pd.DataFrame,
    products: pd.DataFrame,
    customers: pd.DataFrame,
) -> pd.DataFrame:
    """
    Check integrity rules and store issues on each row.

    Records are never dropped. is_valid is False when one or more checks fail.
    """
    frame = transactions.copy()
    n = len(frame)
    issues: list[list[str]] = [[] for _ in range(n)]

    required = [col for col in TRANSACTION_COLUMNS if col in frame.columns]
    missing_required = [col for col in TRANSACTION_COLUMNS if col not in frame.columns]
    if missing_required:
        raise ValueError(f"Transactions table is missing columns: {missing_required}")

    _flag(issues, frame[required].isna().any(axis=1), "missing_value")
    _flag(issues, frame["transaction_date"].isna(), "invalid_date")
    _flag(issues, frame["transaction_id"].duplicated(keep=False), "duplicate_transaction_id")
    _flag(issues, pd.to_numeric(frame["quantity"], errors="coerce").fillna(-1) <= 0, "invalid_quantity")
    _flag(issues, pd.to_numeric(frame["unit_price"], errors="coerce").fillna(-1) <= 0, "invalid_unit_price")
    _flag(issues, pd.to_numeric(frame["unit_cost"], errors="coerce").fillna(-1) <= 0, "invalid_unit_cost")
    _flag(
        issues,
        ~frame["product_id"].isin(products["product_id"]),
        "unknown_product_id",
    )
    _flag(
        issues,
        ~frame["customer_id"].isin(customers["customer_id"]),
        "unknown_customer_id",
    )

    qty = pd.to_numeric(frame["quantity"], errors="coerce")
    unit_price = pd.to_numeric(frame["unit_price"], errors="coerce")
    unit_cost = pd.to_numeric(frame["unit_cost"], errors="coerce")
    discount_pct = pd.to_numeric(frame["discount_percentage"], errors="coerce")
    gst_pct = pd.to_numeric(frame["gst_percentage"], errors="coerce")

    expected_gross = money(qty * unit_price)
    expected_discount = money(frame["gross_sales"] * discount_pct / 100.0)
    expected_net = money(frame["gross_sales"] - frame["discount_amount"])
    expected_cost = money(qty * unit_cost)
    expected_profit = money(frame["net_sales"] - frame["total_cost"])
    expected_gst = money(frame["net_sales"] * gst_pct / 100.0)
    expected_total = money(frame["net_sales"] + frame["gst_amount"])

    _flag(issues, np.abs(frame["gross_sales"] - expected_gross) > MONEY_TOLERANCE, "inconsistent_gross_sales")
    _flag(issues, np.abs(frame["discount_amount"] - expected_discount) > MONEY_TOLERANCE, "inconsistent_discount")
    _flag(issues, np.abs(frame["net_sales"] - expected_net) > MONEY_TOLERANCE, "inconsistent_net_sales")
    _flag(issues, np.abs(frame["total_cost"] - expected_cost) > MONEY_TOLERANCE, "inconsistent_total_cost")
    _flag(issues, np.abs(frame["gross_profit"] - expected_profit) > MONEY_TOLERANCE, "inconsistent_gross_profit")
    _flag(issues, np.abs(frame["gst_amount"] - expected_gst) > MONEY_TOLERANCE, "inconsistent_gst_amount")
    _flag(issues, np.abs(frame["total_amount"] - expected_total) > MONEY_TOLERANCE, "inconsistent_total_amount")

    returned = frame["is_returned"].astype("boolean").fillna(False)
    _flag(
        issues,
        returned & (frame["order_status"].astype(str) != "Returned"),
        "return_status_mismatch",
    )

    frame["validation_issues"] = [";".join(item) if item else "" for item in issues]
    frame["is_valid"] = frame["validation_issues"].eq("")
    return frame


def integrate_dimensions(
    transactions: pd.DataFrame,
    products: pd.DataFrame,
    customers: pd.DataFrame,
) -> pd.DataFrame:
    """Join product and customer attributes, keeping a single copy of overlapping names."""
    product_keep = products.rename(
        columns={
            "unit_cost": "catalog_unit_cost",
            "selling_price": "catalog_selling_price",
        }
    )
    customer_keep = customers.rename(columns={"locality": "customer_locality"})
    merged = transactions.merge(product_keep, on="product_id", how="left", validate="many_to_one")
    merged = merged.merge(customer_keep, on="customer_id", how="left", validate="many_to_one")
    merged = merged.rename(columns={"locality": "sale_locality"})
    return merged


def engineer_features(sales: pd.DataFrame) -> pd.DataFrame:
    """Add calendar, profitability, and customer-level features. Original money columns stay intact."""
    sales = sales.copy()
    dates = sales["transaction_date"]

    sales["year"] = dates.dt.year
    sales["month"] = dates.dt.month
    sales["month_name"] = dates.dt.month_name()
    sales["quarter"] = dates.dt.quarter
    sales["day"] = dates.dt.day
    sales["day_of_week"] = dates.dt.day_of_week
    sales["day_name"] = dates.dt.day_name()
    sales["is_weekend"] = sales["day_of_week"] >= 5
    sales["order_month"] = dates.dt.to_period("M").astype(str)

    # revenue is GST-exclusive net_sales; original financial columns are not overwritten.
    sales["revenue"] = sales["net_sales"]
    sales["profit"] = sales["gross_profit"]
    sales["profit_margin"] = np.where(
        sales["revenue"].abs() > 1e-9,
        sales["profit"] / sales["revenue"],
        np.nan,
    )

    sales["is_returned"] = sales["is_returned"].astype(bool)

    realized = ~sales["is_returned"]
    purchase_count = sales.groupby("customer_id")["transaction_id"].transform("count")
    realized_spend = (
        sales.loc[realized]
        .groupby("customer_id")["revenue"]
        .sum()
        .rename("customer_total_spending")
    )
    sales["customer_purchase_count"] = purchase_count.astype(int)
    sales["customer_total_spending"] = sales["customer_id"].map(realized_spend).fillna(0.0)
    sales["customer_total_spending"] = money(sales["customer_total_spending"])
    return sales


def build_monthly_sales(sales: pd.DataFrame) -> pd.DataFrame:
    """
    Month-level table for analytics and forecasting.

    realized_revenue excludes returned transactions. Invalid rows are omitted
    from aggregates so forecasting is not driven by failed checks.
    """
    usable = sales.loc[sales["is_valid"]].copy()
    if usable.empty:
        return pd.DataFrame(
            columns=[
                "month",
                "total_orders",
                "units_sold",
                "gross_revenue",
                "realized_revenue",
                "total_profit",
                "average_order_value",
                "return_count",
            ]
        )

    realized_mask = ~usable["is_returned"]
    usable["realized_revenue"] = np.where(realized_mask, usable["revenue"], 0.0)
    usable["realized_profit"] = np.where(realized_mask, usable["profit"], 0.0)

    grouped = usable.groupby("order_month", dropna=False)
    monthly = grouped.agg(
        total_orders=("order_id", "nunique"),
        units_sold=("quantity", "sum"),
        gross_revenue=("revenue", "sum"),
        realized_revenue=("realized_revenue", "sum"),
        total_profit=("realized_profit", "sum"),
        return_count=("is_returned", "sum"),
    ).reset_index()

    realized_orders = (
        usable.loc[realized_mask]
        .groupby("order_month")["order_id"]
        .nunique()
        .rename("realized_orders")
    )
    monthly = monthly.merge(realized_orders, left_on="order_month", right_index=True, how="left")
    monthly["realized_orders"] = monthly["realized_orders"].fillna(0)
    monthly["average_order_value"] = np.where(
        monthly["realized_orders"] > 0,
        monthly["realized_revenue"] / monthly["realized_orders"],
        0.0,
    )
    monthly = monthly.drop(columns=["realized_orders"])
    monthly = monthly.rename(columns={"order_month": "month"})
    monthly = monthly.sort_values("month").reset_index(drop=True)

    money_cols = ["gross_revenue", "realized_revenue", "total_profit", "average_order_value"]
    monthly[money_cols] = np.round(monthly[money_cols], 2)
    monthly["return_count"] = monthly["return_count"].astype(int)
    monthly["units_sold"] = monthly["units_sold"].astype(int)
    monthly["total_orders"] = monthly["total_orders"].astype(int)
    return monthly[
        [
            "month",
            "total_orders",
            "units_sold",
            "gross_revenue",
            "realized_revenue",
            "total_profit",
            "average_order_value",
            "return_count",
        ]
    ]


def arrange_cleaned_columns(sales: pd.DataFrame) -> pd.DataFrame:
    """Stable column order for the processed sales file."""
    preferred = [
        "transaction_id",
        "order_id",
        "transaction_date",
        "year",
        "month",
        "month_name",
        "quarter",
        "day",
        "day_of_week",
        "day_name",
        "is_weekend",
        "order_month",
        "customer_id",
        "customer_name",
        "age",
        "gender",
        "city",
        "customer_locality",
        "customer_segment",
        "customer_purchase_count",
        "customer_total_spending",
        "product_id",
        "product_name",
        "category",
        "subcategory",
        "brand",
        "catalog_unit_cost",
        "catalog_selling_price",
        "quantity",
        "unit_price",
        "gross_sales",
        "discount_percentage",
        "discount_amount",
        "net_sales",
        "unit_cost",
        "total_cost",
        "gross_profit",
        "gst_percentage",
        "gst_amount",
        "total_amount",
        "revenue",
        "profit",
        "profit_margin",
        "payment_method",
        "sales_channel",
        "sale_locality",
        "order_status",
        "is_returned",
        "is_valid",
        "validation_issues",
    ]
    remaining = [col for col in sales.columns if col not in preferred]
    return sales[preferred + remaining]


def save_outputs(cleaned: pd.DataFrame, monthly: pd.DataFrame) -> None:
    """Write processed CSVs, creating data/processed if needed."""
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    cleaned.to_csv(CLEANED_SALES_FILE, index=False)
    monthly.to_csv(MONTHLY_SALES_FILE, index=False)


def print_validation_report(
    original_count: int,
    cleaned: pd.DataFrame,
    monthly: pd.DataFrame,
) -> None:
    """Print the required preprocessing summary."""
    processed_count = len(cleaned)
    invalid_count = int((~cleaned["is_valid"]).sum())
    missing_values = int(cleaned.isna().sum().sum())
    duplicate_ids = int(cleaned["transaction_id"].duplicated().sum())
    total_revenue = float(cleaned["revenue"].sum())
    realized_revenue = float(cleaned.loc[~cleaned["is_returned"], "revenue"].sum())
    total_profit = float(cleaned.loc[~cleaned["is_returned"], "profit"].sum())
    valid_dates = cleaned["transaction_date"].dropna()
    date_min = valid_dates.min()
    date_max = valid_dates.max()

    print("=" * 64)
    print("PROJECT RU'YA — PREPROCESSING COMPLETE")
    print("Source data is SYNTHETIC / fictional.")
    print("=" * 64)
    print(f"Original transaction count : {original_count:,}")
    print(f"Processed transaction count: {processed_count:,}")
    print(f"Removed/invalid records    : 0 removed / {invalid_count:,} flagged")
    print(f"Missing values             : {missing_values:,}")
    print(f"Duplicate transaction IDs  : {duplicate_ids:,}")
    print(f"Total revenue (before returns): {total_revenue:,.2f}")
    print(f"Realized revenue (ex-returns) : {realized_revenue:,.2f}")
    print(f"Total profit (ex-returns)     : {total_profit:,.2f}")
    if pd.isna(date_min) or pd.isna(date_max):
        print("Date range                  : unavailable")
    else:
        print(f"Date range                  : {date_min.date()} to {date_max.date()}")
    print(f"Monthly rows               : {len(monthly):,}")
    print(f"Wrote {CLEANED_SALES_FILE.relative_to(ROOT_DIR)}")
    print(f"Wrote {MONTHLY_SALES_FILE.relative_to(ROOT_DIR)}")
    print("=" * 64)


def process() -> tuple[pd.DataFrame, pd.DataFrame]:
    """Run the full preprocessing pipeline and return cleaned plus monthly tables."""
    transactions, products, customers = load_raw_tables()
    original_count = len(transactions)
    transactions = parse_dates(transactions)
    transactions = validate_and_flag(transactions, products, customers)
    sales = integrate_dimensions(transactions, products, customers)
    sales = engineer_features(sales)
    sales = arrange_cleaned_columns(sales)
    monthly = build_monthly_sales(sales)
    save_outputs(sales, monthly)
    print_validation_report(original_count, sales, monthly)
    return sales, monthly

def normalize_upload(raw: pd.DataFrame) -> pd.DataFrame:
    """Convert an uploaded retail CSV into the cleaned_sales schema used by analytics."""
    from config import COLUMN_MAP, REQUIRED_COLUMNS

    df = raw.copy()
    df.columns = [
        str(c).replace("\ufeff", "").strip().lower().replace(" ", "_")
        for c in df.columns
    ]
    df = df.rename(columns={c: COLUMN_MAP[c] for c in df.columns if c in COLUMN_MAP})
    df = df.loc[:, ~df.columns.duplicated()]

    if "revenue" not in df.columns and "net_sales" in df.columns:
        df["revenue"] = df["net_sales"]
    if "profit" not in df.columns and "gross_profit" in df.columns:
        df["profit"] = df["gross_profit"]

    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"Uploaded CSV is missing required columns: {missing}")

    df["transaction_date"] = pd.to_datetime(df["transaction_date"], errors="coerce")
    df = df.loc[df["transaction_date"].notna()].reset_index(drop=True)
    if df.empty:
        raise ValueError("No rows with a valid date were found.")

    for col in ["quantity", "revenue", "profit", "unit_price", "unit_cost",
                "discount_percentage", "discount_amount"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
        else:
            df[col] = 0.0

    if "is_returned" in df.columns:
        flag = df["is_returned"].astype(str).str.strip().str.lower()
    elif "return_status" in df.columns:
        flag = df["return_status"].astype(str).str.strip().str.lower()
    else:
        flag = pd.Series("no", index=df.index)
    df["is_returned"] = flag.isin(["returned", "return", "yes", "true", "1"])

    if "transaction_id" not in df.columns:
        if df["order_id"].is_unique:
            df["transaction_id"] = df["order_id"].astype(str)
        else:
            df["transaction_id"] = [f"TXN{i:07d}" for i in range(1, len(df) + 1)]
    if "product_id" not in df.columns:
        df["product_id"] = pd.factorize(df["product_name"])[0] + 1

    for col in ["brand", "sales_channel", "payment_method", "customer_segment",
                "sale_locality", "city"]:
        if col not in df.columns:
            df[col] = "Unknown"
        df[col] = df[col].fillna("Unknown").astype(str)
    df["customer_locality"] = df["sale_locality"]
    df["locality"] = df["sale_locality"]

    df["net_sales"] = df["revenue"]
    df["gross_profit"] = df["profit"]
    df["order_month"] = df["transaction_date"].dt.to_period("M").astype(str)
    df["is_valid"] = True
    return df


def process_upload(raw: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Upload pipeline: returns (cleaned_sales, monthly_sales). Nothing is written to disk."""
    cleaned = normalize_upload(raw)
    monthly = build_monthly_sales(cleaned)
    return cleaned, monthly

def main() -> int:
    try:
        process()
    except FileNotFoundError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    except (OSError, ValueError) as exc:
        print(f"ERROR: preprocessing failed: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
