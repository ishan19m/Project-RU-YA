import os
import warnings

import numpy as np
import pandas as pd

from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error

from statsmodels.tsa.holtwinters import ExponentialSmoothing

warnings.filterwarnings("ignore")


BASE_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../../")
)

DATA_PATH = os.path.join(
    BASE_DIR, "data", "processed", "monthly_sales.csv"
)

OUTPUT_DIR = os.path.join(
    BASE_DIR, "data", "processed", "forecasting"
)




def load_monthly_data(monthly_df=None):

    df = pd.read_csv(DATA_PATH) if monthly_df is None else monthly_df.copy()

    df["month"] = pd.to_datetime(df["month"])

    df = df.sort_values("month").reset_index(drop=True)

    df["realized_revenue"] = pd.to_numeric(
        df["realized_revenue"], errors="coerce"
    )

    df = df.dropna(subset=["realized_revenue"])

    if len(df) < 36:
        raise ValueError(
            "At least 36 months of historical data are required."
        )

    if df["month"].duplicated().any():
        raise ValueError("Duplicate monthly records found.")

    print(f"Loaded {len(df)} monthly observations.")

    return df


def calculate_metrics(actual, predicted):

    mae = mean_absolute_error(actual, predicted)

    rmse = np.sqrt(mean_squared_error(actual, predicted))

    non_zero = np.array(actual) != 0

    mape = (
        np.mean(
            np.abs(
                (
                    np.array(actual)[non_zero]
                    - np.array(predicted)[non_zero]
                )
                / np.array(actual)[non_zero]
            )
        ) * 100
    )

    return {
        "MAE": mae,
        "RMSE": rmse,
        "MAPE": mape
    }


def create_ml_features(df):

    data = df.copy()

    data["month_number"] = data["month"].dt.month
    data["year"] = data["month"].dt.year

    data["lag_1"] = data["realized_revenue"].shift(1)
    data["lag_2"] = data["realized_revenue"].shift(2)
    data["lag_3"] = data["realized_revenue"].shift(3)
    data["lag_12"] = data["realized_revenue"].shift(12)

    data["rolling_mean_3"] = (
        data["realized_revenue"]
        .shift(1)
        .rolling(3)
        .mean()
    )

    return data.dropna().reset_index(drop=True)


def evaluate_models(df, save=True):

    print("\nEvaluating forecasting models...")

    train = df.iloc[:-12].copy()
    test = df.iloc[-12:].copy()

    actual = test["realized_revenue"].values

    results = []

    # 1. Seasonal Naive Baseline

    seasonal_predictions = (
        train["realized_revenue"]
        .iloc[-12:]
        .values
    )

    seasonal_metrics = calculate_metrics(
        actual, seasonal_predictions
    )

    results.append({
        "model": "Seasonal Naive",
        **seasonal_metrics
    })

    # 2. Exponential Smoothing

    es_model = ExponentialSmoothing(
        train["realized_revenue"],
        trend="add",
        seasonal="add",
        seasonal_periods=12,
        initialization_method="estimated"
    )

    es_fitted = es_model.fit(optimized=True)

    es_predictions = es_fitted.forecast(12).values

    es_metrics = calculate_metrics(
        actual, es_predictions
    )

    results.append({
        "model": "Exponential Smoothing",
        **es_metrics
    })

    # 3. Random Forest

    feature_df = create_ml_features(df)

    train_features = feature_df[
        feature_df["month"] <= train["month"].iloc[-1]
    ]

    test_features = feature_df[
        feature_df["month"] >= test["month"].iloc[0]
    ]

    feature_columns = [
        "month_number",
        "year",
        "lag_1",
        "lag_2",
        "lag_3",
        "lag_12",
        "rolling_mean_3"
    ]

    rf_model = RandomForestRegressor(
        n_estimators=300,
        max_depth=5,
        min_samples_leaf=2,
        random_state=42
    )

    rf_model.fit(
        train_features[feature_columns],
        train_features["realized_revenue"]
    )

    rf_predictions = rf_model.predict(
        test_features[feature_columns]
    )

    rf_metrics = calculate_metrics(
        actual, rf_predictions
    )

    results.append({
        "model": "Random Forest",
        **rf_metrics
    })

    results_df = pd.DataFrame(results)

    results_df = results_df.sort_values(
        "RMSE"
    ).reset_index(drop=True)

    if save:
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        results_df.to_csv(
            os.path.join(OUTPUT_DIR, "model_evaluation.csv"),
            index=False
        )

    print("\nMODEL PERFORMANCE")
    print("=" * 60)
    print(results_df.to_string(index=False))

    return results_df

def generate_future_forecast(df, save=True):

    print("\nGenerating 12-month future forecast...")

    model = ExponentialSmoothing(
        df["realized_revenue"],
        trend="add",
        seasonal="add",
        seasonal_periods=12,
        initialization_method="estimated"
    )

    fitted_model = model.fit(optimized=True)

    forecast_values = fitted_model.forecast(12)

    future_dates = pd.date_range(
        start=df["month"].max() + pd.offsets.MonthBegin(1),
        periods=12,
        freq="MS"
    )

    forecast_df = pd.DataFrame({
        "month": future_dates,
        "forecasted_revenue": forecast_values.values
    })

    forecast_df["forecasted_revenue"] = (
        forecast_df["forecasted_revenue"].clip(lower=0)
    )

    if save:
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        forecast_df.to_csv(
            os.path.join(OUTPUT_DIR, "future_forecast.csv"),
            index=False
        )

    print("\n12-MONTH REVENUE FORECAST")
    print("=" * 60)
    print(forecast_df.to_string(index=False))

    print("\nTotal forecasted revenue: ₹{:,.2f}".format(
        forecast_df["forecasted_revenue"].sum()
    ))

    return forecast_df

if __name__ == "__main__":

    monthly_data = load_monthly_data()

    evaluate_models(monthly_data)


