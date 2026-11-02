"""
=========================================================
PROJECT RU'YA — SEE BEYOND THE NUMBERS
Retail Sales Analytics Engine
=========================================================

Purpose:
Generate business intelligence from the processed
retail sales database.

Data source:
SQLite database containing synthetic retail data.

Analytics:
1. Executive KPIs
2. Sales trends
3. Product performance
4. Category performance
5. Brand performance
6. Customer RFM segmentation
7. Geographic performance
8. Discount analysis
9. Sales channel analysis
10. Payment analysis

All monetary values are GST-exclusive.
Returned transactions are excluded from realized
revenue and realized profit.
=========================================================
"""

from pathlib import Path

import numpy as np
import pandas as pd

from sqlalchemy import create_engine


# =========================================================
# CONFIGURATION
# =========================================================

ROOT_DIR = Path(__file__).resolve().parents[2]

DATABASE_PATH = ROOT_DIR / "database" / "ruya.db"

EXPORT_DIR = ROOT_DIR / "data" / "processed" / "analytics"

engine = create_engine(
    f"sqlite:///{DATABASE_PATH.as_posix()}",
    echo=False
)


# =========================================================
# DATA LOADING
# =========================================================

def load_sales_data():

    if not DATABASE_PATH.exists():
        raise FileNotFoundError(
            f"Database not found: {DATABASE_PATH}"
        )

    query = """
        SELECT *
        FROM sales_transactions
    """

    df = pd.read_sql(query, engine)

    if df.empty:
        raise ValueError("Sales database is empty.")

    df["transaction_date"] = pd.to_datetime(
        df["transaction_date"],
        errors="coerce"
    )

    return df


def load_monthly_data():

    query = """
        SELECT *
        FROM monthly_sales
    """

    df = pd.read_sql(query, engine)

    if "month" in df.columns:
        df["month"] = pd.to_datetime(
            df["month"],
            errors="coerce"
        )

    return df


# =========================================================
# DATA NORMALIZATION
# =========================================================

def prepare_data(df):

    df = df.copy()

    # Handle boolean values safely.
    df["is_returned"] = (
        df["is_returned"]
        .astype(str)
        .str.lower()
        .isin(["true", "1", "yes"])
    )

    # Identify financial columns.
    if "revenue" not in df.columns:
        if "net_sales" in df.columns:
            df["revenue"] = df["net_sales"]
        else:
            raise ValueError(
                "Revenue column not found."
            )

    if "profit" not in df.columns:
        if "gross_profit" in df.columns:
            df["profit"] = df["gross_profit"]
        else:
            raise ValueError(
                "Profit column not found."
            )

    numeric_columns = [
        "revenue",
        "profit",
        "quantity",
        "discount_percentage",
        "discount_amount",
        "unit_price",
        "unit_cost",
    ]

    for column in numeric_columns:
        if column in df.columns:
            df[column] = pd.to_numeric(
                df[column],
                errors="coerce"
            ).fillna(0)

    # Derived analytical fields.
    df["realized_revenue"] = np.where(
        df["is_returned"],
        0,
        df["revenue"]
    )

    df["realized_profit"] = np.where(
        df["is_returned"],
        0,
        df["profit"]
    )

    df["year"] = df["transaction_date"].dt.year

    df["month"] = df["transaction_date"].dt.month

    df["quarter"] = (
        df["transaction_date"].dt.to_period("Q").astype(str)
    )

    df["month_name"] = (
        df["transaction_date"].dt.strftime("%b")
    )

    df["year_month"] = (
        df["transaction_date"].dt.to_period("M").astype(str)
    )

    return df


# =========================================================
# 1. EXECUTIVE KPIs
# =========================================================

def calculate_executive_kpis(df):

    total_transactions = len(df)

    returned = df[df["is_returned"]]

    valid_sales = df[~df["is_returned"]]

    gross_revenue = df["revenue"].sum()

    realized_revenue = valid_sales["revenue"].sum()

    realized_profit = valid_sales["profit"].sum()

    total_orders = (
        valid_sales["order_id"].nunique()
        if "order_id" in df.columns
        else len(valid_sales)
    )

    total_units = valid_sales["quantity"].sum()

    return_count = len(returned)

    return_rate = (
        return_count / total_transactions * 100
        if total_transactions else 0
    )

    average_order_value = (
        realized_revenue / total_orders
        if total_orders else 0
    )

    profit_margin = (
        realized_profit / realized_revenue * 100
        if realized_revenue else 0
    )

    average_discount = (
        df["discount_percentage"].mean()
        if "discount_percentage" in df.columns
        else 0
    )

    return pd.DataFrame([{
        "total_transactions": total_transactions,
        "total_orders": total_orders,
        "total_units_sold": total_units,
        "gross_revenue_before_returns": gross_revenue,
        "realized_revenue": realized_revenue,
        "realized_profit": realized_profit,
        "average_order_value": average_order_value,
        "profit_margin_percentage": profit_margin,
        "return_count": return_count,
        "return_rate_percentage": return_rate,
        "average_discount_percentage": average_discount,
    }])


