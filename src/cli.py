from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

from .analysis import compute_correlation_matrix, compute_summary_stats
from .config import DEFAULT_DATA_PATH, DEFAULT_MA_WINDOWS, DEFAULT_OUTPUT_DIR, DEFAULT_RSI_WINDOW, DEFAULT_VOL_WINDOW
from .data_loader import build_quality_report, clean_market_data, load_market_data, save_clean_outputs
from .indicators import build_feature_set
from .visualizations import (
    plot_correlation_heatmap,
    plot_dashboard,
    plot_moving_averages,
    plot_normalized_prices,
    plot_rsi_macd,
    plot_volatility,
)


def _load_clean_or_raw(input_path: Path, output_dir: Path) -> pd.DataFrame:
    """Load cleaned data if available; otherwise load raw input and clean it."""
    cleaned_path = output_dir / "cleaned_market_data.csv"
    if cleaned_path.exists():
        df = pd.read_csv(cleaned_path, parse_dates=["Date"])
    else:
        raw = load_market_data(input_path)
        df = clean_market_data(raw)
    return df


def cmd_clean_data(args: argparse.Namespace) -> None:
    """CLI command: clean source data and write quality artifacts."""
    input_path = Path(args.input)
    output_dir = Path(args.output)

    raw_df = load_market_data(input_path)
    cleaned_df = clean_market_data(raw_df)
    report = build_quality_report(raw_df, cleaned_df)

    cleaned_path, report_path = save_clean_outputs(cleaned_df, report, output_dir)
    print(f"Saved cleaned data: {cleaned_path}")
    print(f"Saved quality report: {report_path}")


def cmd_run_analysis(args: argparse.Namespace) -> None:
    """CLI command: compute features, summary statistics, and correlation matrix."""
    input_path = Path(args.input)
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    cleaned_df = _load_clean_or_raw(input_path, output_dir)
    features_df = build_feature_set(
        cleaned_df,
        ma_windows=tuple(args.ma_windows),
        vol_window=args.vol_window,
        rsi_window=args.rsi_window,
    )

    summary_df = compute_summary_stats(features_df, vol_window=args.vol_window)
    corr_df = compute_correlation_matrix(features_df)

    features_path = output_dir / "features_dataset.csv"
    summary_path = output_dir / "summary_stats.csv"
    corr_path = output_dir / "correlation_matrix.csv"

    features_df.to_csv(features_path, index=False)
    summary_df.to_csv(summary_path, index=False)
    corr_df.to_csv(corr_path)

    print(f"Saved features: {features_path}")
    print(f"Saved summary stats: {summary_path}")
    print(f"Saved correlation matrix: {corr_path}")


def cmd_plot_all(args: argparse.Namespace) -> None:
    """CLI command: generate dashboard and ticker-level visualizations."""
    input_path = Path(args.input)
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    features_path = output_dir / "features_dataset.csv"
    corr_path = output_dir / "correlation_matrix.csv"

    if features_path.exists() and corr_path.exists():
        features_df = pd.read_csv(features_path, parse_dates=["Date"])
        corr_df = pd.read_csv(corr_path, index_col=0)
    else:
        cleaned_df = _load_clean_or_raw(input_path, output_dir)
        features_df = build_feature_set(
            cleaned_df,
            ma_windows=tuple(args.ma_windows),
            vol_window=args.vol_window,
            rsi_window=args.rsi_window,
        )
        corr_df = compute_correlation_matrix(features_df)

    plot_paths = [
        plot_normalized_prices(features_df, output_dir),
        plot_correlation_heatmap(corr_df, output_dir),
        plot_dashboard(features_df, corr_df, output_dir, vol_window=args.vol_window),
    ]

    tickers = sorted(features_df["Ticker"].unique())
    if args.ticker == "ALL":
        selected = tickers
    else:
        selected_ticker = args.ticker
        if selected_ticker not in tickers and f"^{selected_ticker}" in tickers:
            selected_ticker = f"^{selected_ticker}"
        selected = [selected_ticker]

    if args.per_ticker_limit >= 0:
        selected = selected[: args.per_ticker_limit]

    for ticker in selected:
        if ticker not in tickers:
            print(f"Skipped unknown ticker: {ticker}")
            continue
        try:
            plot_paths.append(
                plot_moving_averages(features_df, output_dir, ticker=ticker, windows=tuple(args.ma_windows))
            )
            plot_paths.append(plot_volatility(features_df, output_dir, ticker=ticker, vol_window=args.vol_window))
            plot_paths.append(plot_rsi_macd(features_df, output_dir, ticker=ticker, rsi_window=args.rsi_window))
        except Exception as exc:
            print(f"Warning: failed to render detailed plots for {ticker}: {exc}")

    for p in plot_paths:
        print(f"Saved plot: {p}")


