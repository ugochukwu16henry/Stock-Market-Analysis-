from __future__ import annotations

import numpy as np
import pandas as pd

from .config import MACD_FAST, MACD_SIGNAL, MACD_SLOW, TRADING_DAYS_PER_YEAR


def add_returns_features(df: pd.DataFrame) -> pd.DataFrame:
    """Add daily and cumulative returns per ticker."""
    out = df.copy()
    out["Daily_Return"] = out.groupby("Ticker")["Close"].pct_change()
    out["Cumulative_Return"] = (
        1 + out["Daily_Return"].fillna(0)
    ).groupby(out["Ticker"]).cumprod() - 1
    return out


def add_moving_averages(df: pd.DataFrame, windows: tuple[int, ...] = (20, 50)) -> pd.DataFrame:
    """Add simple moving averages for each requested window."""
    out = df.copy()
    for window in windows:
        col = f"SMA_{window}"
        out[col] = out.groupby("Ticker")["Close"].transform(lambda s: s.rolling(window=window).mean())
    return out


def add_rolling_volatility(df: pd.DataFrame, window: int = 20) -> pd.DataFrame:
    """Add annualized realized volatility from daily returns."""
    out = df.copy()
    out[f"Volatility_{window}"] = out.groupby("Ticker")["Daily_Return"].transform(
        lambda s: s.rolling(window=window).std() * np.sqrt(TRADING_DAYS_PER_YEAR)
    )
    return out


def add_rsi(df: pd.DataFrame, window: int = 14) -> pd.DataFrame:
    """Add Relative Strength Index (RSI) per ticker."""
    out = df.copy()

    def _rsi(series: pd.Series) -> pd.Series:
        """Compute RSI series from a close-price series."""
        delta = series.diff()
        gain = delta.clip(lower=0)
        loss = -delta.clip(upper=0)
        avg_gain = gain.rolling(window=window, min_periods=window).mean()
        avg_loss = loss.rolling(window=window, min_periods=window).mean()
        rs = avg_gain / avg_loss.replace(0, np.nan)
        return 100 - (100 / (1 + rs))

    out[f"RSI_{window}"] = out.groupby("Ticker")["Close"].transform(_rsi)
    return out


def add_macd(
    df: pd.DataFrame,
    fast: int = MACD_FAST,
    slow: int = MACD_SLOW,
    signal: int = MACD_SIGNAL,
) -> pd.DataFrame:
    """Add MACD line, signal line, and histogram per ticker."""
    out = df.copy()

    def _ema(series: pd.Series, span: int) -> pd.Series:
        """Compute exponential moving average for a given span."""
        return series.ewm(span=span, adjust=False).mean()

    fast_ema = out.groupby("Ticker")["Close"].transform(lambda s: _ema(s, fast))
    slow_ema = out.groupby("Ticker")["Close"].transform(lambda s: _ema(s, slow))
    out["MACD"] = fast_ema - slow_ema
    out["MACD_Signal"] = out.groupby("Ticker")["MACD"].transform(lambda s: _ema(s, signal))
    out["MACD_Hist"] = out["MACD"] - out["MACD_Signal"]
    return out


def build_feature_set(
    df: pd.DataFrame,
    ma_windows: tuple[int, ...] = (20, 50),
    vol_window: int = 20,
    rsi_window: int = 14,
) -> pd.DataFrame:
    """Run the full feature engineering pipeline."""
    out = add_returns_features(df)
    out = add_moving_averages(out, ma_windows)
    out = add_rolling_volatility(out, vol_window)
    out = add_rsi(out, rsi_window)
    out = add_macd(out)
    return out