# =========================================================
# 2. SALES TRENDS
# =========================================================

def calculate_sales_trends(df):

    monthly = (
        df.groupby("year_month")
        .agg(
            total_transactions=("transaction_id", "count"),
            gross_revenue=("revenue", "sum"),
            realized_revenue=("realized_revenue", "sum"),
            realized_profit=("realized_profit", "sum"),
            units_sold=("quantity", "sum"),
            return_count=("is_returned", "sum"),
        )
        .reset_index()
    )

    monthly["month"] = pd.to_datetime(
        monthly["year_month"]
    )

    monthly = monthly.sort_values("month")

    monthly["profit_margin"] = np.where(
        monthly["realized_revenue"] > 0,
        monthly["realized_profit"]
        / monthly["realized_revenue"] * 100,
        0
    )

    # Yearly performance.
    yearly = (
        monthly.assign(year=monthly["month"].dt.year)
        .groupby("year")
        .agg(
            gross_revenue=("gross_revenue", "sum"),
            realized_revenue=("realized_revenue", "sum"),
            realized_profit=("realized_profit", "sum"),
            units_sold=("units_sold", "sum"),
            transactions=("total_transactions", "sum"),
        )
        .reset_index()
    )

    # Quarterly performance.
    quarterly = (
        df.groupby("quarter")
        .agg(
            realized_revenue=("realized_revenue", "sum"),
            realized_profit=("realized_profit", "sum"),
            units_sold=("quantity", "sum"),
        )
        .reset_index()
    )

    return monthly, yearly, quarterly


# =========================================================
# 3. PRODUCT PERFORMANCE
# =========================================================

def calculate_product_performance(df):

    required = [
        "product_id",
        "product_name",
        "category",
        "brand",
    ]

    for column in required:
        if column not in df.columns:
            raise ValueError(
                f"Missing product column: {column}"
            )

    products = (
        df.groupby(
            ["product_id", "product_name", "category", "brand"]
        )
        .agg(
            units_sold=("quantity", "sum"),
            gross_revenue=("revenue", "sum"),
            realized_revenue=("realized_revenue", "sum"),
            realized_profit=("realized_profit", "sum"),
            transactions=("transaction_id", "count"),
        )
        .reset_index()
    )

    products["profit_margin"] = np.where(
        products["realized_revenue"] > 0,
        products["realized_profit"]
        / products["realized_revenue"] * 100,
        0
    )

    best_sellers = products.sort_values(
        "units_sold",
        ascending=False
    )

    top_revenue = products.sort_values(
        "realized_revenue",
        ascending=False
    )

    top_profit = products.sort_values(
        "realized_profit",
        ascending=False
    )

    return best_sellers, top_revenue, top_profit


# =========================================================
# 4. CATEGORY PERFORMANCE
# =========================================================

def calculate_category_performance(df):

    category = (
        df.groupby("category")
        .agg(
            units_sold=("quantity", "sum"),
            gross_revenue=("revenue", "sum"),
            realized_revenue=("realized_revenue", "sum"),
            realized_profit=("realized_profit", "sum"),
            transaction_count=("transaction_id", "count"),
        )
        .reset_index()
    )

    category["profit_margin"] = np.where(
        category["realized_revenue"] > 0,
        category["realized_profit"]
        / category["realized_revenue"] * 100,
        0
    )

    category["revenue_share"] = (
        category["realized_revenue"]
        / category["realized_revenue"].sum() * 100
    )

    return category.sort_values(
        "realized_revenue",
        ascending=False
    )


# =========================================================
# 5. BRAND PERFORMANCE
# =========================================================

def calculate_brand_performance(df):

    brand = (
        df.groupby("brand")
        .agg(
            units_sold=("quantity", "sum"),
            realized_revenue=("realized_revenue", "sum"),
            realized_profit=("realized_profit", "sum"),
            transaction_count=("transaction_id", "count"),
        )
        .reset_index()
    )

    brand["profit_margin"] = np.where(
        brand["realized_revenue"] > 0,
        brand["realized_profit"]
        / brand["realized_revenue"] * 100,
        0
    )

    return brand.sort_values(
        "realized_revenue",
        ascending=False
    )