def cmd_full_pipeline(args: argparse.Namespace) -> None:
    """CLI command: run cleaning, analysis, and plotting in sequence."""
    clean_args = argparse.Namespace(input=args.input, output=args.output)
    run_args = argparse.Namespace(
        input=args.input,
        output=args.output,
        ma_windows=args.ma_windows,
        vol_window=args.vol_window,
        rsi_window=args.rsi_window,
    )
    plot_args = argparse.Namespace(
        input=args.input,
        output=args.output,
        ma_windows=args.ma_windows,
        vol_window=args.vol_window,
        rsi_window=args.rsi_window,
        ticker=args.ticker,
        per_ticker_limit=args.per_ticker_limit,
    )

    cmd_clean_data(clean_args)
    cmd_run_analysis(run_args)
    cmd_plot_all(plot_args)

    report_path = Path(args.output) / "data_quality_report.json"
    if report_path.exists():
        report = json.loads(report_path.read_text(encoding="utf-8"))
        print("\nPipeline summary")
        print(f"Ticker count: {report['ticker_count']}")
        print(f"Date range: {report['date_min']} to {report['date_max']}")
        print(f"Volume-limited tickers: {report['volume_limited_tickers']}")


def build_parser() -> argparse.ArgumentParser:
    """Build and return the command-line parser for all supported commands."""
    parser = argparse.ArgumentParser(description="Stock Market Analysis CLI")
    parser.add_argument("--input", default=str(DEFAULT_DATA_PATH), help="Path to input CSV dataset")
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT_DIR), help="Output directory")

    subparsers = parser.add_subparsers(dest="command", required=True)

    clean = subparsers.add_parser("clean-data", help="Load and clean source data")
    clean.set_defaults(func=cmd_clean_data)

    analysis = subparsers.add_parser("run-analysis", help="Compute analytics and export tables")
    analysis.add_argument("--ma-windows", nargs="+", type=int, default=list(DEFAULT_MA_WINDOWS))
    analysis.add_argument("--vol-window", type=int, default=DEFAULT_VOL_WINDOW)
    analysis.add_argument("--rsi-window", type=int, default=DEFAULT_RSI_WINDOW)
    analysis.set_defaults(func=cmd_run_analysis)

    plots = subparsers.add_parser("plot-all", help="Generate visual outputs")
    plots.add_argument("--ma-windows", nargs="+", type=int, default=list(DEFAULT_MA_WINDOWS))
    plots.add_argument("--vol-window", type=int, default=DEFAULT_VOL_WINDOW)
    plots.add_argument("--rsi-window", type=int, default=DEFAULT_RSI_WINDOW)
    plots.add_argument("--ticker", default="ALL", help="Ticker symbol or ALL")
    plots.add_argument(
        "--per-ticker-limit",
        type=int,
        default=3,
        help="Number of ticker-specific detailed charts to generate. Use -1 for all.",
    )
    plots.set_defaults(func=cmd_plot_all)

    full = subparsers.add_parser("full-pipeline", help="Run clean + analysis + plots")
    full.add_argument("--ma-windows", nargs="+", type=int, default=list(DEFAULT_MA_WINDOWS))
    full.add_argument("--vol-window", type=int, default=DEFAULT_VOL_WINDOW)
    full.add_argument("--rsi-window", type=int, default=DEFAULT_RSI_WINDOW)
    full.add_argument("--ticker", default="ALL", help="Ticker symbol or ALL")
    full.add_argument(
        "--per-ticker-limit",
        type=int,
        default=3,
        help="Number of ticker-specific detailed charts to generate. Use -1 for all.",
    )
    full.set_defaults(func=cmd_full_pipeline)

    return parser


def main() -> None:
    """Parse CLI arguments and dispatch execution to the selected command."""
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
