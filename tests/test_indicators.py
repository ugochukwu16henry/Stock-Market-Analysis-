import numpy as np
import pandas as pd

from src.indicators import add_macd, add_moving_averages, add_returns_features, add_rsi, add_rolling_volatility


def _sample_df(rows=40):
    """Create a deterministic single-ticker dataset for unit tests."""
    dates = pd.date_range("2020-01-01", periods=rows, freq="D")
    close = np.linspace(100, 140, rows)
    return pd.DataFrame(
        {
            "Date": dates,
            "Open": close,
            "High": close + 1,
            "Low": close - 1,
            "Close": close,
            "Volume": 1000,
            "Ticker": "AAA",
            "Index_Name": "Sample",
        }
    )


def test_daily_return_exists_and_first_nan():
    """Verify daily return column exists and starts with NaN due to pct_change."""
    df = add_returns_features(_sample_df())
    assert "Daily_Return" in df.columns
    assert np.isnan(df.loc[0, "Daily_Return"])


def test_moving_average_column_created():
    """Verify moving average column is created with expected warm-up NaNs."""
    df = add_moving_averages(_sample_df(), windows=(5,))
    assert "SMA_5" in df.columns
    assert df["SMA_5"].isna().sum() >= 4


def test_volatility_column_created():
    """Verify rolling volatility feature is created."""
    df = add_returns_features(_sample_df())
    df = add_rolling_volatility(df, window=5)
    assert "Volatility_5" in df.columns


def test_rsi_macd_columns_created():
    """Verify RSI and MACD related columns are created by indicator functions."""
    df = _sample_df()
    df = add_rsi(df, window=14)
    df = add_macd(df)
    assert "RSI_14" in df.columns
    assert "MACD" in df.columns
    assert "MACD_Signal" in df.columns
    assert "MACD_Hist" in df.columns