# =========================================================
# 6. CUSTOMER RFM SEGMENTATION
# =========================================================

def calculate_customer_rfm(df):

    customer_df = df[
        ~df["is_returned"]
    ].copy()

    reference_date = (
        customer_df["transaction_date"].max()
        + pd.Timedelta(days=1)
    )

    rfm = (
        customer_df.groupby("customer_id")
        .agg(
            recency=(
                "transaction_date",
                lambda x: (reference_date - x.max()).days
            ),
            frequency=("order_id", "nunique"),
            monetary=("revenue", "sum"),
        )
        .reset_index()
    )

    # Rank first to avoid duplicate-bin problems.
    rfm["r_score"] = pd.qcut(
        rfm["recency"].rank(method="first"),
        5,
        labels=[5, 4, 3, 2, 1]
    ).astype(int)

    rfm["f_score"] = pd.qcut(
        rfm["frequency"].rank(method="first"),
        5,
        labels=[1, 2, 3, 4, 5]
    ).astype(int)

    rfm["m_score"] = pd.qcut(
        rfm["monetary"].rank(method="first"),
        5,
        labels=[1, 2, 3, 4, 5]
    ).astype(int)

    rfm["rfm_score"] = (
        rfm["r_score"].astype(str)
        + rfm["f_score"].astype(str)
        + rfm["m_score"].astype(str)
    )

    def assign_segment(row):

        r = row["r_score"]
        f = row["f_score"]
        m = row["m_score"]

        if r >= 4 and f >= 4 and m >= 4:
            return "Champions"

        elif r >= 3 and f >= 4:
            return "Loyal Customers"

        elif r >= 4 and f <= 2:
            return "Recent Customers"

        elif r >= 3 and f >= 2 and m >= 2:
            return "Potential Loyalists"

        elif r <= 2 and f >= 3:
            return "At Risk"

        elif r <= 2 and f <= 2:
            return "Lost Customers"

        else:
            return "Needs Attention"

    rfm["customer_segment"] = rfm.apply(
        assign_segment,
        axis=1
    )

    return rfm.sort_values(
        "monetary",
        ascending=False
    )


def calculate_customer_summary(rfm):

    summary = (
        rfm.groupby("customer_segment")
        .agg(
            customer_count=("customer_id", "count"),
            average_spending=("monetary", "mean"),
            total_spending=("monetary", "sum"),
            average_frequency=("frequency", "mean"),
            average_recency=("recency", "mean"),
        )
        .reset_index()
    )

    summary["customer_percentage"] = (
        summary["customer_count"]
        / summary["customer_count"].sum() * 100
    )

    return summary


# =========================================================
# 7. GEOGRAPHICAL ANALYTICS
# =========================================================

def calculate_geographical_performance(df):

    # Use transaction locality for geographical sales analysis.
    if "sale_locality" in df.columns:
        locality_column = "sale_locality"

    elif "customer_locality" in df.columns:
        locality_column = "customer_locality"

    elif "locality" in df.columns:
        locality_column = "locality"

    else:
        raise ValueError(
            "No locality column found in sales dataset."
        )

    geography = (
        df.groupby(locality_column)
        .agg(
            total_transactions=("transaction_id", "count"),
            units_sold=("quantity", "sum"),
            realized_revenue=("realized_revenue", "sum"),
            realized_profit=("realized_profit", "sum"),
        )
        .reset_index()
        .rename(columns={
            locality_column: "locality"
        })
    )

    geography["revenue_share"] = (
        geography["realized_revenue"]
        / geography["realized_revenue"].sum() * 100
    )

    return geography.sort_values(
        "realized_revenue",
        ascending=False
    )
# =========================================================
# 8. DISCOUNT AND PROFITABILITY ANALYTICS
# =========================================================

def calculate_discount_analysis(df):

    discount_df = df.copy()

    discount_df["discount_band"] = pd.cut(
        discount_df["discount_percentage"],
        bins=[-0.01, 5, 10, 15, 20, 30, 100],
        labels=[
            "0–5%",
            "5–10%",
            "10–15%",
            "15–20%",
            "20–30%",
            "Above 30%",
        ]
    )

    discount = (
        discount_df.groupby(
            "discount_band",
            observed=False
        )
        .agg(
            transaction_count=("transaction_id", "count"),
            average_discount=("discount_percentage", "mean"),
            realized_revenue=("realized_revenue", "sum"),
            realized_profit=("realized_profit", "sum"),
        )
        .reset_index()
    )

    discount["profit_margin"] = np.where(
        discount["realized_revenue"] > 0,
        discount["realized_profit"]
        / discount["realized_revenue"] * 100,
        0
    )

    return discount


