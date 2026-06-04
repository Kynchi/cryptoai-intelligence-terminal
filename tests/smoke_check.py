from __future__ import annotations

import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from forecasting.backtesting import BacktestingEngine
from forecasting.inference import ForecastingEngine
from services.dataset_repository import DatasetRepository


def main() -> None:
    repository = DatasetRepository()
    df = repository.load_processed("BTC", refresh=True)
    assert len(df) > 100, "BTC seed dataset should contain enough rows"
    prediction = ForecastingEngine().predict("BTC", horizons=[1, 3, 7])
    assert prediction["forecast"], "Forecast response should contain forecast points"
    backtest = BacktestingEngine().run_signal_backtest(df)
    assert backtest.final_equity >= 0
    print("smoke_check=ok")


if __name__ == "__main__":
    main()
