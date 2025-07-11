import requests
from statistics import correlation
from typing import List, Tuple

COINGECKO_BASE = "https://api.coingecko.com/api/v3"


def fetch_market_chart(coin_id: str, days: int, interval: str | None = None) -> Tuple[List[Tuple[int, float]], List[Tuple[int, float]]]:
    """Return price and market cap history for a coin."""
    params = {"vs_currency": "usd", "days": days}
    if interval:
        params["interval"] = interval
    resp = requests.get(f"{COINGECKO_BASE}/coins/{coin_id}/market_chart", params=params)
    resp.raise_for_status()
    data = resp.json()
    return data["prices"], data["market_caps"]


def usdt_dominance_series(days: int, interval: str | None = None) -> List[Tuple[int, float]]:
    """Approximate USDT dominance percentage over time using BTC and ETH market caps."""
    _, usdt_caps = fetch_market_chart("tether", days, interval)
    _, btc_caps = fetch_market_chart("bitcoin", days, interval)
    _, eth_caps = fetch_market_chart("ethereum", days, interval)

    length = min(len(usdt_caps), len(btc_caps), len(eth_caps))
    dominance = []
    for i in range(length):
        ts = usdt_caps[i][0]
        total = usdt_caps[i][1] + btc_caps[i][1] + eth_caps[i][1]
        dom = (usdt_caps[i][1] / total * 100) if total else 0.0
        dominance.append((ts, dom))
    return dominance


def returns(series: List[Tuple[int, float]], step: int) -> List[float]:
    """Compute simple returns from a time series."""
    r: List[float] = []
    for i in range(step, len(series)):
        prev = series[i - step][1]
        if prev:
            r.append((series[i][1] - prev) / prev)
    return r


def correlation_for_timeframe(prices: List[Tuple[int, float]], dominance: List[Tuple[int, float]], step: int) -> float:
    """Correlation between coin returns and dominance returns using a step size."""
    pr = returns(prices, step)
    dr = returns(dominance, step)
    length = min(len(pr), len(dr))
    if length < 2:
        return 0.0
    return float(correlation(pr[:length], dr[:length]))


def entry_exit(prices: List[Tuple[int, float]], step: int) -> Tuple[float | None, float | None]:
    if len(prices) < step + 1:
        return None, None
    return prices[-step - 1][1], prices[-1][1]


def trade_type(corr: float) -> str:
    if corr <= -0.2:
        return "long"
    if corr >= 0.2:
        return "short"
    return "neutral"


def analyze_coin(coin_id: str) -> None:
    # intraday (5 min resolution) for 2 days
    dom_intraday = usdt_dominance_series(2)
    prices_intraday, _ = fetch_market_chart(coin_id, 2)

    results = []
    for minutes in (15, 120):
        step = max(1, minutes // 5)
        corr = correlation_for_timeframe(prices_intraday, dom_intraday, step)
        entry, exit_ = entry_exit(prices_intraday, step)
        results.append({
            "tf": {15: "15m", 120: "2h"}[minutes],
            "corr": corr,
            "conf": abs(corr),
            "trade": trade_type(corr),
            "entry": entry,
            "exit": exit_,
        })

    # daily data for 30 days
    dom_daily = usdt_dominance_series(30, interval="daily")
    prices_daily, _ = fetch_market_chart(coin_id, 30, interval="daily")

    for minutes, step_days in ((1440, 1), (10080, 7)):
        corr = correlation_for_timeframe(prices_daily, dom_daily, step_days)
        entry, exit_ = entry_exit(prices_daily, step_days)
        results.append({
            "tf": {1440: "1d", 10080: "1w"}[minutes],
            "corr": corr,
            "conf": abs(corr),
            "trade": trade_type(corr),
            "entry": entry,
            "exit": exit_,
        })

    for r in results:
        entry = f"{r['entry']:.4f}" if r['entry'] is not None else "n/a"
        exit_ = f"{r['exit']:.4f}" if r['exit'] is not None else "n/a"
        print(
            f"{r['tf']}: corr={r['corr']:.4f} conf={r['conf']:.4f} "
            f"{r['trade']} entry={entry} exit={exit_}"
        )


def main(coin_id: str = "bitcoin") -> None:
    analyze_coin(coin_id)


if __name__ == "__main__":
    import sys

    coin = sys.argv[1] if len(sys.argv) > 1 else "bitcoin"
    main(coin)
