from src.forecasting.forecasting_engine import (
    load_monthly_data,
    evaluate_models,
    generate_future_forecast
)


if __name__ == "__main__":

    print("=" * 60)
    print("PROJECT RU'YA — FORECASTING ENGINE")
    print("SEE BEYOND THE NUMBERS")
    print("=" * 60)

    monthly_data = load_monthly_data()

    evaluate_models(monthly_data)

    generate_future_forecast(monthly_data)