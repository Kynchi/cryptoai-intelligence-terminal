from __future__ import annotations

from forecasting.backtesting import BacktestingEngine
from indicators.technical import add_technical_indicators
from tests.test_indicators import sample_frame


def test_backtest_returns_core_quant_metrics():
    df = add_technical_indicators(sample_frame(180))
    result = BacktestingEngine().run_signal_backtest(df)
    assert isinstance(result.roi, float)
    assert isinstance(result.sharpe_ratio, float)
    assert isinstance(result.win_rate, float)
    assert isinstance(result.max_drawdown, float)
    assert result.final_equity >= 0
