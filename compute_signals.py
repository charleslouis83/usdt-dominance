"""Compute Pearson correlations between coins and USDT dominance."""

from __future__ import annotations

import os
import glob
from typing import List

import pandas as pd
from scipy.stats import pearsonr

DATA_DIR = "data"
TIMEFRAMES = ["15m", "2h", "4h", "1d", "1wk"]


def load_usdt(tf: str) -> pd.Series:
    path = os.path.join(DATA_DIR, f"usdt_dominance_{tf}.csv")
    if not os.path.exists(path):
        raise FileNotFoundError(path)
    df = pd.read_csv(path, parse_dates=["datetime"])
    return df.set_index("datetime")["close"]


def load_coin(path: str) -> pd.Series:
    df = pd.read_csv(path, parse_dates=["datetime"])
    return df.set_index("datetime")["close"]


def compute_for_tf(tf: str) -> pd.DataFrame:
    usdt = load_usdt(tf)
    rows = []
    pattern = os.path.join(DATA_DIR, f"*_{tf}.csv")
    for path in glob.glob(pattern):
        if path.startswith(os.path.join(DATA_DIR, "usdt_dominance")):
            continue
        symbol = os.path.basename(path).replace(f"_{tf}.csv", "")
        price = load_coin(path)
        joined = pd.concat([price, usdt], axis=1, join="inner").dropna()
        if len(joined) < 7:
            continue
        corr, _ = pearsonr(joined.iloc[:, 0], joined.iloc[:, 1])
        rows.append({
            "timeframe": tf,
            "symbol": symbol,
            "date": joined.index[-1],
            "correlation": corr,
        })
    df = pd.DataFrame(rows)
    path_out = os.path.join(DATA_DIR, f"signals_summary_{tf}.csv")
    df.to_csv(path_out, index=False)
    return df


def main() -> None:
    frames: List[pd.DataFrame] = []
    for tf in TIMEFRAMES:
        try:
            df = compute_for_tf(tf)
            frames.append(df)
        except FileNotFoundError:
            print(f"Missing USDT data for {tf}, skipping")
    if frames:
        master = pd.concat(frames, ignore_index=True)
        master.to_csv(os.path.join(DATA_DIR, "signals_summary.csv"), index=False)


if __name__ == "__main__":
    main()
