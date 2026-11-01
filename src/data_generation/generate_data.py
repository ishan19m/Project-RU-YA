"""
PROJECT RU'YA — See Beyond the Numbers
Synthetic retail dataset generator for ElectroMart Chandigarh.

THIS DATASET IS SYNTHETIC.
It is fictional data created for analytics and forecasting development.
It does not represent real customers, orders, or ElectroMart operations.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

RANDOM_SEED = 42
N_TRANSACTIONS = 50_000
N_CUSTOMERS = 5_000
START_DATE = pd.Timestamp("2022-01-01")
END_DATE = pd.Timestamp("2025-12-31")
GST_PERCENTAGE = 18.0

ROOT_DIR = Path(__file__).resolve().parents[2]
RAW_DIR = ROOT_DIR / "data" / "raw"

CATEGORIES = [
    "Smartphones",
    "Laptops",
    "Tablets",
    "Televisions",
    "Audio Devices",
    "Home Appliances",
    "Accessories",
]

# Higher weight = stronger baseline demand for the category.
CATEGORY_DEMAND = {
    "Smartphones": 1.35,
    "Laptops": 1.05,
    "Tablets": 0.70,
    "Televisions": 0.85,
    "Audio Devices": 1.10,
    "Home Appliances": 0.90,
    "Accessories": 1.25,
}

# Typical return rates by category (online slightly higher later).
CATEGORY_RETURN_RATE = {
    "Smartphones": 0.035,
    "Laptops": 0.025,
    "Tablets": 0.040,
    "Televisions": 0.020,
    "Audio Devices": 0.055,
    "Home Appliances": 0.030,
    "Accessories": 0.080,
}

# Typical discount ranges (percent) by category.
CATEGORY_DISCOUNT = {
    "Smartphones": (0.0, 8.0),
    "Laptops": (2.0, 12.0),
    "Tablets": (2.0, 10.0),
    "Televisions": (5.0, 18.0),
    "Audio Devices": (5.0, 22.0),
    "Home Appliances": (4.0, 16.0),
    "Accessories": (8.0, 28.0),
}

LOCALITY_CITY = {
    "Sector 17": "Chandigarh",
    "Sector 22": "Chandigarh",
    "Sector 35": "Chandigarh",
    "Sector 43": "Chandigarh",
    "Sector 15": "Chandigarh",
    "Manimajra": "Chandigarh",
    "Mohali": "Mohali",
    "Panchkula": "Panchkula",
    "Zirakpur": "Zirakpur",
}

# Store / delivery localities, weighted toward commercial hubs.
LOCALITY_WEIGHTS = {
    "Sector 17": 0.16,
    "Sector 22": 0.12,
    "Sector 35": 0.13,
    "Sector 43": 0.10,
    "Sector 15": 0.09,
    "Manimajra": 0.08,
    "Mohali": 0.14,
    "Panchkula": 0.10,
    "Zirakpur": 0.08,
}

MALE_FIRST = [
    "Aarav", "Vivaan", "Aditya", "Vihaan", "Arjun", "Sai", "Reyansh", "Krishna",
    "Ishaan", "Shaurya", "Dhruv", "Kabir", "Ritvik", "Atharv", "Rohan", "Kunal",
    "Harsh", "Nikhil", "Manan", "Yash", "Gaurav", "Varun", "Aman", "Rahul",
    "Siddharth", "Karthik", "Abhinav", "Dev", "Aniket", "Parth",
]
FEMALE_FIRST = [
    "Aanya", "Diya", "Ananya", "Isha", "Kiara", "Myra", "Saanvi", "Aadhya",
    "Pari", "Riya", "Anvi", "Navya", "Meera", "Ira", "Aditi", "Nisha",
    "Pooja", "Neha", "Shreya", "Kavya", "Tanvi", "Simran", "Priya", "Sneha",
    "Ishita", "Tanya", "Pallavi", "Kritika", "Aishwarya", "Jhanvi",
]
LAST_NAMES = [
    "Sharma", "Singh", "Kaur", "Verma", "Gupta", "Kapoor", "Malhotra", "Chopra",
    "Bansal", "Arora", "Khanna", "Joshi", "Mehta", "Aggarwal", "Bhatia", "Sethi",
    "Gill", "Dhawan", "Chawla", "Thakur", "Rana", "Sandhu", "Ahuja", "Bedi",
]


def money(values: np.ndarray | pd.Series | float) -> np.ndarray | float:
    """Round currency values to two decimal places."""
    return np.round(values, 2)


def build_product_catalog() -> list[dict]:
    """Return a fixed catalog of 72 electronics SKUs with realistic INR prices."""
    # unit_cost is below selling_price; margins vary by category.
    return [
        # Smartphones
        {"product_name": "Samsung Galaxy S24", "category": "Smartphones", "subcategory": "Flagship", "brand": "Samsung", "unit_cost": 58990, "selling_price": 74999},
        {"product_name": "Samsung Galaxy S23 FE", "category": "Smartphones", "subcategory": "Flagship", "brand": "Samsung", "unit_cost": 38990, "selling_price": 49999},
        {"product_name": "Samsung Galaxy A55", "category": "Smartphones", "subcategory": "Mid-range", "brand": "Samsung", "unit_cost": 27990, "selling_price": 35999},
        {"product_name": "Samsung Galaxy A15", "category": "Smartphones", "subcategory": "Budget", "brand": "Samsung", "unit_cost": 11990, "selling_price": 15999},
        {"product_name": "Samsung Galaxy M35", "category": "Smartphones", "subcategory": "Budget", "brand": "Samsung", "unit_cost": 13990, "selling_price": 18499},
        {"product_name": "Apple iPhone 16", "category": "Smartphones", "subcategory": "Flagship", "brand": "Apple", "unit_cost": 69990, "selling_price": 79900},
        {"product_name": "Apple iPhone 15", "category": "Smartphones", "subcategory": "Flagship", "brand": "Apple", "unit_cost": 58990, "selling_price": 69900},
        {"product_name": "Apple iPhone 14", "category": "Smartphones", "subcategory": "Flagship", "brand": "Apple", "unit_cost": 48990, "selling_price": 59900},
        {"product_name": "Apple iPhone 13", "category": "Smartphones", "subcategory": "Mid-range", "brand": "Apple", "unit_cost": 41990, "selling_price": 52900},
        {"product_name": "Xiaomi 14", "category": "Smartphones", "subcategory": "Flagship", "brand": "Xiaomi", "unit_cost": 42990, "selling_price": 54999},
        {"product_name": "Xiaomi 13T", "category": "Smartphones", "subcategory": "Mid-range", "brand": "Xiaomi", "unit_cost": 28990, "selling_price": 37999},
        {"product_name": "Redmi Note 13 Pro", "category": "Smartphones", "subcategory": "Mid-range", "brand": "Xiaomi", "unit_cost": 17990, "selling_price": 23999},
        {"product_name": "Redmi 13C", "category": "Smartphones", "subcategory": "Budget", "brand": "Xiaomi", "unit_cost": 7290, "selling_price": 9999},
        {"product_name": "Samsung Galaxy Z Flip5", "category": "Smartphones", "subcategory": "Flagship", "brand": "Samsung", "unit_cost": 78990, "selling_price": 99999},
        # Laptops
        {"product_name": "HP Pavilion 15", "category": "Laptops", "subcategory": "Consumer", "brand": "HP", "unit_cost": 44990, "selling_price": 58990},
        {"product_name": "HP Victus 16", "category": "Laptops", "subcategory": "Gaming", "brand": "HP", "unit_cost": 62990, "selling_price": 79990},
        {"product_name": "HP 15s", "category": "Laptops", "subcategory": "Budget", "brand": "HP", "unit_cost": 31990, "selling_price": 41990},
        {"product_name": "Dell Inspiron 14", "category": "Laptops", "subcategory": "Consumer", "brand": "Dell", "unit_cost": 42990, "selling_price": 56990},
        {"product_name": "Dell XPS 13", "category": "Laptops", "subcategory": "Premium", "brand": "Dell", "unit_cost": 98990, "selling_price": 129990},
        {"product_name": "Dell Vostro 15", "category": "Laptops", "subcategory": "Business", "brand": "Dell", "unit_cost": 38990, "selling_price": 51990},
        {"product_name": "Lenovo IdeaPad Slim 3", "category": "Laptops", "subcategory": "Consumer", "brand": "Lenovo", "unit_cost": 33990, "selling_price": 44990},
        {"product_name": "Lenovo ThinkPad E14", "category": "Laptops", "subcategory": "Business", "brand": "Lenovo", "unit_cost": 52990, "selling_price": 68990},
        {"product_name": "Lenovo Legion 5", "category": "Laptops", "subcategory": "Gaming", "brand": "Lenovo", "unit_cost": 74990, "selling_price": 96990},
        {"product_name": "Apple MacBook Air 13 M2", "category": "Laptops", "subcategory": "Premium", "brand": "Apple", "unit_cost": 84990, "selling_price": 99990},
        {"product_name": "Apple MacBook Pro 14", "category": "Laptops", "subcategory": "Premium", "brand": "Apple", "unit_cost": 149990, "selling_price": 169900},
        {"product_name": "Xiaomi Notebook Pro", "category": "Laptops", "subcategory": "Consumer", "brand": "Xiaomi", "unit_cost": 42990, "selling_price": 54999},
        # Tablets
        {"product_name": "Apple iPad 10th Gen", "category": "Tablets", "subcategory": "Wi-Fi", "brand": "Apple", "unit_cost": 28990, "selling_price": 39900},
        {"product_name": "Apple iPad Air M2", "category": "Tablets", "subcategory": "Premium", "brand": "Apple", "unit_cost": 48990, "selling_price": 59900},
        {"product_name": "Apple iPad Mini", "category": "Tablets", "subcategory": "Compact", "brand": "Apple", "unit_cost": 38990, "selling_price": 49900},
        {"product_name": "Samsung Galaxy Tab S9", "category": "Tablets", "subcategory": "Premium", "brand": "Samsung", "unit_cost": 52990, "selling_price": 67999},
        {"product_name": "Samsung Galaxy Tab A9+", "category": "Tablets", "subcategory": "Budget", "brand": "Samsung", "unit_cost": 15990, "selling_price": 21999},
        {"product_name": "Lenovo Tab M11", "category": "Tablets", "subcategory": "Budget", "brand": "Lenovo", "unit_cost": 11990, "selling_price": 16999},
        {"product_name": "Xiaomi Pad 6", "category": "Tablets", "subcategory": "Mid-range", "brand": "Xiaomi", "unit_cost": 18990, "selling_price": 26999},
        {"product_name": "Samsung Galaxy Tab S9 FE", "category": "Tablets", "subcategory": "Mid-range", "brand": "Samsung", "unit_cost": 27990, "selling_price": 36999},
        # Televisions
        {"product_name": "Samsung 43-inch Crystal 4K", "category": "Televisions", "subcategory": "LED", "brand": "Samsung", "unit_cost": 22990, "selling_price": 31990},
        {"product_name": "Samsung 55-inch QLED 4K", "category": "Televisions", "subcategory": "QLED", "brand": "Samsung", "unit_cost": 48990, "selling_price": 64990},
        {"product_name": "Samsung 65-inch QLED 4K", "category": "Televisions", "subcategory": "QLED", "brand": "Samsung", "unit_cost": 72990, "selling_price": 94990},
        {"product_name": "Sony Bravia 43-inch 4K", "category": "Televisions", "subcategory": "LED", "brand": "Sony", "unit_cost": 34990, "selling_price": 46990},
        {"product_name": "Sony Bravia 55-inch 4K", "category": "Televisions", "subcategory": "LED", "brand": "Sony", "unit_cost": 54990, "selling_price": 72990},
        {"product_name": "Sony Bravia 65-inch OLED", "category": "Televisions", "subcategory": "OLED", "brand": "Sony", "unit_cost": 129990, "selling_price": 169990},
        {"product_name": "LG 43-inch UHD 4K", "category": "Televisions", "subcategory": "LED", "brand": "LG", "unit_cost": 21990, "selling_price": 30990},
        {"product_name": "LG 55-inch OLED", "category": "Televisions", "subcategory": "OLED", "brand": "LG", "unit_cost": 89990, "selling_price": 119990},
        {"product_name": "Xiaomi Smart TV 43-inch", "category": "Televisions", "subcategory": "LED", "brand": "Xiaomi", "unit_cost": 17990, "selling_price": 24999},
        {"product_name": "Xiaomi Smart TV 55-inch", "category": "Televisions", "subcategory": "LED", "brand": "Xiaomi", "unit_cost": 26990, "selling_price": 35999},
        # Audio Devices
        {"product_name": "Sony WH-1000XM5", "category": "Audio Devices", "subcategory": "Headphones", "brand": "Sony", "unit_cost": 18990, "selling_price": 29990},
        {"product_name": "Sony WF-1000XM5", "category": "Audio Devices", "subcategory": "Earbuds", "brand": "Sony", "unit_cost": 14990, "selling_price": 24990},
        {"product_name": "Sony SRS-XB100", "category": "Audio Devices", "subcategory": "Speakers", "brand": "Sony", "unit_cost": 3290, "selling_price": 4990},
        {"product_name": "boAt Airdopes 141", "category": "Audio Devices", "subcategory": "Earbuds", "brand": "boAt", "unit_cost": 790, "selling_price": 1299},
        {"product_name": "boAt Rockerz 255", "category": "Audio Devices", "subcategory": "Neckband", "brand": "boAt", "unit_cost": 690, "selling_price": 1199},
        {"product_name": "boAt Stone 350", "category": "Audio Devices", "subcategory": "Speakers", "brand": "boAt", "unit_cost": 1290, "selling_price": 1999},
        {"product_name": "Samsung Galaxy Buds2 Pro", "category": "Audio Devices", "subcategory": "Earbuds", "brand": "Samsung", "unit_cost": 8990, "selling_price": 13990},
        {"product_name": "Apple AirPods Pro 2", "category": "Audio Devices", "subcategory": "Earbuds", "brand": "Apple", "unit_cost": 17990, "selling_price": 24900},
        {"product_name": "Apple AirPods 3", "category": "Audio Devices", "subcategory": "Earbuds", "brand": "Apple", "unit_cost": 12990, "selling_price": 19900},
        {"product_name": "LG XBOOM Go", "category": "Audio Devices", "subcategory": "Speakers", "brand": "LG", "unit_cost": 4490, "selling_price": 6990},
        # Home Appliances
        {"product_name": "LG 1.5 Ton Split AC", "category": "Home Appliances", "subcategory": "Air Conditioner", "brand": "LG", "unit_cost": 28990, "selling_price": 38990},
        {"product_name": "Samsung 1.5 Ton Split AC", "category": "Home Appliances", "subcategory": "Air Conditioner", "brand": "Samsung", "unit_cost": 27990, "selling_price": 37990},
        {"product_name": "LG 260L Refrigerator", "category": "Home Appliances", "subcategory": "Refrigerator", "brand": "LG", "unit_cost": 18990, "selling_price": 26990},
        {"product_name": "Samsung 236L Refrigerator", "category": "Home Appliances", "subcategory": "Refrigerator", "brand": "Samsung", "unit_cost": 17990, "selling_price": 25490},
        {"product_name": "LG 7kg Front Load WM", "category": "Home Appliances", "subcategory": "Washing Machine", "brand": "LG", "unit_cost": 22990, "selling_price": 31990},
        {"product_name": "Samsung 7kg Front Load WM", "category": "Home Appliances", "subcategory": "Washing Machine", "brand": "Samsung", "unit_cost": 21990, "selling_price": 30990},
        {"product_name": "LG 28L Convection Microwave", "category": "Home Appliances", "subcategory": "Microwave", "brand": "LG", "unit_cost": 8990, "selling_price": 12990},
        {"product_name": "Xiaomi Smart Air Purifier", "category": "Home Appliances", "subcategory": "Air Purifier", "brand": "Xiaomi", "unit_cost": 6990, "selling_price": 9999},
        # Accessories
        {"product_name": "Apple MagSafe Charger", "category": "Accessories", "subcategory": "Charging", "brand": "Apple", "unit_cost": 3290, "selling_price": 4500},
        {"product_name": "Samsung 25W Travel Adapter", "category": "Accessories", "subcategory": "Charging", "brand": "Samsung", "unit_cost": 990, "selling_price": 1699},
        {"product_name": "Xiaomi 20000mAh Power Bank", "category": "Accessories", "subcategory": "Power Bank", "brand": "Xiaomi", "unit_cost": 1290, "selling_price": 1999},
        {"product_name": "boAt 10000mAh Power Bank", "category": "Accessories", "subcategory": "Power Bank", "brand": "boAt", "unit_cost": 790, "selling_price": 1299},
        {"product_name": "HP Wireless Mouse", "category": "Accessories", "subcategory": "Peripherals", "brand": "HP", "unit_cost": 490, "selling_price": 899},
        {"product_name": "Dell KM3322W Keyboard Mouse", "category": "Accessories", "subcategory": "Peripherals", "brand": "Dell", "unit_cost": 1090, "selling_price": 1799},
        {"product_name": "Lenovo 512GB SSD", "category": "Accessories", "subcategory": "Storage", "brand": "Lenovo", "unit_cost": 2890, "selling_price": 4299},
        {"product_name": "Sony 64GB microSD", "category": "Accessories", "subcategory": "Storage", "brand": "Sony", "unit_cost": 490, "selling_price": 799},
        {"product_name": "Samsung 1TB T7 SSD", "category": "Accessories", "subcategory": "Storage", "brand": "Samsung", "unit_cost": 6490, "selling_price": 8999},
        {"product_name": "Apple USB-C Cable", "category": "Accessories", "subcategory": "Cables", "brand": "Apple", "unit_cost": 1290, "selling_price": 1900},
        {"product_name": "boAt USB-C Cable 3-Pack", "category": "Accessories", "subcategory": "Cables", "brand": "boAt", "unit_cost": 290, "selling_price": 499},
        {"product_name": "Xiaomi Silicone Phone Case", "category": "Accessories", "subcategory": "Cases", "brand": "Xiaomi", "unit_cost": 190, "selling_price": 399},
    ]


def generate_products(rng: np.random.Generator) -> pd.DataFrame:
    """Build the product master with IDs and popularity weights."""
    catalog = build_product_catalog()
    n = len(catalog)
    assert 60 <= n <= 80, "Product catalog must contain 60–80 SKUs."

    products = pd.DataFrame(catalog)
    products.insert(0, "product_id", [f"PRD{i:04d}" for i in range(1, n + 1)])
    products["unit_cost"] = money(products["unit_cost"].astype(float))
    products["selling_price"] = money(products["selling_price"].astype(float))

    # Zipf-like popularity so a few SKUs dominate each category.
    ranks = np.arange(1, n + 1)
    rng.shuffle(ranks)
    popularity = 1.0 / np.power(ranks, 0.65)
    cat_boost = products["category"].map(CATEGORY_DEMAND).astype(float).to_numpy()
    products["popularity"] = popularity * cat_boost
    return products


def generate_customers(rng: np.random.Generator) -> pd.DataFrame:
    """Build 5,000 customers across Chandigarh and nearby cities."""
    localities = list(LOCALITY_CITY.keys())
    loc_p = np.array([LOCALITY_WEIGHTS[loc] for loc in localities], dtype=float)
    loc_p /= loc_p.sum()

    locality = rng.choice(localities, size=N_CUSTOMERS, p=loc_p)
    city = np.array([LOCALITY_CITY[loc] for loc in locality])

    # Age peaks in the 25–40 working-age band.
    age = np.clip(rng.normal(loc=34, scale=11, size=N_CUSTOMERS).round().astype(int), 18, 72)

    gender_p = np.array([0.51, 0.47, 0.02])
    gender = rng.choice(["Male", "Female", "Other"], size=N_CUSTOMERS, p=gender_p)

    first_pool = {
        "Male": MALE_FIRST,
        "Female": FEMALE_FIRST,
        "Other": MALE_FIRST + FEMALE_FIRST,
    }
    names = []
    for g in gender:
        first = rng.choice(first_pool[g])
        last = rng.choice(LAST_NAMES)
        names.append(f"{first} {last}")

    # Segment depends partly on age (older customers slightly more premium).
    segment = rng.choice(["Premium", "Standard", "Value"], size=N_CUSTOMERS, p=[0.22, 0.53, 0.25])
    premium_tilt = (age >= 42) & (rng.random(N_CUSTOMERS) < 0.18)
    value_tilt = (age <= 24) & (rng.random(N_CUSTOMERS) < 0.22)
    segment = np.where(premium_tilt, "Premium", segment)
    segment = np.where(value_tilt & (segment != "Premium"), "Value", segment)

    # Pareto-like purchase frequency: a minority of customers buy often.
    frequency_weight = rng.pareto(a=1.6, size=N_CUSTOMERS) + 0.15
    frequency_weight = np.clip(frequency_weight, 0.05, None)

    customers = pd.DataFrame(
        {
            "customer_id": [f"CUS{i:05d}" for i in range(1, N_CUSTOMERS + 1)],
            "customer_name": names,
            "age": age,
            "gender": gender,
            "city": city,
            "locality": locality,
            "customer_segment": segment,
            "frequency_weight": frequency_weight,
        }
    )
    return customers


def _festival_windows() -> list[tuple[pd.Timestamp, pd.Timestamp, float]]:
    """Named Indian festival / promo windows with demand multipliers."""
    peaks = [
        # Diwali week (strongest electronics season)
        ("2022-10-18", "2022-10-30", 2.40),
        ("2023-11-06", "2023-11-18", 2.40),
        ("2024-10-26", "2024-11-07", 2.40),
        ("2025-10-14", "2025-10-26", 2.40),
        # Dussehra / pre-Diwali shopping
        ("2022-09-28", "2022-10-08", 1.70),
        ("2023-10-16", "2023-10-26", 1.70),
        ("2024-10-04", "2024-10-14", 1.70),
        ("2025-09-24", "2025-10-04", 1.70),
        # Holi
        ("2022-03-14", "2022-03-20", 1.35),
        ("2023-03-04", "2023-03-10", 1.35),
        ("2024-03-21", "2024-03-27", 1.35),
        ("2025-03-10", "2025-03-16", 1.35),
        # Republic Day / Independence Day / Christmas
        ("2022-01-22", "2022-01-28", 1.30),
        ("2023-01-22", "2023-01-28", 1.30),
        ("2024-01-22", "2024-01-28", 1.30),
        ("2025-01-22", "2025-01-28", 1.30),
        ("2022-08-12", "2022-08-16", 1.25),
        ("2023-08-13", "2023-08-17", 1.25),
        ("2024-08-13", "2024-08-17", 1.25),
        ("2025-08-13", "2025-08-17", 1.25),
        # Great Indian Festival / year-end promotions
        ("2022-10-01", "2022-10-12", 1.85),
        ("2023-10-01", "2023-10-12", 1.85),
        ("2024-10-01", "2024-10-12", 1.85),
        ("2025-10-01", "2025-10-12", 1.85),
        ("2022-12-20", "2022-12-31", 1.55),
        ("2023-12-20", "2023-12-31", 1.55),
        ("2024-12-20", "2024-12-31", 1.55),
        ("2025-12-20", "2025-12-31", 1.55),
        ("2023-01-01", "2023-01-05", 1.20),
        ("2024-01-01", "2024-01-05", 1.20),
        ("2025-01-01", "2025-01-05", 1.20),
    ]
    return [
        (pd.Timestamp(start), pd.Timestamp(end), multiplier)
        for start, end, multiplier in peaks
    ]


def date_demand_weights(dates: pd.DatetimeIndex) -> np.ndarray:
    """Non-uniform daily demand: weekends, festivals, year-end, mild growth."""
    weights = np.ones(len(dates), dtype=float)

    weekday = dates.day_of_week
    weights[weekday == 5] *= 1.28  # Saturday
    weights[weekday == 6] *= 1.16  # Sunday
    weights[weekday == 4] *= 1.08  # Friday

    # Mild year-over-year growth in store traffic.
    year = dates.year.to_numpy()
    weights *= 1.0 + 0.06 * (year - 2022)

    month = dates.month.to_numpy()
    # Wedding / winter electronics season.
    weights[np.isin(month, [11, 12, 1, 2])] *= 1.12
    # Summer cooling demand is applied later at category level; mild overall lift.
    weights[np.isin(month, [5, 6])] *= 1.06

    for start, end, multiplier in _festival_windows():
        mask = (dates >= start) & (dates <= end)
        weights[mask] *= multiplier

    return weights


def category_seasonality(dates: pd.DatetimeIndex) -> dict[str, np.ndarray]:
    """Per-day category multipliers (ACs in summer, TVs around sports/festivals)."""
    n = len(dates)
    month = dates.month.to_numpy()
    festival = np.zeros(n, dtype=bool)
    for start, end, _ in _festival_windows():
        festival |= (dates >= start) & (dates <= end)

    factors = {cat: np.ones(n, dtype=float) for cat in CATEGORIES}
    factors["Home Appliances"][np.isin(month, [4, 5, 6, 7])] *= 1.55
    factors["Televisions"][festival] *= 1.35
    factors["Televisions"][np.isin(month, [10, 11, 12])] *= 1.20
    factors["Smartphones"][festival] *= 1.40
    factors["Smartphones"][np.isin(month, [9, 10])] *= 1.15  # launch season
    factors["Laptops"][np.isin(month, [5, 6, 7])] *= 1.20  # back-to-college
    factors["Accessories"][festival] *= 1.25
    factors["Audio Devices"][festival] *= 1.20
    factors["Tablets"][np.isin(month, [5, 6])] *= 1.15
    return factors


def sample_from_weighted_rows(row_weights: np.ndarray, rng: np.random.Generator) -> np.ndarray:
    """Sample one column index per row from a (n, k) weight matrix."""
    normalized = row_weights / row_weights.sum(axis=1, keepdims=True)
    cumulative = np.cumsum(normalized, axis=1)
    draws = rng.random(row_weights.shape[0])
    return (draws[:, None] <= cumulative).argmax(axis=1)


def generate_transactions(
    products: pd.DataFrame,
    customers: pd.DataFrame,
    rng: np.random.Generator,
) -> pd.DataFrame:
    """Generate 50,000 line-item transactions with consistent financials."""
    n = N_TRANSACTIONS
    calendar = pd.date_range(START_DATE, END_DATE, freq="D")
    date_p = date_demand_weights(calendar)
    date_p /= date_p.sum()
    txn_dates = pd.to_datetime(rng.choice(calendar.to_numpy(), size=n, p=date_p))

    # Bundle some line items into shared orders (same customer, date, channel).
    n_orders = int(n * 0.82)
    raw_order_ids = rng.integers(1, n_orders + 1, size=n)
    canonical = pd.Series(np.arange(n)).groupby(raw_order_ids).transform("first").to_numpy()
    txn_dates = txn_dates[canonical]

    cust_p = customers["frequency_weight"].to_numpy(dtype=float).copy()
    cust_p /= cust_p.sum()
    customer_pos = rng.choice(len(customers), size=n, p=cust_p)[canonical]
    sales_channel = rng.choice(["Offline", "Online"], size=n, p=[0.62, 0.38])[canonical]

    # Sample category using date-aware demand, then a product in that category.
    season = category_seasonality(pd.DatetimeIndex(txn_dates))
    cat_weights = np.column_stack(
        [CATEGORY_DEMAND[cat] * season[cat] for cat in CATEGORIES]
    )
    sampled_cat_idx = sample_from_weighted_rows(cat_weights, rng)
    sampled_categories = np.array(CATEGORIES)[sampled_cat_idx]

    product_cats = products["category"].to_numpy()
    popularity = products["popularity"].to_numpy()
    chosen_product_pos = np.empty(n, dtype=int)
    for cat in CATEGORIES:
        mask = sampled_categories == cat
        if not mask.any():
            continue
        in_cat = np.flatnonzero(product_cats == cat)
        weights = popularity[in_cat]
        weights = weights / weights.sum()
        chosen_product_pos[mask] = rng.choice(in_cat, size=int(mask.sum()), p=weights)

    premium_products = np.flatnonzero(
        products["selling_price"].to_numpy() >= products["selling_price"].quantile(0.65)
    )
    value_products = np.flatnonzero(
        products["selling_price"].to_numpy() <= products["selling_price"].quantile(0.45)
    )
    segments = customers["customer_segment"].to_numpy()[customer_pos]
    resample_draw = rng.random(n)
    premium_mask = (segments == "Premium") & (resample_draw < 0.45)
    value_mask = (segments == "Value") & (resample_draw < 0.40)
    if premium_mask.any():
        chosen_product_pos[premium_mask] = rng.choice(premium_products, size=int(premium_mask.sum()))
    if value_mask.any():
        chosen_product_pos[value_mask] = rng.choice(value_products, size=int(value_mask.sum()))

    prod = products.iloc[chosen_product_pos].reset_index(drop=True)
    cust = customers.iloc[customer_pos].reset_index(drop=True)
    categories = prod["category"].to_numpy()

    # Quantity: accessories sell in small bundles; big-ticket items usually 1.
    quantity = np.ones(n, dtype=int)
    qty_draw = rng.random(n)
    accessory = categories == "Accessories"
    audio = categories == "Audio Devices"
    quantity[accessory & (qty_draw < 0.35)] = 2
    quantity[accessory & (qty_draw >= 0.35) & (qty_draw < 0.48)] = 3
    quantity[accessory & (qty_draw >= 0.48) & (qty_draw < 0.54)] = 4
    quantity[audio & (qty_draw < 0.12)] = 2
    quantity[~accessory & ~audio & (qty_draw < 0.04)] = 2

    unit_price = prod["selling_price"].to_numpy(dtype=float)
    unit_cost = prod["unit_cost"].to_numpy(dtype=float)

    # Discount: category range + festival lift + small noise.
    low = np.array([CATEGORY_DISCOUNT[c][0] for c in categories])
    high = np.array([CATEGORY_DISCOUNT[c][1] for c in categories])
    discount_percentage = rng.uniform(low, high)
    festival_mask = np.zeros(n, dtype=bool)
    for start, end, _ in _festival_windows():
        festival_mask |= (txn_dates >= start) & (txn_dates <= end)
    discount_percentage[festival_mask] += rng.uniform(4.0, 12.0, size=int(festival_mask.sum()))
    weekend = pd.DatetimeIndex(txn_dates).day_of_week >= 5
    discount_percentage[weekend] += rng.uniform(0.0, 2.5, size=int(weekend.sum()))
    discount_percentage = np.clip(np.round(discount_percentage, 2), 0.0, 40.0)

    gross_sales = money(quantity * unit_price)
    discount_amount = money(gross_sales * discount_percentage / 100.0)
    net_sales = money(gross_sales - discount_amount)
    total_cost = money(quantity * unit_cost)
    gross_profit = money(net_sales - total_cost)
    gst_percentage = np.full(n, GST_PERCENTAGE)
    gst_amount = money(net_sales * gst_percentage / 100.0)
    total_amount = money(net_sales + gst_amount)

    payment_method = np.empty(n, dtype=object)
    online = sales_channel == "Online"
    payment_method[online] = rng.choice(
        ["UPI", "Credit Card", "Debit Card", "Digital Wallet", "Net Banking"],
        size=int(online.sum()),
        p=[0.52, 0.18, 0.14, 0.11, 0.05],
    )
    payment_method[~online] = rng.choice(
        ["UPI", "Cash", "Debit Card", "Credit Card", "Digital Wallet"],
        size=int((~online).sum()),
        p=[0.38, 0.28, 0.16, 0.12, 0.06],
    )

    locality = cust["locality"].to_numpy(dtype=object)
    travel = (~online) & (rng.random(n) < 0.12)
    locality[travel] = "Sector 17"

    base_return = np.array([CATEGORY_RETURN_RATE[c] for c in categories])
    return_p = np.where(online, base_return * 1.35, base_return)
    is_returned = rng.random(n) < return_p
    order_status = np.where(is_returned, "Returned", "Completed")
    cancel_mask = (~is_returned) & (rng.random(n) < 0.015)
    order_status[cancel_mask] = "Cancelled"

    transactions = pd.DataFrame(
        {
            "transaction_id": [f"TXN{i:07d}" for i in range(1, n + 1)],
            "order_id": [f"ORD{oid:06d}" for oid in raw_order_ids],
            "transaction_date": pd.to_datetime(txn_dates).strftime("%Y-%m-%d"),
            "customer_id": cust["customer_id"].to_numpy(),
            "product_id": prod["product_id"].to_numpy(),
            "quantity": quantity,
            "unit_price": unit_price,
            "gross_sales": gross_sales,
            "discount_percentage": discount_percentage,
            "discount_amount": discount_amount,
            "net_sales": net_sales,
            "unit_cost": unit_cost,
            "total_cost": total_cost,
            "gross_profit": gross_profit,
            "gst_percentage": gst_percentage,
            "gst_amount": gst_amount,
            "total_amount": total_amount,
            "payment_method": payment_method,
            "sales_channel": sales_channel,
            "locality": locality,
            "order_status": order_status,
            "is_returned": is_returned,
        }
    )
    return transactions


def validate_dataset(
    products: pd.DataFrame,
    customers: pd.DataFrame,
    transactions: pd.DataFrame,
) -> dict:
    """Run integrity checks and return summary metrics."""
    product_cols = [
        "product_id",
        "product_name",
        "category",
        "subcategory",
        "brand",
        "unit_cost",
        "selling_price",
    ]
    customer_cols = [
        "customer_id",
        "customer_name",
        "age",
        "gender",
        "city",
        "locality",
        "customer_segment",
    ]
    products = products[product_cols]
    customers = customers[customer_cols]

    dates = pd.to_datetime(transactions["transaction_date"])
    missing = int(
        products.isna().sum().sum()
        + customers.isna().sum().sum()
        + transactions.isna().sum().sum()
    )
    dup_txn = int(transactions["transaction_id"].duplicated().sum())

    expected_gross = money(transactions["quantity"] * transactions["unit_price"])
    expected_disc = money(transactions["gross_sales"] * transactions["discount_percentage"] / 100.0)
    expected_net = money(transactions["gross_sales"] - transactions["discount_amount"])
    expected_cost = money(transactions["quantity"] * transactions["unit_cost"])
    expected_profit = money(transactions["net_sales"] - transactions["total_cost"])
    expected_gst = money(transactions["net_sales"] * transactions["gst_percentage"] / 100.0)
    expected_total = money(transactions["net_sales"] + transactions["gst_amount"])

    assert len(transactions) == N_TRANSACTIONS
    assert 60 <= len(products) <= 80
    assert len(customers) == N_CUSTOMERS
    assert products["product_id"].is_unique
    assert customers["customer_id"].is_unique
    assert dup_txn == 0
    assert missing == 0
    assert dates.min() >= START_DATE
    assert dates.max() <= END_DATE
    assert transactions["customer_id"].isin(customers["customer_id"]).all()
    assert transactions["product_id"].isin(products["product_id"]).all()
    assert (transactions["quantity"] > 0).all()
    assert (transactions["unit_price"] > 0).all()
    assert (transactions["unit_cost"] > 0).all()
    assert (products["selling_price"] > products["unit_cost"]).all()
    assert (transactions["discount_percentage"] >= 0).all()
    assert (transactions["gst_percentage"] >= 0).all()
    assert np.allclose(transactions["gross_sales"], expected_gross, atol=0.011)
    assert np.allclose(transactions["discount_amount"], expected_disc, atol=0.011)
    assert np.allclose(transactions["net_sales"], expected_net, atol=0.011)
    assert np.allclose(transactions["total_cost"], expected_cost, atol=0.011)
    assert np.allclose(transactions["gross_profit"], expected_profit, atol=0.011)
    assert np.allclose(transactions["gst_amount"], expected_gst, atol=0.011)
    assert np.allclose(transactions["total_amount"], expected_total, atol=0.011)
    returned = transactions["is_returned"].astype(bool)
    assert (transactions.loc[returned, "order_status"] == "Returned").all()

    summary = {
        "n_transactions": len(transactions),
        "n_products": len(products),
        "n_customers": len(customers),
        "date_min": dates.min().strftime("%Y-%m-%d"),
        "date_max": dates.max().strftime("%Y-%m-%d"),
        "gross_sales": float(transactions["gross_sales"].sum()),
        "net_sales": float(transactions["net_sales"].sum()),
        "gross_profit": float(transactions["gross_profit"].sum()),
        "return_rate": float(returned.mean()),
        "missing_values": missing,
        "duplicate_transaction_ids": dup_txn,
    }
    return summary, products, customers


def save_csv(df: pd.DataFrame, path: Path) -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)


def print_summary(summary: dict) -> None:
    print("=" * 64)
    print("PROJECT RU'YA — SYNTHETIC DATASET GENERATION COMPLETE")
    print("THIS DATASET IS SYNTHETIC AND FICTIONAL.")
    print("=" * 64)
    print(f"Transaction records     : {summary['n_transactions']:,}")
    print(f"Products                : {summary['n_products']:,}")
    print(f"Customers               : {summary['n_customers']:,}")
    print(f"Date range              : {summary['date_min']} to {summary['date_max']}")
    print(f"Total gross sales (INR) : {summary['gross_sales']:,.2f}")
    print(f"Total net sales (INR)   : {summary['net_sales']:,.2f}")
    print(f"Total gross profit (INR): {summary['gross_profit']:,.2f}")
    print(f"Return rate             : {summary['return_rate']:.2%}")
    print(f"Missing values          : {summary['missing_values']}")
    print(f"Duplicate transaction IDs: {summary['duplicate_transaction_ids']}")
    print("=" * 64)


def main() -> None:
    print("PROJECT RU'YA — generating SYNTHETIC ElectroMart Chandigarh data...")
    rng = np.random.default_rng(RANDOM_SEED)

    products = generate_products(rng)
    customers = generate_customers(rng)
    transactions = generate_transactions(products, customers, rng)
    summary, products, customers = validate_dataset(products, customers, transactions)

    save_csv(products, RAW_DIR / "products.csv")
    save_csv(customers, RAW_DIR / "customers.csv")
    save_csv(transactions, RAW_DIR / "sales_transactions.csv")

    print_summary(summary)
    print(f"Wrote {RAW_DIR / 'products.csv'}")
    print(f"Wrote {RAW_DIR / 'customers.csv'}")
    print(f"Wrote {RAW_DIR / 'sales_transactions.csv'}")


if __name__ == "__main__":
    main()
