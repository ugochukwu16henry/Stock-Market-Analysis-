# Stock Market Analysis Application

This project analyzes historical global stock index data using Python, Pandas, NumPy, and Matplotlib.

## YouTube Demo

- Video walkthrough: https://youtu.be/Mrqvzl7RJHQ

## Features

- Data loading and cleaning from CSV
- Data quality checks (missing values, date ranges, ticker coverage)
- Daily return and cumulative return calculation
- Moving averages (default: 20 and 50 days)
- Rolling annualized volatility
- Technical indicators: RSI and MACD
- Cross-index correlation analysis
- Visual output as separate charts and one combined dashboard
- CLI workflow plus notebook workflow

## Project Structure

- `src/`: analysis package and CLI
- `tests/`: unit tests for core computations
- `notebooks/`: notebook workflow
- `outputs/`: generated charts and reports
- `.sixth/Global_Stock_Market_Indices_2000_2026.csv`: source dataset

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## CLI Usage

Run from project root.

```bash
python -m src.cli clean-data
python -m src.cli run-analysis
python -m src.cli plot-all --ticker ALL
python -m src.cli full-pipeline --ticker ALL
```

Optional input/output override:

```bash
python -m src.cli full-pipeline --input .sixth/Global_Stock_Market_Indices_2000_2026.csv --output outputs

# Generate detailed per-ticker charts for all tickers (can be slow)
python -m src.cli full-pipeline --ticker ALL --per-ticker-limit -1
```

## Outputs

After running `full-pipeline`, expected outputs include:

- `outputs/cleaned_market_data.csv`
- `outputs/data_quality_report.json`
- `outputs/features_dataset.csv`
- `outputs/summary_stats.csv`
- `outputs/correlation_matrix.csv`
- `outputs/normalized_prices.png`
- `outputs/correlation_heatmap.png`
- `outputs/dashboard_combined.png`
- ticker-specific moving average, volatility, and RSI/MACD charts

## Key Findings

- Dataset coverage: 14 global indices
- Date range analyzed: 2000-01-03 to 2026-03-25
- Top 3 indices by latest cumulative return: ^BSESN (13.0041), ^BVSP (9.9524), ^KS11 (4.3277)

## Outcome Preview

### Combined Dashboard

![Combined Dashboard](outputs/dashboard_combined.png)

### Normalized Price Performance

![Normalized Prices](outputs/normalized_prices.png)

### Correlation Heatmap

![Correlation Heatmap](outputs/correlation_heatmap.png)

### Example Ticker Plots (BSESN)

![BSESN Moving Averages](outputs/moving_averages_BSESN.png)

![BSESN Volatility](outputs/volatility_BSESN.png)

![BSESN RSI and MACD](outputs/rsi_macd_BSESN.png)

## Notes

- Some tickers may contain zero volume rows. The dataset is retained, but volume-based interpretation should be treated carefully.
- This project focuses on descriptive historical analysis and visualization, not forecasting.
