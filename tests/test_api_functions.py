import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import builtins
from unittest.mock import Mock, patch
import requests
import usdt_dominance


def make_response(json_data):
    resp = Mock()
    resp.json.return_value = json_data
    resp.raise_for_status = Mock()
    return resp


def test_get_usdt_dominance():
    data = {"data": {"market_cap_percentage": {"usdt": 4.2}}}
    with patch("usdt_dominance.requests.get", return_value=make_response(data)) as mock_get:
        dom = usdt_dominance.get_usdt_dominance()
        assert dom == 4.2
        mock_get.assert_called_once_with(f"{usdt_dominance.COINGECKO_BASE}/global")


def test_get_top_coins_market_data():
    coins_page1 = [{"id": f"coin{i}"} for i in range(1, 251)]
    coins_page2 = [{"id": f"coin{250 + i}"} for i in range(1, 51)]
    with patch("usdt_dominance.requests.get") as mock_get:
        mock_get.side_effect = [make_response(coins_page1), make_response(coins_page2)]
        coins = usdt_dominance.get_top_coins_market_data(limit=300)
        assert len(coins) == 300
        assert coins[0]["id"] == "coin1"
        assert coins[-1]["id"] == "coin300"


def test_risk_signal():
    assert usdt_dominance.risk_signal(3.9, 0.1) == "bullish"
    assert usdt_dominance.risk_signal(5.6, -0.1) == "bearish"
    assert usdt_dominance.risk_signal(5.0, 0) == "neutral"


def test_fetch_market_chart_success():
    data = {"prices": [1, 2], "market_caps": [3, 4]}
    with patch("usdt_dominance.requests.get", return_value=make_response(data)):
        prices, caps = usdt_dominance.fetch_market_chart("bitcoin", days=1)
        assert prices == [1, 2]
        assert caps == [3, 4]


def test_fetch_market_chart_failure(capsys):
    def raise_exc(*args, **kwargs):
        raise requests.RequestException("boom")

    with patch("usdt_dominance.requests.get", side_effect=raise_exc):
        prices, caps = usdt_dominance.fetch_market_chart("btc", days=1)
        assert prices == []
        assert caps == []
        captured = capsys.readouterr()
        assert "Failed to fetch market chart for btc" in captured.out
