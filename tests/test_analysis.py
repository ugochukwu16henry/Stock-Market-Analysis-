import numpy as np
import pandas as pd

from src.analysis import compute_correlation_matrix, compute_summary_stats
from src.indicators import build_feature_set


def _sample_df(rows=80):
    """Create a deterministic two-ticker dataset for analysis unit tests."""
    dates = pd.date_range("2020-01-01", periods=rows, freq="D")
    records = []
    for ticker, base in [("AAA", 100), ("BBB", 200)]:
        close = np.linspace(base, base * 1.2, rows)
        for d, c in zip(dates, close):
            records.append(
                {
                    "Date": d,
                    "Open": c,
                    "High": c + 1,
                    "Low": c - 1,
                    "Close": c,
                    "Volume": 1000,
                    "Ticker": ticker,
                    "Index_Name": f"Index {ticker}",
                }
            )
    return pd.DataFrame(records)


def test_summary_stats_contains_expected_columns():
    """Verify summary stats output includes required reporting fields."""
    df = build_feature_set(_sample_df())
    summary = compute_summary_stats(df)
    expected = {"Ticker", "index_name", "annualized_return", "annualized_volatility", "sharpe_like"}
    assert expected.issubset(set(summary.columns))


def test_correlation_matrix_is_square():
    """Verify correlation matrix dimensions and labels are consistent."""
    df = build_feature_set(_sample_df())
    corr = compute_correlation_matrix(df)
    assert corr.shape[0] == corr.shape[1]
    assert set(corr.columns) == set(corr.index)
