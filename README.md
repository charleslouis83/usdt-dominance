# aibot

This repository contains a Python script `usdt_dominance.py` that fetches
historical market data from the CoinGecko API and computes how strongly a coin
is correlated with USDT dominance. The script approximates USDT dominance using
market caps of USDT, Bitcoin and Ethereum, and prints signals for multiple
timeframes.

Run the script with Python 3. It prints correlation statistics for the coin in
four timeframes:

* **15m** and **2h** – computed from 5-minute data over the last two days.
* **1d** and **1w** – computed from daily data over the last month.

For each timeframe you will see the correlation, a confidence score (absolute
value of the correlation), and whether the setup suggests a *long* or *short*
bias. The entry and exit price correspond to the first and last prices used in
that timeframe.
```
python3 usdt_dominance.py [coin_id]
```

`coin_id` defaults to `bitcoin` if not provided. Use a CoinGecko coin ID

Install dependencies (requests and numpy) if they are not already available:
```
pip install requests numpy
```

