"""
PROJECT RU'YA
Database Management Module

Handles SQLite database creation, CSV imports,
data retrieval, and analytical SQL queries.
"""

from pathlib import Path

import pandas as pd

from sqlalchemy import (
    create_engine,
    MetaData,
    Table,
    Column,
    Integer,
    Float,
    String,
    Boolean,
    DateTime,
    ForeignKey,
    text,
)
from sqlalchemy.engine import Engine


# --------------------------------------------------
# PATH CONFIGURATION
# --------------------------------------------------

ROOT_DIR = Path(__file__).resolve().parents[2]

DATABASE_DIR = ROOT_DIR / "database"
DATABASE_PATH = DATABASE_DIR / "ruya.db"

RAW_DIR = ROOT_DIR / "data" / "raw"
PROCESSED_DIR = ROOT_DIR / "data" / "processed"

DATABASE_DIR.mkdir(parents=True, exist_ok=True)


# --------------------------------------------------
# DATABASE ENGINE
# --------------------------------------------------

engine = create_engine(
    f"sqlite:///{DATABASE_PATH.as_posix()}",
    echo=False,
)


# Enable SQLite foreign key enforcement.
from sqlalchemy import event


@event.listens_for(engine, "connect")
def enable_foreign_keys(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


# --------------------------------------------------
# DATA TYPES
# --------------------------------------------------

def infer_sql_type(series, column_name):

    if column_name == "transaction_date":
        return DateTime()

    if pd.api.types.is_bool_dtype(series):
        return Boolean()

    if pd.api.types.is_integer_dtype(series):
        return Integer()

    if pd.api.types.is_float_dtype(series):
        return Float()

    return String()


# --------------------------------------------------
# TABLE CREATION
# --------------------------------------------------

def create_table(metadata, table_name, dataframe):

    columns = []

    primary_keys = {
        "products": ["product_id"],
        "customers": ["customer_id"],
        "sales_transactions": ["transaction_id"],
        "monthly_sales": ["month"],
    }

    foreign_keys = {
        "sales_transactions": {
            "product_id": "products.product_id",
            "customer_id": "customers.customer_id",
        }
    }

    for column_name in dataframe.columns:

        column_type = infer_sql_type(
            dataframe[column_name],
            column_name
        )

        is_primary = (
            column_name in primary_keys.get(table_name, [])
        )

        foreign_key = foreign_keys.get(
            table_name, {}
        ).get(column_name)

        if foreign_key:
            columns.append(
                Column(
                    column_name,
                    column_type,
                    ForeignKey(foreign_key),
                    primary_key=is_primary,
                )
            )

        else:
            columns.append(
                Column(
                    column_name,
                    column_type,
                    primary_key=is_primary,
                )
            )

    return Table(
        table_name,
        metadata,
        *columns
    )


# --------------------------------------------------
# CSV LOADING
# --------------------------------------------------

def load_csv_files():

    files = {
        "products": RAW_DIR / "products.csv",
        "customers": RAW_DIR / "customers.csv",
        "sales_transactions": (
            PROCESSED_DIR / "cleaned_sales.csv"
        ),
        "monthly_sales": (
            PROCESSED_DIR / "monthly_sales.csv"
        ),
    }

    dataframes = {}

    for table_name, file_path in files.items():

        if not file_path.exists():
            raise FileNotFoundError(
                f"Missing dataset: {file_path}"
            )

        df = pd.read_csv(file_path)

        if table_name == "sales_transactions":
            df["transaction_date"] = pd.to_datetime(
                df["transaction_date"]
            )

        dataframes[table_name] = df

    return dataframes


# --------------------------------------------------
# DATABASE SETUP
# --------------------------------------------------

def setup_database():

    print("\nPROJECT RU'YA DATABASE SETUP")
    print("=" * 45)

    dataframes = load_csv_files()

    metadata = MetaData()

    tables = {}

    for table_name, df in dataframes.items():

        tables[table_name] = create_table(
            metadata,
            table_name,
            df
        )

    # Recreate tables in dependency order.
    metadata.drop_all(engine)
    metadata.create_all(engine)

    with engine.begin() as connection:

        for table_name, df in dataframes.items():

            df.to_sql(
                name=table_name,
                con=connection,
                if_exists="append",
                index=False,
                chunksize=5000,
            )

            print(
                f"Loaded {table_name}: "
                f"{len(df):,} records"
            )

    print("\nDatabase created successfully.")
    print(f"Location: {DATABASE_PATH}")

    return dataframes


# --------------------------------------------------
# DATABASE UTILITIES
# --------------------------------------------------

def get_table_counts():

    tables = [
        "products",
        "customers",
        "sales_transactions",
        "monthly_sales",
    ]

    results = {}

    with engine.connect() as connection:

        for table in tables:

            count = connection.execute(
                text(f"SELECT COUNT(*) FROM {table}")
            ).scalar_one()

            results[table] = count

    return results


def execute_query(query):

    with engine.connect() as connection:

        return pd.read_sql(
            text(query),
            connection
        )


# --------------------------------------------------
# ANALYTICAL VALIDATION
# --------------------------------------------------

def validate_database():

    print("\nDATABASE VALIDATION")
    print("=" * 45)

    counts = get_table_counts()

    for table, count in counts.items():
        print(f"{table}: {count:,} records")

    queries = {
        "Gross revenue": """
            SELECT SUM(revenue)
            FROM sales_transactions
        """,

        "Realized revenue": """
            SELECT SUM(revenue)
            FROM sales_transactions
            WHERE is_returned = 0
        """,

        "Realized profit": """
            SELECT SUM(profit)
            FROM sales_transactions
            WHERE is_returned = 0
        """,

        "Total orders": """
            SELECT COUNT(DISTINCT order_id)
            FROM sales_transactions
            WHERE is_returned = 0
        """,

        "Units sold": """
            SELECT SUM(quantity)
            FROM sales_transactions
            WHERE is_returned = 0
        """,

        "Returned transactions": """
            SELECT COUNT(*)
            FROM sales_transactions
            WHERE is_returned = 1
        """,
    }

    print("\nFINANCIAL METRICS")
    print("-" * 45)

    with engine.connect() as connection:

        for label, query in queries.items():

            result = connection.execute(
                text(query)
            ).scalar_one()

            print(f"{label}: {result:,.2f}")

    expected_counts = {
        "products": 74,
        "customers": 5000,
        "sales_transactions": 50000,
        "monthly_sales": 48,
    }

    assert counts == expected_counts, (
        f"Unexpected record counts: {counts}"
    )

    print("\nAll record-count validations passed.")


if __name__ == "__main__":

    setup_database()
    validate_database()