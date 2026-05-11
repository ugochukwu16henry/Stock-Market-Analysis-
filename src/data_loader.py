from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Tuple

import pandas as pd

REQUIRED_COLUMNS = ["Date", "Open", "High", "Low", "Close", "Volume", "Ticker", "Index_Name"]
NUMERIC_COLUMNS = ["Open", "High", "Low", "Close", "Volume"]


def load_market_data(csv_path: Path) -> pd.DataFrame:
    """Load raw market data from CSV."""
    df = pd.read_csv(csv_path)
    return df


def clean_market_data(df: pd.DataFrame) -> pd.DataFrame:
    """Validate, type-cast, and sort market data for analysis."""
    missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    cleaned = df.copy()
    cleaned["Date"] = pd.to_datetime(cleaned["Date"], errors="coerce")

    for col in NUMERIC_COLUMNS:
        cleaned[col] = pd.to_numeric(cleaned[col], errors="coerce")

    cleaned = cleaned.dropna(subset=["Date", "Open", "High", "Low", "Close", "Ticker", "Index_Name"])
    cleaned["Ticker"] = cleaned["Ticker"].astype(str).str.strip()
    cleaned["Index_Name"] = cleaned["Index_Name"].astype(str).str.strip()

    cleaned = cleaned.drop_duplicates(subset=["Date", "Ticker"]).sort_values(["Ticker", "Date"])
    cleaned.reset_index(drop=True, inplace=True)
    return cleaned


def build_quality_report(raw_df: pd.DataFrame, cleaned_df: pd.DataFrame) -> Dict[str, object]:
    """Generate a concise data quality report for logging and grading evidence."""
    per_ticker = (
        cleaned_df.groupby("Ticker")
        .agg(
            rows=("Date", "count"),
            start_date=("Date", "min"),
            end_date=("Date", "max"),
            zero_volume_rows=("Volume", lambda s: int((s == 0).sum())),
        )
        .reset_index()
    )

    volume_limited = per_ticker.loc[per_ticker["zero_volume_rows"] > 0, "Ticker"].tolist()

    report = {
        "raw_shape": list(raw_df.shape),
        "cleaned_shape": list(cleaned_df.shape),
        "missing_values_cleaned": cleaned_df.isna().sum().to_dict(),
        "ticker_count": int(cleaned_df["Ticker"].nunique()),
        "date_min": cleaned_df["Date"].min().strftime("%Y-%m-%d"),
        "date_max": cleaned_df["Date"].max().strftime("%Y-%m-%d"),
        "volume_limited_tickers": volume_limited,
        "per_ticker_summary": per_ticker.assign(
            start_date=per_ticker["start_date"].dt.strftime("%Y-%m-%d"),
            end_date=per_ticker["end_date"].dt.strftime("%Y-%m-%d"),
        ).to_dict(orient="records"),
    }
    return report


def save_clean_outputs(cleaned_df: pd.DataFrame, report: Dict[str, object], output_dir: Path) -> Tuple[Path, Path]:
    """Save cleaned data and quality report artifacts."""
    output_dir.mkdir(parents=True, exist_ok=True)
    cleaned_path = output_dir / "cleaned_market_data.csv"
    report_path = output_dir / "data_quality_report.json"

    cleaned_df.to_csv(cleaned_path, index=False)
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return cleaned_path, report_path
