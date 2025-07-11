import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import requests
import usdt_dominance


def test_usdt_dominance_failure(monkeypatch, capsys):
    def fake_get(*args, **kwargs):
        raise requests.RequestException("boom")

    monkeypatch.setattr(usdt_dominance.requests, "get", fake_get)
    result = usdt_dominance.get_usdt_dominance()
    captured = capsys.readouterr()
    assert result == 0.0
    assert "Failed to fetch USDT dominance" in captured.out


def test_top_coins_market_data_failure(monkeypatch, capsys):
    def fake_get(*args, **kwargs):
        raise requests.RequestException("boom")

    monkeypatch.setattr(usdt_dominance.requests, "get", fake_get)
    result = usdt_dominance.get_top_coins_market_data()
    captured = capsys.readouterr()
    assert result == []
    assert "Failed to fetch market data" in captured.out
