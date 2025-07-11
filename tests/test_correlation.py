import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import usdt_dominance


def test_constant_series():
    data = [1, 1, 1, 1]
    result = usdt_dominance.correlation_for_timeframe(data, data)
    assert result == 0.0
