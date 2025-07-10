"""Simple backtesting engine for classified signals."""

from __future__ import annotations

import os
import pandas as pd

DATA_DIR = "data"


def simulate_trade(row: pd.Series) -> float:
    entry = row["entry"]
    exit_price = row["exit"]
    if row["signal"] == "long":
        return (exit_price - entry) / entry
    elif row["signal"] == "short":
        return (entry - exit_price) / entry
    return 0.0


def main() -> None:
    path = os.path.join(DATA_DIR, "classification_summary.csv")
    if not os.path.exists(path):
        print("No classification data found")
        return
    df = pd.read_csv(path)
    df["return"] = df.apply(simulate_trade, axis=1)
    summary = df.groupby("timeframe")["return"].mean().reset_index()
    df.to_csv(os.path.join(DATA_DIR, "backtest_results.csv"), index=False)
    summary.to_csv(os.path.join(DATA_DIR, "backtest_summary.csv"), index=False)


if __name__ == "__main__":
    main()