# =========================================================
# 9. SALES CHANNEL ANALYSIS
# =========================================================

def calculate_channel_performance(df):

    if "sales_channel" not in df.columns:
        return pd.DataFrame()

    channel = (
        df.groupby("sales_channel")
        .agg(
            transactions=("transaction_id", "count"),
            realized_revenue=("realized_revenue", "sum"),
            realized_profit=("realized_profit", "sum"),
            units_sold=("quantity", "sum"),
        )
        .reset_index()
    )

    return channel.sort_values(
        "realized_revenue",
        ascending=False
    )


# =========================================================
# 10. PAYMENT METHOD ANALYSIS
# =========================================================

def calculate_payment_performance(df):

    if "payment_method" not in df.columns:
        return pd.DataFrame()

    payment = (
        df.groupby("payment_method")
        .agg(
            transaction_count=("transaction_id", "count"),
            realized_revenue=("realized_revenue", "sum"),
        )
        .reset_index()
    )

    payment["transaction_share"] = (
        payment["transaction_count"]
        / payment["transaction_count"].sum() * 100
    )

    return payment.sort_values(
        "realized_revenue",
        ascending=False
    )


# =========================================================
# EXPORT ANALYTICS
# =========================================================

def export_results(results):

    EXPORT_DIR.mkdir(parents=True, exist_ok=True)

    for name, dataframe in results.items():

        if isinstance(dataframe, pd.DataFrame):

            output_path = EXPORT_DIR / f"{name}.csv"

            dataframe.to_csv(
                output_path,
                index=False
            )

            print(
                f"Exported: {output_path.name}"
            )


# =========================================================
# MAIN ANALYTICS PIPELINE
# =========================================================

def run_all_analytics(df=None, export=True):

    print("\n")
    print("=" * 60)
    print("PROJECT RU'YA — ANALYTICS ENGINE")
    print("SEE BEYOND THE NUMBERS")
    print("=" * 60)

    print("\nLoading database...")

    raw_df = load_sales_data() if df is None else df

    df = prepare_data(raw_df)

    print(f"Loaded transactions: {len(df):,}")

    print("\nCalculating business analytics...")

    # Executive KPIs
    kpis = calculate_executive_kpis(df)

    # Sales trends
    monthly, yearly, quarterly = (
        calculate_sales_trends(df)
    )

    # Product analytics
    best_sellers, top_revenue, top_profit = (
        calculate_product_performance(df)
    )

    # Category and brand analytics
    category = calculate_category_performance(df)

    brand = calculate_brand_performance(df)

    # Customer analytics
    rfm = calculate_customer_rfm(df)

    customer_summary = calculate_customer_summary(rfm)

    # Geographic analytics
    geography = calculate_geographical_performance(df)

    # Discount analytics
    discount = calculate_discount_analysis(df)

    # Channel and payment analytics
    channel = calculate_channel_performance(df)

    payment = calculate_payment_performance(df)

    results = {
        "executive_kpis": kpis,
        "monthly_trends": monthly,
        "yearly_performance": yearly,
        "quarterly_performance": quarterly,
        "product_best_sellers": best_sellers,
        "product_revenue": top_revenue,
        "product_profitability": top_profit,
        "category_performance": category,
        "brand_performance": brand,
        "customer_rfm": rfm,
        "customer_segments": customer_summary,
        "geographical_performance": geography,
        "discount_analysis": discount,
        "channel_performance": channel,
        "payment_performance": payment,
    }

    print("\nExporting analytical results...")

    if export:
        export_results(results)

    print("\n")
    print("=" * 60)
    print("EXECUTIVE BUSINESS SUMMARY")
    print("=" * 60)

    print(
        kpis.T.to_string(
            header=False
        )
    )

    print("\nTOP 5 PRODUCT CATEGORIES")

    print(
        category.head(5).to_string(index=False)
    )

    print("\nTOP 5 BRANDS")

    print(
        brand.head(5).to_string(index=False)
    )

    print("\nCUSTOMER SEGMENTS")

    print(
        customer_summary.to_string(index=False)
    )

    print("\nTOP 5 LOCALITIES")

    print(
        geography.head(5).to_string(index=False)
    )

    print("\n")
    print("=" * 60)
    print("ANALYTICS ENGINE EXECUTED SUCCESSFULLY")
    print(f"Export location: {EXPORT_DIR}")
    print("=" * 60)

    return results


# =========================================================
# EXECUTION
# =========================================================

if __name__ == "__main__":

    run_all_analytics()