import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import requests
import usdt_dominance


def test_get_usdt_dominance_error(monkeypatch, capsys):
    def fake_get(*args, **kwargs):
        raise requests.RequestException("boom")

    monkeypatch.setattr(usdt_dominance.requests, "get", fake_get)
    dom = usdt_dominance.get_usdt_dominance()
    assert dom == 0.0
    captured = capsys.readouterr()
    assert "Failed to fetch USDT dominance" in captured.out


def test_get_top_coins_market_data_error(monkeypatch, capsys):
    def fake_get(*args, **kwargs):
        raise requests.RequestException("boom")

    monkeypatch.setattr(usdt_dominance.requests, "get", fake_get)
    data = usdt_dominance.get_top_coins_market_data()
    assert data == []
    captured = capsys.readouterr()
    assert "Failed to fetch market data" in captured.out

