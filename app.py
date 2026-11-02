"""PROJECT RU'YA — FastAPI application entry point."""

import contextlib
import io

import pandas as pd
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from config import ALLOWED_ORIGINS, MAX_UPLOAD_BYTES
from src.analytics.analytics_engine import run_all_analytics
from src.forecasting.forecasting_engine import (
    evaluate_models,
    generate_future_forecast,
    load_monthly_data,
)
from src.preprocessing.process_data import process_upload

app = FastAPI(title="PROJECT RU'YA API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_methods=["*"],
    allow_headers=["*"],
)


def _f(value) -> float:
    """Plain, JSON-safe float (NaN/inf become 0)."""
    try:
        number = float(value)
    except (TypeError, ValueError):
        return 0.0
    return number if number == number and abs(number) != float("inf") else 0.0


def build_forecast(monthly: pd.DataFrame) -> dict:
    try:
        data = load_monthly_data(monthly)
        with contextlib.redirect_stdout(io.StringIO()):
            evaluation = evaluate_models(data, save=False)
            future = generate_future_forecast(data, save=False)
    except ValueError as exc:
        return {"available": False, "message": str(exc), "models": [], "future": []}
    except Exception:
        return {
            "available": False,
            "message": "Forecast could not be generated for this dataset.",
            "models": [],
            "future": [],
        }

    return {
        "available": True,
        "best_model": str(evaluation.iloc[0]["model"]),
        # generate_future_forecast always uses Exponential Smoothing.
        "forecast_model": "Exponential Smoothing",
        "models": [
            {
                "model": str(row["model"]),
                "MAE": _f(row["MAE"]),
                "RMSE": _f(row["RMSE"]),
                "MAPE": _f(row["MAPE"]),
            }
            for _, row in evaluation.iterrows()
        ],
        "future": [
            {
                "month": pd.Timestamp(row["month"]).strftime("%Y-%m"),
                "forecasted_revenue": _f(row["forecasted_revenue"]),
            }
            for _, row in future.iterrows()
        ],
    }


def build_analysis(raw: pd.DataFrame) -> dict:
    cleaned, monthly = process_upload(raw)

    with contextlib.redirect_stdout(io.StringIO()):
        results = run_all_analytics(cleaned, export=False)

    k = results["executive_kpis"].iloc[0]
    category = results["category_performance"]
    products = results["product_revenue"].head(10)

    return {
        "kpis": {
            "total_revenue": _f(k["gross_revenue_before_returns"]),
            "realized_revenue": _f(k["realized_revenue"]),
            "total_profit": _f(k["realized_profit"]),
            "profit_margin_pct": _f(k["profit_margin_percentage"]),
            "total_orders": int(_f(k["total_orders"])),
            "units_sold": int(_f(k["total_units_sold"])),
            "average_order_value": _f(k["average_order_value"]),
            "return_rate_pct": _f(k["return_rate_percentage"]),
        },
        "monthly": [
            {
                "month": str(r["month"]),
                "realized_revenue": _f(r["realized_revenue"]),
                "total_profit": _f(r["total_profit"]),
                "total_orders": int(_f(r["total_orders"])),
            }
            for _, r in monthly.iterrows()
        ],
        "categories": [
            {
                "name": str(r["category"]),
                "revenue": _f(r["realized_revenue"]),
                "share_pct": _f(r["revenue_share"]),
            }
            for _, r in category.iterrows()
        ],
        "products": [
            {
                "name": str(r["product_name"]),
                "category": str(r["category"]),
                "revenue": _f(r["realized_revenue"]),
                "units": int(_f(r["units_sold"])),
            }
            for _, r in products.iterrows()
        ],
        "forecast": build_forecast(monthly),
    }


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/datasets/upload")
async def upload_dataset(file: UploadFile = File(...)):
    if not (file.filename or "").lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Please upload a CSV file.")

    content = await file.read()
    if len(content) > MAX_UPLOAD_BYTES:
        raise HTTPException(
            status_code=413, detail="File is too large. The limit is 4 MB."
        )

    try:
        raw = pd.read_csv(io.BytesIO(content), encoding="utf-8-sig")
    except Exception:
        raise HTTPException(status_code=400, detail="Could not read this CSV file.")

    try:
        return build_analysis(raw)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    except Exception:
        raise HTTPException(
            status_code=500, detail="Analysis failed for this dataset."
        )