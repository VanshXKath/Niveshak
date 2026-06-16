from __future__ import annotations

import json
from pathlib import Path

from backend.app.models.sector import SectorAnalysisResponse, SectorPerformance
from backend.app.services.stock_service import StockService

SECTOR_PATH = Path(__file__).resolve().parent.parent / "data" / "sector_map.json"


class SectorService:
    def __init__(self) -> None:
        self._stock_service = StockService()

    def analyze(self, period: str = "3mo") -> SectorAnalysisResponse:
        sector_map = self._load_sectors()
        performances: list[SectorPerformance] = []

        for sector, symbols in sector_map.items():
            changes: list[float] = []
            top_symbol = None
            top_change = float("-inf")

            for symbol in symbols:
                try:
                    history = self._stock_service.get_stock_history(symbol, period=period, interval="1d")
                    prices = [point.close for point in history.prices if point.close]
                    if len(prices) < 2:
                        continue
                    change = ((prices[-1] - prices[0]) / prices[0]) * 100
                    changes.append(change)
                    if change > top_change:
                        top_change = change
                        top_symbol = symbol
                except Exception:
                    continue

            avg_change = sum(changes) / len(changes) if changes else None
            momentum = self._momentum_score(avg_change)
            performances.append(
                SectorPerformance(
                    sector=sector,
                    average_change_percent=round(avg_change, 2) if avg_change is not None else None,
                    momentum_score=momentum,
                    rank=0,
                    top_stock=top_symbol,
                    explanation=self._sector_explain(sector, avg_change),
                )
            )

        performances.sort(key=lambda item: item.momentum_score, reverse=True)
        performances = [
            item.model_copy(update={"rank": index}) for index, item in enumerate(performances, start=1)
        ]

        strongest = performances[0].sector if performances else None
        weakest = performances[-1].sector if performances else None
        summary = (
            f"Sector momentum scan over {period} (StockEdge / StockScans inspired). "
            f"Strongest: {strongest or 'N/A'}. Weakest: {weakest or 'N/A'}. "
            "Sector rotation helps beginners avoid betting on one industry only."
        )

        return SectorAnalysisResponse(
            period=period,
            sectors=performances,
            strongest_sector=strongest,
            weakest_sector=weakest,
            beginner_summary=summary,
        )

    def _momentum_score(self, change: float | None) -> float:
        if change is None:
            return 0.0
        return max(-100.0, min(100.0, change * 2))

    def _sector_explain(self, sector: str, change: float | None) -> str:
        if change is None:
            return f"No usable data for {sector}."
        if change > 5:
            return f"{sector} is leading — strong relative performance."
        if change < -5:
            return f"{sector} is lagging — weak relative performance."
        return f"{sector} is moving near market average."

    def _load_sectors(self) -> dict[str, list[str]]:
        try:
            with SECTOR_PATH.open(encoding="utf-8") as file:
                return json.load(file)
        except (OSError, json.JSONDecodeError):
            return {}
