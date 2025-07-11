import requests
from statistics import mean, correlation, StatisticsError

COINGECKO_BASE = "https://api.coingecko.com/api/v3"


def get_usdt_dominance() -> float:
    """Fetch current USDT market cap percentage from CoinGecko."""
    url = f"{COINGECKO_BASE}/global"
    try:
        resp = requests.get(url)
        resp.raise_for_status()
    except requests.RequestException as exc:
        print(f"Failed to fetch USDT dominance: {exc}")
        return 0.0

    data = resp.json()
    return data["data"]["market_cap_percentage"].get("usdt", 0.0)


def get_top_coins_market_data(limit: int = 300):
    """Return market data for top `limit` coins sorted by market cap."""
    per_page = 250
    coins = []
    for page in range(1, (limit - 1) // per_page + 2):
        page_limit = min(per_page, limit - len(coins))
        url = (
            f"{COINGECKO_BASE}/coins/markets?vs_currency=usd&order=market_cap_desc"
            f"&per_page={page_limit}&page={page}"
        )
        try:
            resp = requests.get(url)
            resp.raise_for_status()
        except requests.RequestException as exc:
            print(f"Failed to fetch market data page {page}: {exc}")
            return []

        coins.extend(resp.json())
    return coins[:limit]


def fetch_market_chart(coin_id: str, days: int = 30):
    """Fetch historical market chart data for a coin.

    On network failure the function prints an error and returns two empty
    lists so any correlation calculations can safely proceed with zero data.
    """
    url = f"{COINGECKO_BASE}/coins/{coin_id}/market_chart?vs_currency=usd&days={days}"
    try:
        resp = requests.get(url)
        resp.raise_for_status()
    except requests.RequestException as exc:
        print(f"Failed to fetch market chart for {coin_id}: {exc}")
        return [], []

    data = resp.json()
    return data.get("prices", []), data.get("market_caps", [])


def average_change_24h(coins) -> float:
    """Compute average 24h price change percentage for given coins."""
    return mean(c.get("price_change_percentage_24h", 0.0) for c in coins)


def coin_change(coins, coin_id: str) -> float:
    """Return 24h price change percentage for a specific coin id."""
    for coin in coins:
        if coin.get("id") == coin_id:
            return coin.get("price_change_percentage_24h", 0.0)
    return 0.0


def correlation_for_timeframe(series_a, series_b):
    """Return the correlation between two numeric series.

    If the correlation cannot be calculated because one of the series is
    constant (zero variance) or has insufficient data, ``0.0`` is returned
    instead of raising ``StatisticsError``.
    """

    try:
        return correlation(series_a, series_b)
    except StatisticsError:
        return 0.0


def risk_signal(usdt_dom: float, avg_change: float) -> str:
    """Determine market risk signal based on dominance and average change."""
    if usdt_dom < 4.0 and avg_change > 0:
        return "bullish"
    if usdt_dom > 5.5 and avg_change < 0:
        return "bearish"
    return "neutral"


def main(coin_id: str = "bitcoin"):
    usdt_dom = get_usdt_dominance()
    coins = get_top_coins_market_data()
    avg_change = average_change_24h(coins)
    coin_specific = coin_change(coins, coin_id)
    signal = risk_signal(usdt_dom, avg_change)

    print(f"USDT dominance: {usdt_dom:.2f}%")
    print(f"Avg 24h change (top 300): {avg_change:.2f}%")
    print(f"{coin_id} 24h change: {coin_specific:.2f}%")
    print(f"Market signal: {signal}")


if __name__ == "__main__":
    import sys

    coin = sys.argv[1] if len(sys.argv) > 1 else "bitcoin"
    main(coin)
