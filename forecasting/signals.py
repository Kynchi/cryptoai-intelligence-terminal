from __future__ import annotations

from dataclasses import dataclass


@dataclass
class TradingSignal:
    action: str
    score: float
    expected_return: float
    risk_level: str
    rationale: list[str]


class TradingSignalEngine:
    def __init__(self, buy_threshold: float = 0.015, sell_threshold: float = -0.015):
        self.buy_threshold = buy_threshold
        self.sell_threshold = sell_threshold

    def generate(
        self,
        current_price: float,
        forecast_price: float,
        lower_95: float,
        upper_95: float,
        volatility: float,
        sentiment_score: float = 0.0,
    ) -> TradingSignal:
        expected_return = (forecast_price - current_price) / current_price
        downside = max(0.0, (current_price - lower_95) / current_price)
        upside = max(0.0, (upper_95 - current_price) / current_price)
        risk_adjusted = expected_return / max(volatility, 1e-6)
        score = 0.75 * risk_adjusted + 0.25 * sentiment_score

        if expected_return >= self.buy_threshold and upside > downside:
            action = "BUY"
        elif expected_return <= self.sell_threshold and downside >= upside:
            action = "SELL"
        else:
            action = "HOLD"

        risk_level = "LOW"
        if volatility > 0.055 or downside > 0.18:
            risk_level = "HIGH"
        elif volatility > 0.03 or downside > 0.09:
            risk_level = "MEDIUM"

        rationale = [
            f"Expected return {expected_return:.2%}",
            f"95% downside {downside:.2%}",
            f"Volatility {volatility:.2%}",
            f"Market sentiment score {sentiment_score:.2f}",
        ]
        return TradingSignal(action, float(score), float(expected_return), risk_level, rationale)
