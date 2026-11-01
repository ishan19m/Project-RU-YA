# PROJECT RU'YA — See Beyond the Numbers

Retail sales analytics and forecasting for **ElectroMart Chandigarh**, a fictional electronics retailer.

RU'YA (vision) is a Python system that turns transactional history into insight: what sold, why it moved, and what is likely to sell next.

## Purpose

Help merchandising and store operations:

- Understand sales performance across products, categories, and time
- Identify patterns, seasonality, and demand drivers
- Produce forecasts that support inventory and planning decisions

## Scope

This repository will cover:

1. Synthetic retail data generation for ElectroMart Chandigarh
2. Cleaning and feature preparation
3. Descriptive analytics and interactive visualization
4. Statistical and machine-learning forecasts
5. A Streamlit dashboard and SQLite-backed storage

Implementation is staged. This commit initializes structure only.

## Technology stack

| Area | Tools |
| --- | --- |
| Language | Python |
| Data | Pandas, NumPy |
| Visualization | Plotly, Matplotlib, Seaborn |
| Application | Streamlit |
| Modeling | Scikit-learn, Statsmodels |
| Persistence | SQLite, SQLAlchemy |

## Project layout

```
PROJECT-RUYA/
├── data/
│   ├── raw/              # original / generated source files
│   └── processed/        # analysis-ready datasets
├── src/
│   ├── data_generation/  # synthetic sales data
│   ├── preprocessing/    # cleaning and transforms
│   ├── analytics/        # descriptive analysis
│   └── forecasting/      # demand models
├── database/             # SQLite database files
├── models/               # persisted trained models
├── notebooks/            # exploration
├── tests/
├── app.py                # Streamlit entry point
├── config.py             # shared settings
└── requirements.txt
```

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Status

Project structure initialized. Analytics, forecasting, and the dashboard are not implemented yet.
