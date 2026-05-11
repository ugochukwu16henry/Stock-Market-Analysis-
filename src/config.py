from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
DEFAULT_DATA_PATH = ROOT_DIR / ".sixth" / "Global_Stock_Market_Indices_2000_2026.csv"
DEFAULT_OUTPUT_DIR = ROOT_DIR / "outputs"
PROCESSED_DIR = ROOT_DIR / "data" / "processed"

DEFAULT_MA_WINDOWS = (20, 50)
DEFAULT_VOL_WINDOW = 20
DEFAULT_RSI_WINDOW = 14
MACD_FAST = 12
MACD_SLOW = 26
MACD_SIGNAL = 9
TRADING_DAYS_PER_YEAR = 252
