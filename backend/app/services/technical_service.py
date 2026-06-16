from __future__ import annotations

import pandas as pd

from backend.app.models.technical import IndicatorValue, TechnicalAnalysisResponse
from backend.app.services.stock_service import StockDataError, StockService


class TechnicalService:
    def __init__(self) -> None:
        self._stock_service = StockService()

    def analyze(self, symbol: str, period: str = "6mo") -> TechnicalAnalysisResponse:
        history = self._stock_service.get_stock_history(symbol=symbol, period=period, interval="1d")
        frame = pd.DataFrame([point.model_dump() for point in history.prices])
        if frame.empty or "close" not in frame.columns:
            raise StockDataError(f"Not enough price data to run technical analysis for '{symbol}'.")

        closes = frame["close"].astype(float).dropna()
        if len(closes) < 20:
            raise StockDataError("Need at least 20 trading days of data for technical analysis.")

        rsi = self._rsi(closes)
        sma_20 = closes.rolling(20).mean().iloc[-1]
        sma_50 = closes.rolling(50).mean().iloc[-1] if len(closes) >= 50 else None
        ema_20 = closes.ewm(span=20, adjust=False).mean().iloc[-1]
        macd_line, signal_line = self._macd(closes)
        upper_bb, lower_bb = self._bollinger(closes)
        support, resistance = self._support_resistance(closes)
        current = float(closes.iloc[-1])

        indicators = [
            self._indicator("RSI (14)", rsi, self._rsi_signal(rsi), self._rsi_explain(rsi)),
            self._indicator("SMA 20", float(sma_20), self._ma_signal(current, float(sma_20)), "20-day simple moving average smooths short-term noise."),
            self._indicator("EMA 20", float(ema_20), self._ma_signal(current, float(ema_20)), "20-day exponential moving average reacts faster than SMA."),
            self._indicator("MACD", macd_line, self._macd_signal(macd_line, signal_line), "MACD tracks momentum shifts using moving averages."),
            self._indicator("Bollinger Upper", upper_bb, "neutral", "Upper volatility band — price near here can mean stretched move."),
            self._indicator("Bollinger Lower", lower_bb, "neutral", "Lower volatility band — price near here can mean oversold conditions."),
        ]
        if sma_50 is not None:
            indicators.insert(3, self._indicator("SMA 50", float(sma_50), self._ma_signal(current, float(sma_50)), "50-day average shows medium-term trend."))

        trend, trend_explain = self._detect_trend(current, sma_20, sma_50, rsi)
        summary = (
            f"Trend looks {trend.lower()}. RSI is {rsi:.1f}. "
            f"Support near INR {support:,.0f} and resistance near INR {resistance:,.0f}. "
            "Inspired by StockEdge-style scans: use this as a learning dashboard, not a buy/sell signal."
        )

        return TechnicalAnalysisResponse(
            symbol=history.symbol,
            trend=trend,
            trend_explanation=trend_explain,
            support_level=round(support, 2),
            resistance_level=round(resistance, 2),
            indicators=indicators,
            beginner_summary=summary,
        )

    def _rsi(self, closes: pd.Series, period: int = 14) -> float:
        delta = closes.diff()
        gain = delta.clip(lower=0).rolling(period).mean()
        loss = (-delta.clip(upper=0)).rolling(period).mean()
        rs = gain / loss.replace(0, pd.NA)
        value = 100 - (100 / (1 + rs))
        return float(value.iloc[-1])

    def _macd(self, closes: pd.Series) -> tuple[float, float]:
        ema_12 = closes.ewm(span=12, adjust=False).mean()
        ema_26 = closes.ewm(span=26, adjust=False).mean()
        macd = ema_12 - ema_26
        signal = macd.ewm(span=9, adjust=False).mean()
        return float(macd.iloc[-1]), float(signal.iloc[-1])

    def _bollinger(self, closes: pd.Series, period: int = 20) -> tuple[float, float]:
        sma = closes.rolling(period).mean()
        std = closes.rolling(period).std()
        return float((sma + 2 * std).iloc[-1]), float((sma - 2 * std).iloc[-1])

    def _support_resistance(self, closes: pd.Series, window: int = 20) -> tuple[float, float]:
        recent = closes.tail(window)
        return float(recent.min()), float(recent.max())

    def _detect_trend(self, price: float, sma_20: float, sma_50: float | None, rsi: float) -> tuple[str, str]:
        if sma_50 is not None and price > sma_20 > sma_50:
            return "Bullish", "Price is above short and medium moving averages — typical uptrend structure."
        if sma_50 is not None and price < sma_20 < sma_50:
            return "Bearish", "Price is below short and medium moving averages — typical downtrend structure."
        if rsi >= 60:
            return "Bullish Momentum", "RSI shows strong momentum even if trend is mixed."
        if rsi <= 40:
            return "Bearish Momentum", "RSI shows weak momentum; trend may be soft."
        return "Sideways", "No clear trend — price is moving in a range."

    def _indicator(self, name: str, value: float | None, signal: str, explanation: str) -> IndicatorValue:
        return IndicatorValue(name=name, value=round(value, 2) if value is not None else None, signal=signal, explanation=explanation)

    def _rsi_signal(self, rsi: float) -> str:
        if rsi >= 70:
            return "overbought"
        if rsi <= 30:
            return "oversold"
        return "neutral"

    def _rsi_explain(self, rsi: float) -> str:
        if rsi >= 70:
            return "RSI above 70 — stock may be overbought (priced for perfection)."
        if rsi <= 30:
            return "RSI below 30 — stock may be oversold (selling may be overdone)."
        return "RSI between 30-70 — no extreme signal."

    def _ma_signal(self, price: float, ma: float) -> str:
        return "bullish" if price >= ma else "bearish"

    def _macd_signal(self, macd: float, signal: float) -> str:
        return "bullish" if macd >= signal else "bearish"
