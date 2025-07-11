import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import usdt_dominance
import requests


def test_get_usdt_dominance(monkeypatch):
    def fake_get(url):
        class Resp:
            def raise_for_status(self):
                pass

            def json(self):
                return {"data": {"market_cap_percentage": {"usdt": 6.5}}}

        return Resp()

    monkeypatch.setattr(requests, "get", fake_get)
    result = usdt_dominance.get_usdt_dominance()
    assert result == 6.5


def test_get_top_coins_market_data(monkeypatch):
    calls = []

    def fake_get(url):
        calls.append(url)

        class Resp:
            def raise_for_status(self):
                pass

            def json(self):
                if "page=1" in url:
                    return [{"id": str(i)} for i in range(250)]
                return [{"id": str(i)} for i in range(250, 260)]

        return Resp()

    monkeypatch.setattr(requests, "get", fake_get)
    data = usdt_dominance.get_top_coins_market_data(limit=260)
    assert len(data) == 260
    assert len(calls) == 2
    assert "page=1" in calls[0]
    assert "page=2" in calls[1]


def test_risk_signal():
    assert usdt_dominance.risk_signal(3.9, 1) == "bullish"
    assert usdt_dominance.risk_signal(6.0, -1) == "bearish"
    assert usdt_dominance.risk_signal(5.0, 0.1) == "neutral"


def test_fetch_market_chart_success(monkeypatch):
    def fake_get(url):
        class Resp:
            def raise_for_status(self):
                pass

            def json(self):
                return {"prices": [1, 2], "market_caps": [3, 4]}

        return Resp()

    monkeypatch.setattr(requests, "get", fake_get)
    prices, caps = usdt_dominance.fetch_market_chart("bitcoin", days=7)
    assert prices == [1, 2]
    assert caps == [3, 4]


def test_fetch_market_chart_failure(monkeypatch, capsys):
    def fake_get(url):
        raise requests.RequestException("oops")

    monkeypatch.setattr(requests, "get", fake_get)
    prices, caps = usdt_dominance.fetch_market_chart("bitcoin")
    captured = capsys.readouterr()
    assert "Failed to fetch market chart" in captured.out
    assert prices == []
    assert caps == []
