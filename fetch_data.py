"""Fetch USDT dominance and Binance OHLCV data."""

from __future__ import annotations

import os
from datetime import datetime
from typing import List, Dict

import pandas as pd
import yfinance as yf
import ccxt

DATA_DIR = "data"

TIMEFRAMES = {
    "15m": {"yf_interval": "15m", "period": "60d"},
    "2h": {"yf_interval": "60m", "period": "60d", "resample": "2h"},
    "4h": {"yf_interval": "60m", "period": "60d", "resample": "4h"},
    "1d": {"yf_interval": "1d", "start": "2019-01-01"},
    "1wk": {"yf_interval": "1wk", "start": "2019-01-01"},
}

BINANCE_LIMIT = 500


def ensure_data_dir() -> None:
    os.makedirs(DATA_DIR, exist_ok=True)


def fetch_usdt_dominance(tf: str) -> pd.DataFrame:
    params = TIMEFRAMES[tf]
    interval = params["yf_interval"]
    kwargs: Dict[str, str] = {}
    if "period" in params:
        kwargs["period"] = params["period"]
    if "start" in params:
        kwargs["start"] = params["start"]
    df = yf.download("USDT-USD", interval=interval, **kwargs)

    if df.empty:
        return df

    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(1)
    df = df.rename(columns={"Adj Close": "close"})
    df = df[["Open", "High", "Low", "close", "Volume"]]
    df.columns = ["open", "high", "low", "close", "volume"]

    if "resample" in params:
        df = df.resample(params["resample"]).agg({
            "open": "first",
            "high": "max",
            "low": "min",
            "close": "last",
            "volume": "sum",
        })

    df = df.reset_index().rename(columns={"index": "datetime"})
    df["datetime"] = pd.to_datetime(df["datetime"]).dt.tz_localize(None)
    df = df.dropna()

    path = os.path.join(DATA_DIR, f"usdt_dominance_{tf}.csv")
    df.to_csv(path, index=False)
    return df


def fetch_binance_symbols(limit: int = 50) -> List[str]:
    exchange = ccxt.binance()
    markets = exchange.load_markets()
    symbols = [s for s in markets if s.endswith("/USDT")]
    return symbols[:limit]


def fetch_coin(symbol: str, tf: str) -> pd.DataFrame:
    exchange = ccxt.binance()
    ohlcv = exchange.fetch_ohlcv(symbol, timeframe=tf, limit=BINANCE_LIMIT)
    df = pd.DataFrame(ohlcv, columns=["datetime", "open", "high", "low", "close", "volume"])
    df["datetime"] = pd.to_datetime(df["datetime"], unit="ms")
    df["datetime"] = df["datetime"].dt.tz_localize(None)
    df = df.dropna()
    path = os.path.join(DATA_DIR, f"{symbol.replace('/', '')}_{tf}.csv")
    df.to_csv(path, index=False)
    return df


def main() -> None:
    ensure_data_dir()
    for tf in TIMEFRAMES:
        print(f"Fetching USDT dominance {tf}...")
        usdt_df = fetch_usdt_dominance(tf)
        if usdt_df.empty:
            print(f"Warning: no data for timeframe {tf}")
    symbols = fetch_binance_symbols()
    for symbol in symbols:
        for tf in TIMEFRAMES:
            print(f"Fetching {symbol} {tf}...")
            try:
                fetch_coin(symbol, tf)
            except Exception as e:
                print(f"Failed to fetch {symbol} {tf}: {e}")


if __name__ == "__main__":
    main()
