from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def _safe_name(value: str) -> str:
    return value.replace("^", "").replace("/", "_").replace(" ", "_")


def plot_normalized_prices(df: pd.DataFrame, output_dir: Path) -> Path:
    """Plot normalized close price for all tickers."""
    output_dir.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(14, 7))

    for ticker, chunk in df.groupby("Ticker"):
        norm = chunk["Close"] / chunk["Close"].iloc[0]
        ax.plot(chunk["Date"], norm, label=ticker, linewidth=1.0)

    ax.set_title("Normalized Index Performance Over Time")
    ax.set_xlabel("Date")
    ax.set_ylabel("Normalized Close")
    ax.legend(loc="upper left", ncol=3, fontsize=8)
    ax.grid(alpha=0.25)

    out = output_dir / "normalized_prices.png"
    fig.tight_layout()
    fig.savefig(out, dpi=150)
    plt.close(fig)
    return out


def plot_correlation_heatmap(corr: pd.DataFrame, output_dir: Path) -> Path:
    """Plot return correlation heatmap."""
    output_dir.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(10, 8))

    im = ax.imshow(corr.values, cmap="coolwarm", vmin=-1, vmax=1)
    ax.set_xticks(range(len(corr.columns)))
    ax.set_yticks(range(len(corr.index)))
    ax.set_xticklabels(corr.columns, rotation=45, ha="right")
    ax.set_yticklabels(corr.index)
    ax.set_title("Daily Return Correlation")

    cbar = plt.colorbar(im, ax=ax)
    cbar.set_label("Correlation")

    out = output_dir / "correlation_heatmap.png"
    fig.tight_layout()
    fig.savefig(out, dpi=150)
    plt.close(fig)
    return out


def plot_moving_averages(df: pd.DataFrame, output_dir: Path, ticker: str, windows: tuple[int, ...] = (20, 50)) -> Path:
    """Plot close and moving averages for one ticker."""
    output_dir.mkdir(parents=True, exist_ok=True)
    ticker_df = df[df["Ticker"] == ticker].copy()

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(ticker_df["Date"], ticker_df["Close"], label="Close", linewidth=1.3)
    for w in windows:
        ax.plot(ticker_df["Date"], ticker_df[f"SMA_{w}"], label=f"SMA {w}", linewidth=1.0)

    ax.set_title(f"Moving Averages - {ticker}")
    ax.set_xlabel("Date")
    ax.set_ylabel("Price")
    ax.legend()
    ax.grid(alpha=0.25)

    out = output_dir / f"moving_averages_{_safe_name(ticker)}.png"
    fig.tight_layout()
    fig.savefig(out, dpi=150)
    plt.close(fig)
    return out


def plot_volatility(df: pd.DataFrame, output_dir: Path, ticker: str, vol_window: int = 20) -> Path:
    """Plot rolling annualized volatility for one ticker."""
    output_dir.mkdir(parents=True, exist_ok=True)
    ticker_df = df[df["Ticker"] == ticker].copy()
    vol_col = f"Volatility_{vol_window}"

    fig, ax = plt.subplots(figsize=(12, 5))
    ax.plot(ticker_df["Date"], ticker_df[vol_col], color="tab:red", linewidth=1.0)
    ax.set_title(f"Annualized Volatility ({vol_window}d) - {ticker}")
    ax.set_xlabel("Date")
    ax.set_ylabel("Volatility")
    ax.grid(alpha=0.25)

    out = output_dir / f"volatility_{_safe_name(ticker)}.png"
    fig.tight_layout()
    fig.savefig(out, dpi=150)
    plt.close(fig)
    return out


