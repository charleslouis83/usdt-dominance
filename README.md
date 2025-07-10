# USDT Dominance Signal Confirmation System

This repository contains a basic implementation of a multi‑stage analytics pipeline that fetches USDT dominance data alongside Binance coin prices, computes correlations, classifies trading signals and provides a Streamlit dashboard.

## Requirements

- Python 3.11+
- `pandas`, `yfinance`, `ccxt`, `scipy`, `streamlit`

Install dependencies with:

```bash
pip install -r requirements.txt
```

## Usage

Run the pipeline step by step:

```bash
python fetch_data.py
python compute_signals.py
python compute_classification.py
python backtest.py
streamlit run app/app.py
```

CSV data is written to the `data/` directory.
