# aibot

This repository contains a small script `usdt_dominance.py` that fetches
USDT dominance and market data for the top 300 cryptocurrencies using the
CoinGecko public API.

## Usage

Run the script with Python 3. It will output the current USDT dominance,
the average 24h change across the top 300 coins, the 24h change for a
specific coin, and a simple market signal (bullish, bearish, or neutral).

```
python3 usdt_dominance.py [coin_id]
```

`coin_id` defaults to `bitcoin` if not provided. Use a CoinGecko coin ID
(e.g. `ethereum`, `solana`, etc.).

The project depends only on the `requests` package. Install it using the
provided requirements file:

```
pip install -r requirements.txt
```

The helper function `fetch_market_chart` gracefully handles network errors. If
the request fails, it prints an error message and returns empty lists so the
rest of the analysis can continue (yielding zero correlations).