def plot_rsi_macd(df: pd.DataFrame, output_dir: Path, ticker: str, rsi_window: int = 14) -> Path:
    """Plot RSI and MACD for one ticker in stacked panels."""
    output_dir.mkdir(parents=True, exist_ok=True)
    ticker_df = df[df["Ticker"] == ticker].copy()

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), sharex=True)

    ax1.plot(ticker_df["Date"], ticker_df[f"RSI_{rsi_window}"], color="tab:purple", linewidth=1.0)
    ax1.axhline(70, linestyle="--", linewidth=0.8, color="red")
    ax1.axhline(30, linestyle="--", linewidth=0.8, color="green")
    ax1.set_title(f"RSI ({rsi_window}) - {ticker}")
    ax1.set_ylabel("RSI")
    ax1.grid(alpha=0.25)

    ax2.plot(ticker_df["Date"], ticker_df["MACD"], label="MACD", linewidth=1.0)
    ax2.plot(ticker_df["Date"], ticker_df["MACD_Signal"], label="Signal", linewidth=1.0)
    ax2.bar(ticker_df["Date"], ticker_df["MACD_Hist"], label="Hist", alpha=0.3)
    ax2.set_title("MACD")
    ax2.set_ylabel("Value")
    ax2.legend()
    ax2.grid(alpha=0.25)

    out = output_dir / f"rsi_macd_{_safe_name(ticker)}.png"
    fig.tight_layout()
    fig.savefig(out, dpi=150)
    plt.close(fig)
    return out


def plot_dashboard(df: pd.DataFrame, corr: pd.DataFrame, output_dir: Path, vol_window: int = 20) -> Path:
    """Create one combined dashboard figure with key analysis views."""
    output_dir.mkdir(parents=True, exist_ok=True)

    first_ticker = sorted(df["Ticker"].unique())[0]
    sample = df[df["Ticker"] == first_ticker].copy()

    fig = plt.figure(figsize=(16, 10))

    ax1 = fig.add_subplot(2, 2, 1)
    for ticker, chunk in df.groupby("Ticker"):
        norm = chunk["Close"] / chunk["Close"].iloc[0]
        ax1.plot(chunk["Date"], norm, linewidth=0.8, label=ticker)
    ax1.set_title("Normalized Prices (All Tickers)")
    ax1.set_xlabel("Date")
    ax1.set_ylabel("Normalized Close")
    ax1.grid(alpha=0.25)

    ax2 = fig.add_subplot(2, 2, 2)
    im = ax2.imshow(corr.values, cmap="coolwarm", vmin=-1, vmax=1)
    ax2.set_xticks(range(len(corr.columns)))
    ax2.set_yticks(range(len(corr.index)))
    ax2.set_xticklabels(corr.columns, rotation=45, ha="right")
    ax2.set_yticklabels(corr.index)
    ax2.set_title("Return Correlation")
    fig.colorbar(im, ax=ax2, fraction=0.046, pad=0.04)

    ax3 = fig.add_subplot(2, 2, 3)
    ax3.plot(sample["Date"], sample["Close"], label="Close", linewidth=1.0)
    if "SMA_20" in sample:
        ax3.plot(sample["Date"], sample["SMA_20"], label="SMA 20", linewidth=1.0)
    if "SMA_50" in sample:
        ax3.plot(sample["Date"], sample["SMA_50"], label="SMA 50", linewidth=1.0)
    ax3.set_title(f"Moving Averages ({first_ticker})")
    ax3.set_xlabel("Date")
    ax3.set_ylabel("Price")
    ax3.legend()
    ax3.grid(alpha=0.25)

    ax4 = fig.add_subplot(2, 2, 4)
    vol_col = f"Volatility_{vol_window}"
    if vol_col in sample:
        ax4.plot(sample["Date"], sample[vol_col], color="tab:red", linewidth=1.0)
    ax4.set_title(f"Volatility ({vol_window}d, {first_ticker})")
    ax4.set_xlabel("Date")
    ax4.set_ylabel("Volatility")
    ax4.grid(alpha=0.25)

    out = output_dir / "dashboard_combined.png"
    fig.tight_layout()
    fig.savefig(out, dpi=150)
    plt.close(fig)
    return out
