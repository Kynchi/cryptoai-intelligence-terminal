# Professional AI-Powered Crypto Forecasting Ecosystem

Production-grade AI forecasting platform untuk BTC, ETH, SOL, dan XRP. Project ini mengganti aplikasi Flask univariate lama menjadi ekosistem modular berbasis FastAPI, multivariate feature engineering, deep learning model registry, probabilistic inference, market-derived sentiment analysis, explainability, dashboard fintech, backtesting, dan deployment-ready container.

Frontend terbaru adalah **CryptoAI Intelligence Terminal**: React + TypeScript + TailwindCSS dashboard bergaya Bloomberg Terminal, TradingView Premium, CoinGlass, CryptoQuant, dan institutional quant desk.

## Capabilities

- Multi-coin forecasting: BTC, ETH, SOL, XRP.
- Multivariate OHLCV + indikator teknikal: RSI, MACD, EMA, SMA, Bollinger Bands, ATR, VWAP, OBV, ROC, Momentum, Volatility.
- Model factory: LSTM, GRU, BiLSTM, CNN+LSTM, CNN+BiLSTM, CNN+LSTM+Attention, Transformer, Temporal Fusion Transformer-style, N-BEATS, XGBoost Hybrid, LightGBM Hybrid.
- Multi-output horizons: 1, 3, 7, 30, 90, 180, 365 hari.
- Confidence interval dan uncertainty estimation.
- CoinMarketCap ingestion, local seed fallback, processed dataset cache.
- MLflow experiment tracking, Optuna/Keras Tuner hooks.
- Trading signal engine: BUY, SELL, HOLD.
- Backtesting: ROI, Sharpe Ratio, Win Rate, Maximum Drawdown.
- Explainability: SHAP-ready dan correlation fallback.
- Market sentiment gauge: score 0-100 dari RSI, MACD, volume momentum, price momentum, dan EMA trend tanpa API eksternal.
- FastAPI endpoints dan React terminal dashboard dengan ECharts, Recharts-ready structure, TailwindCSS, shadcn-style UI primitives, Framer Motion, and institutional dark theme.
- Docker, docker-compose, GitHub Actions CI.

## Architecture

```text
app/              FastAPI application bootstrap and monitoring middleware
api/              API schemas and route handlers
forecasting/      preprocessing, inference, evaluation, backtesting, signals, explainability
models/           deep model factories, hybrid model wrappers, artifact registry
indicators/       technical indicators and feature generation
services/         CoinMarketCap ingestion, dataset repository, market sentiment, scheduler
utils/            config, logging, path utilities
configs/          JSON/YAML platform configuration
datasets/         raw and processed market data
training/         training pipeline, tuning hooks, CLI
frontend/         dashboard UI
frontend/src/
  api/            cached API client
  assets/         CryptoAI logo assets
  charts/         ECharts-based forecasting, risk, portfolio, heatmap charts
  components/     layout and shadcn-style UI primitives
  hooks/          terminal data provider
  models/         TypeScript API models
  pages/          Dashboard, Market, Forecasting, Model Lab, Sentiment, Portfolio, Backtesting, Risk, Leaderboard, Settings
  styles/         Tailwind global terminal design system
deployment/       deployment notes
tests/            smoke and unit tests
```

Legacy notebook/model assets from the original project remain outside the new runtime path. The new platform uses reusable pipelines instead of duplicated per-coin notebooks.

## Quick Start

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Open `http://localhost:8000`.

For frontend development:

```bash
cd frontend
npm install
npm run dev
```

For production frontend build:

```bash
cd frontend
npm run build
```

Without API keys, the app runs from `datasets/raw/*.csv`. With `COINMARKETCAP_API_KEY`, `/realtime` updates datasets from CoinMarketCap. The sentiment gauge does not require any external API key.

## API

```bash
curl http://localhost:8000/health
curl -X POST http://localhost:8000/predict -H "Content-Type: application/json" -d "{\"symbol\":\"BTC\",\"horizons\":[1,3,7,30]}"
curl -X POST http://localhost:8000/evaluate -H "Content-Type: application/json" -d "{\"symbol\":\"BTC\",\"horizon\":1,\"windows\":120}"
curl -X POST http://localhost:8000/backtest -H "Content-Type: application/json" -d "{\"symbol\":\"BTC\",\"lookahead\":7}"
curl -X POST http://localhost:8000/realtime -H "Content-Type: application/json" -d "{\"symbols\":[\"BTC\"],\"retrain\":false}"
curl "http://localhost:8000/terminal?symbol=BTC"
curl "http://localhost:8000/market-intelligence?symbol=BTC"
curl "http://localhost:8000/risk?symbol=BTC"
curl "http://localhost:8000/portfolio"
```

## Training Workflow

1. `services.dataset_repository.DatasetRepository` loads raw OHLCV CSV or live CoinMarketCap data.
2. `indicators.technical.add_technical_indicators` creates the multivariate feature frame.
3. `forecasting.preprocessing.build_sequence_dataset` creates sequence-to-sequence training samples.
4. `training.train.TrainingPipeline` selects the configured model factory.
5. Deep models use TensorFlow callbacks: Dropout, BatchNormalization, EarlyStopping, ReduceLROnPlateau, L2 regularization.
6. Hybrid models use XGBoost/LightGBM with multi-output wrappers.
7. The scaler, model artifact, metrics, feature names, horizons, and metadata are registered in `models/registry`.
8. MLflow logs params, metrics, and artifacts when installed and configured.

Example:

```bash
python -m training.cli --symbol BTC --model cnn_lstm_attention --epochs 50 --sequence-length 60
```

## Inference Workflow

1. `/predict` loads the best registered model for the coin and optional model name.
2. If a trained artifact exists, the latest scaled sequence is passed to TensorFlow or hybrid estimator.
3. If no artifact exists yet, the platform uses a volatility and momentum-aware probabilistic forecaster so the API/dashboard remain runnable immediately.
4. Forecast outputs are mapped to configured horizons with 80% and 95% confidence intervals.
5. Market-derived sentiment, feature importance, trading signal, historical OHLCV, and leaderboard are returned in one response.

## Market Sentiment Gauge

The Realtime Sentiment Gauge is computed entirely from internal market data:

- 30% RSI
- 30% MACD
- 20% volume momentum
- 20% price momentum
- EMA trend as a stabilizing technical adjustment

Score mapping:

- `0-30`: Extreme Fear
- `31-45`: Bearish
- `46-55`: Neutral
- `56-70`: Bullish
- `71-100`: Extreme Greed

## Docker

```bash
cp .env.example .env
docker compose up --build
```

Services:

- API dashboard: `http://localhost:8000`
- MLflow: `http://localhost:5000`

## Environment Variables

- `COINMARKETCAP_API_KEY`: live market data ingestion.
- `CRYPTO_FORECAST_CONFIG`: config file path, default `configs/config.json`.

## Testing

```bash
python tests/smoke_check.py
pytest tests
```

The smoke check validates processed dataset generation, inference, and backtesting without requiring TensorFlow or API keys.
