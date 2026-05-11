from __future__ import annotations

import numpy as np
import pandas as pd


def compute_summary_stats(df: pd.DataFrame, vol_window: int = 20) -> pd.DataFrame:
    """Create per-ticker summary stats for reporting."""
    vol_col = f"Volatility_{vol_window}"

    grouped = df.groupby("Ticker")
    summary = grouped.agg(
        index_name=("Index_Name", "last"),
        start_date=("Date", "min"),
        end_date=("Date", "max"),
        mean_daily_return=("Daily_Return", "mean"),
        std_daily_return=("Daily_Return", "std"),
        latest_cumulative_return=("Cumulative_Return", "last"),
        latest_volatility=(vol_col, "last"),
    )

    summary["annualized_return"] = (1 + summary["mean_daily_return"]) ** 252 - 1
    summary["annualized_volatility"] = summary["std_daily_return"] * np.sqrt(252)
    summary["sharpe_like"] = summary["annualized_return"] / summary["annualized_volatility"].replace(0, np.nan)

    summary.reset_index(inplace=True)
    return summary


def compute_correlation_matrix(df: pd.DataFrame) -> pd.DataFrame:
    """Create cross-ticker correlation matrix on daily returns."""
    pivoted = df.pivot_table(index="Date", columns="Ticker", values="Daily_Return")
    return pivoted.corr()
