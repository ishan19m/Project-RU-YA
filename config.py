"""PROJECT RU'YA — shared configuration."""

import os
import tempfile
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent

# Built-in sample (read-only). Never write here: Vercel's filesystem is read-only.
SAMPLE_DB_PATH = ROOT_DIR / "database" / "ruya.db"
SHOWCASE_CSV = (
    ROOT_DIR / "data" / "showcase"
    / "ElectroMart_Chandigarh_Showcase_Dataset.csv"
)

# Only /tmp is writable on Vercel.
TMP_DIR = Path(tempfile.gettempdir())

# Vercel rejects request bodies above 4.5 MB.
MAX_UPLOAD_BYTES = 4 * 1024 * 1024

# Comma-separated list of allowed frontend origins.
ALLOWED_ORIGINS = [
    o.strip()
    for o in os.getenv(
        "ALLOWED_ORIGINS", "http://localhost:3000"
    ).split(",")
    if o.strip()
]

MIN_FORECAST_MONTHS = 36  # same rule the forecasting engine already uses

# Uploaded CSV header (lowercased, spaces -> "_") -> internal column name.
COLUMN_MAP = {
    "order_id": "order_id",
    "order_date": "transaction_date",
    "transaction_date": "transaction_date",
    "customer_id": "customer_id",
    "customer_segment": "customer_segment",
    "area": "sale_locality",
    "city": "city",
    "sales_channel": "sales_channel",
    "product_id": "product_id",
    "product_name": "product_name",
    "brand": "brand",
    "category": "category",
    "quantity": "quantity",
    "unit_price": "unit_price",
    "cost_price": "unit_cost",
    "discount_percent": "discount_percentage",
    "discount_percentage": "discount_percentage",
    "discount_amount": "discount_amount",
    "revenue_excl_gst": "revenue",
    "revenue": "revenue",
    "profit_before_returns": "profit",
    "profit": "profit",
    "return_status": "return_status",
    "is_returned": "is_returned",
    "payment_mode": "payment_method",
    "payment_method": "payment_method",
}

# Upload is rejected with a clear message if any of these are missing
# after mapping.
REQUIRED_COLUMNS = [
    "order_id",
    "transaction_date",
    "customer_id",
    "product_name",
    "category",
    "quantity",
    "revenue",
    "profit",
]