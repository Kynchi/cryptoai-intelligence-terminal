export type SignalAction = "BUY" | "SELL" | "HOLD";

export interface ForecastPoint {
  horizon: number;
  predicted_close: number;
  lower_80: number;
  upper_80: number;
  lower_95: number;
  upper_95: number;
}

export interface HistoricalPoint {
  Timestamp: string;
  Open: number;
  High: number;
  Low: number;
  Close: number;
  Volume: number;
}

export interface LeaderboardRecord {
  model_name: string;
  status: string;
  trained_at?: string;
  metrics?: {
    val_rmse?: number;
    val_mae?: number;
    val_mape?: number;
  };
}

export interface PredictionPayload {
  symbol: string;
  model_used: string;
  model_status: string;
  current_price: number;
  forecast: ForecastPoint[];
  signal: {
    action: SignalAction;
    score: number;
    expected_return: number;
    risk_level: string;
    rationale: string[];
  };
  sentiment: {
    symbol: string;
    score: number;
    normalized_score: number;
    label: string;
    derived_from: string[];
    components: Record<string, number>;
  };
  explainability: {
    method: string;
    feature_importance: Array<{ feature: string; importance: number }>;
    summary: string;
  };
  historical: HistoricalPoint[];
  leaderboard: LeaderboardRecord[];
}

export interface MarketSnapshot {
  price: number;
  change_24h: number;
  volume_24h: number;
  market_cap: number;
  dominance: number;
  market_sentiment_score: number;
  ai_recommendation: SignalAction;
  confidence: number;
}

export interface MarketIntelligence {
  whale_activity: number;
  exchange_inflow: number;
  exchange_outflow: number;
  open_interest: number;
  funding_rate: number;
  liquidation_heatmap: Array<{ bucket: number; price: number; intensity: number; side: "long" | "short" }>;
  market_structure: string;
  trend_analysis: {
    momentum_30d: number;
    volatility_30d: number;
    ema200_distance: number;
  };
}

export interface RiskSnapshot {
  volatility: number;
  var_95: number;
  cvar_95: number;
  risk_score: number;
  monte_carlo: Array<{ percentile: number; values: number[] }>;
}

export interface PortfolioSnapshot {
  portfolio_value: number;
  pnl: number;
  risk_exposure: number;
  asset_allocation: Array<{
    symbol: string;
    weight: number;
    value: number;
    price: number;
    pnl_30d: number;
    risk_exposure: number;
  }>;
}

export interface BacktestPayload {
  roi: number;
  sharpe_ratio: number;
  sortino_ratio: number;
  calmar_ratio: number;
  win_rate: number;
  max_drawdown: number;
  profit_factor: number;
  final_equity: number;
  trades: number;
  equity_curve: Array<{ timestamp: string; equity: number; close: number; position: number }>;
}

export interface ModelComparisonRow {
  rank: number;
  model: string;
  accuracy: number;
  mape: number;
  rmse: number;
  mae: number;
  r2: number;
  training_time: string;
  last_training: string;
  status: string;
}

export interface AiInsight {
  headline: string;
  probability: number;
  target_30d: number;
  risk_level: string;
  narrative: string;
}

export interface TerminalPayload {
  symbol: string;
  prediction: PredictionPayload;
  market: MarketSnapshot;
  intelligence: MarketIntelligence;
  risk: RiskSnapshot;
  portfolio: PortfolioSnapshot;
  backtest: BacktestPayload;
  model_comparison: ModelComparisonRow[];
  ai_insight: AiInsight;
}
