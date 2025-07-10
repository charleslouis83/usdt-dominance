"""Classify signals into long/short positions with TP/SL."""

from __future__ import annotations

import os
import pandas as pd

DATA_DIR = "data"
THRESHOLD = 0.3
TP_PCT = 0.02
SL_PCT = 0.01


def load_price(symbol: str, tf: str) -> pd.DataFrame:
    path = os.path.join(DATA_DIR, f"{symbol}_{tf}.csv")
    return pd.read_csv(path, parse_dates=["datetime"])


def classify_signal(row: pd.Series) -> pd.Series:
    corr = row["correlation"]
    if corr <= -THRESHOLD:
        signal = "long"
    elif corr >= THRESHOLD:
        signal = "short"
    else:
        signal = "neutral"
    return pd.Series({"signal": signal, "confidence": abs(corr)})


def compute_entries(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for _, row in df.iterrows():
        price_df = load_price(row.symbol, row.timeframe)
        idx = price_df[price_df["datetime"] == pd.to_datetime(row.date)].index
        if len(idx) == 0 or idx[0] + 1 >= len(price_df):
            continue
        next_bar = price_df.loc[idx[0] + 1]
        entry = next_bar["open"]
        exit_price = next_bar["close"]
        tp = entry * (1 + TP_PCT)
        sl = entry * (1 - SL_PCT)
        rows.append({
            "timeframe": row.timeframe,
            "symbol": row.symbol,
            "signal": row.signal,
            "confidence": row.confidence,
            "entry": entry,
            "exit": exit_price,
            "tp": tp,
            "sl": sl,
        })
    return pd.DataFrame(rows)


def main() -> None:
    path = os.path.join(DATA_DIR, "signals_summary.csv")
    df = pd.read_csv(path, parse_dates=["date"])
    cls = df.apply(classify_signal, axis=1)
    df = pd.concat([df, cls], axis=1)
    df = df[df["signal"] != "neutral"]
    result = compute_entries(df)
    result.to_csv(os.path.join(DATA_DIR, "classification_summary.csv"), index=False)


if __name__ == "__main__":
    main()
