import pandas as pd
from src.preprocessing.process_data import process_upload
from src.analytics.analytics_engine import run_all_analytics
from src.forecasting.forecasting_engine import (
    load_monthly_data, evaluate_models, generate_future_forecast,
)

raw = pd.read_csv(
    "data/showcase/ElectroMart_Chandigarh_Showcase_Dataset.csv",
    encoding="utf-8-sig",
)
cleaned, monthly = process_upload(raw)
results = run_all_analytics(cleaned, export=False)
data = load_monthly_data(monthly)
print(evaluate_models(data, save=False))
print(generate_future_forecast(data, save=False).head())
print("ALL OK")