from __future__ import annotations

from dataclasses import asdict
from typing import Any

from fastapi import APIRouter, HTTPException

from api.schemas import BacktestRequest, EvaluateRequest, PredictRequest, RealtimeRequest, TrainRequest
from forecasting.backtesting import BacktestingEngine
from forecasting.evaluation import EvaluationPipeline
from forecasting.inference import ForecastingEngine
from services.data_ingestion import DataIngestionService
from services.dataset_repository import DatasetRepository
from services.scheduler import RetrainingScheduler
from services.terminal_analytics import TerminalAnalyticsService
from training.train import TrainingPipeline
from utils.config import load_settings


router = APIRouter()


@router.get("/health")
def health() -> dict[str, Any]:
    settings = load_settings()
    return {
        "status": "ok",
        "project": settings.get("project.name"),
        "version": settings.get("project.version"),
        "coins": sorted(settings.coins),
    }


@router.get("/coins")
def coins() -> dict[str, Any]:
    settings = load_settings()
    return {"coins": settings.coins}


@router.post("/predict")
def predict(request: PredictRequest) -> dict[str, Any]:
    try:
        return ForecastingEngine().predict(
            symbol=request.symbol,
            horizons=request.horizons,
            model_name=request.model_name,
        )
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/train")
def train(request: TrainRequest) -> dict[str, Any]:
    try:
        return TrainingPipeline().train(
            symbol=request.symbol,
            model_name=request.model_name,
            overrides=request.overrides,
        )
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/evaluate")
def evaluate(request: EvaluateRequest) -> dict[str, Any]:
    try:
        df = DatasetRepository().load_processed(request.symbol)
        report = EvaluationPipeline().evaluate_baseline(df, horizon=request.horizon, windows=request.windows)
        return asdict(report)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/backtest")
def backtest(request: BacktestRequest) -> dict[str, Any]:
    try:
        settings = load_settings()
        df = DatasetRepository(settings).load_processed(request.symbol)
        engine = BacktestingEngine(
            initial_cash=float(settings.get("backtesting.initial_cash", 10000)),
            fee_rate=float(settings.get("backtesting.fee_rate", 0.001)),
            buy_threshold=float(settings.get("backtesting.buy_threshold", 0.015)),
            sell_threshold=float(settings.get("backtesting.sell_threshold", -0.015)),
        )
        return asdict(engine.run_signal_backtest(df, lookahead=request.lookahead))
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/realtime")
def realtime() -> dict[str, Any]:
    try:
        return ForecastingEngine().realtime_snapshot()
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/realtime")
def update_realtime(request: RealtimeRequest) -> dict[str, Any]:
    try:
        if request.retrain:
            status = RetrainingScheduler().run_once(retrain=True, model_name=request.model_name)
            return asdict(status)
        ingestion = DataIngestionService()
        results = (
            [ingestion.update_symbol(symbol) for symbol in request.symbols]
            if request.symbols
            else ingestion.update_all()
        )
        return {"updates": [asdict(result) for result in results]}
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/leaderboard")
def leaderboard(symbol: str | None = None) -> dict[str, Any]:
    try:
        return {"leaderboard": ForecastingEngine().registry.leaderboard(symbol)}
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/terminal")
def terminal(symbol: str = "BTC") -> dict[str, Any]:
    try:
        return TerminalAnalyticsService().terminal(symbol)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/market-intelligence")
def market_intelligence(symbol: str = "BTC") -> dict[str, Any]:
    try:
        service = TerminalAnalyticsService()
        df = service.repository.load_processed(symbol)
        return service.market_intelligence(df)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/risk")
def risk(symbol: str = "BTC") -> dict[str, Any]:
    try:
        service = TerminalAnalyticsService()
        df = service.repository.load_processed(symbol)
        return service.risk_snapshot(df)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/portfolio")
def portfolio() -> dict[str, Any]:
    try:
        return TerminalAnalyticsService().portfolio_snapshot()
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
