from __future__ import annotations

from backend.app.db.database import get_connection
from backend.app.models.portfolio import PortfolioAnalysisResponse, PortfolioHolding, PortfolioHoldingInput
from backend.app.portfolio_analysis.sector_mapping import map_sector
from backend.app.services.stock_service import StockService


class PortfolioService:
    def __init__(self) -> None:
        self._stock_service = StockService()

    def add_holding(self, holding: PortfolioHoldingInput) -> PortfolioHolding:
        symbol = holding.symbol.strip().upper().replace(".NS", "")
        with get_connection() as connection:
            cursor = connection.execute(
                "INSERT INTO portfolio_holdings (symbol, quantity, avg_price) VALUES (?, ?, ?)",
                (symbol, holding.quantity, holding.avg_price),
            )
            connection.commit()
            row_id = cursor.lastrowid

        return PortfolioHolding(
            id=row_id,
            symbol=symbol,
            quantity=holding.quantity,
            avg_price=holding.avg_price,
        )

    def remove_holding(self, holding_id: int) -> None:
        with get_connection() as connection:
            connection.execute("DELETE FROM portfolio_holdings WHERE id = ?", (holding_id,))
            connection.commit()

    def analyze(self, fetch_live: bool = False) -> PortfolioAnalysisResponse:
        with get_connection() as connection:
            rows = connection.execute("SELECT id, symbol, quantity, avg_price FROM portfolio_holdings").fetchall()

        holdings: list[PortfolioHolding] = []
        sector_exposure: dict[str, float] = {}
        total_invested = 0.0
        total_value = 0.0

        for row in rows:
            invested = row["quantity"] * row["avg_price"]
            total_invested += invested
            current_price = None
            sector = map_sector(row["symbol"])

            if fetch_live:
                try:
                    summary = self._stock_service.get_stock_summary(row["symbol"])
                    current_price = summary.current_price
                    if summary.sector:
                        sector = summary.sector
                except Exception:
                    pass

            market_value = (current_price or row["avg_price"]) * row["quantity"]
            total_value += market_value
            pnl = market_value - invested
            pnl_pct = (pnl / invested * 100) if invested else None

            holdings.append(
                PortfolioHolding(
                    id=row["id"],
                    symbol=row["symbol"],
                    quantity=row["quantity"],
                    avg_price=row["avg_price"],
                    current_price=current_price,
                    market_value=round(market_value, 2),
                    pnl=round(pnl, 2),
                    pnl_percent=round(pnl_pct, 2) if pnl_pct is not None else None,
                    sector=sector,
                )
            )
            sector_exposure[sector] = sector_exposure.get(sector, 0.0) + market_value

        if total_value > 0:
            sector_exposure = {k: round(v / total_value * 100, 2) for k, v in sector_exposure.items()}

        diversification = self._diversification_score(sector_exposure)
        risk = self._risk_label(diversification, len(holdings))
        recommendations = self._recommendations(sector_exposure, len(holdings))
        total_pnl = total_value - total_invested
        total_pnl_pct = (total_pnl / total_invested * 100) if total_invested else None

        summary = (
            f"Portfolio health check (Groww portfolio inspired): {len(holdings)} holdings, "
            f"diversification score {diversification:.0f}/100, risk level {risk}."
        )

        return PortfolioAnalysisResponse(
            holdings=holdings,
            total_invested=round(total_invested, 2),
            total_current_value=round(total_value, 2),
            total_pnl=round(total_pnl, 2),
            total_pnl_percent=round(total_pnl_pct, 2) if total_pnl_pct is not None else None,
            diversification_score=diversification,
            risk_score=risk,
            sector_exposure=sector_exposure,
            recommendations=recommendations,
            beginner_summary=summary,
        )

    def _diversification_score(self, sector_exposure: dict[str, float]) -> float:
        if not sector_exposure:
            return 0.0
        max_weight = max(sector_exposure.values())
        sector_count = len(sector_exposure)
        score = min(sector_count * 15, 60) + max(0, 40 - max_weight)
        return round(min(100.0, score), 2)

    def _risk_label(self, diversification: float, count: int) -> str:
        if count <= 1:
            return "High"
        if diversification >= 70:
            return "Moderate"
        if diversification >= 45:
            return "Moderate-High"
        return "High"

    def _recommendations(self, sector_exposure: dict[str, float], count: int) -> list[str]:
        recs: list[str] = []
        if count < 3:
            recs.append("Add more stocks or index funds to reduce single-stock risk.")
        if sector_exposure:
            top_sector = max(sector_exposure, key=sector_exposure.get)
            if sector_exposure[top_sector] > 50:
                recs.append(f"Over {sector_exposure[top_sector]:.0f}% in {top_sector} — consider diversifying sectors.")
        if not recs:
            recs.append("Portfolio looks reasonably balanced for a learning portfolio.")
        return recs
