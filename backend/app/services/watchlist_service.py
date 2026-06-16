from __future__ import annotations

from backend.app.db.database import get_connection
from backend.app.models.watchlist import (
    AlertCreateRequest,
    AlertItem,
    WatchlistAddRequest,
    WatchlistIntelligenceResponse,
    WatchlistItem,
)
from backend.app.services.stock_service import StockService
from backend.app.services.technical_service import TechnicalService


class WatchlistService:
    def __init__(self) -> None:
        self._stock_service = StockService()
        self._technical_service = TechnicalService()

    def add(self, request: WatchlistAddRequest) -> WatchlistItem:
        symbol = request.symbol.strip().upper().replace(".NS", "")
        with get_connection() as connection:
            connection.execute(
                "INSERT OR IGNORE INTO watchlist (symbol, notes) VALUES (?, ?)",
                (symbol, request.notes),
            )
            connection.commit()
            row = connection.execute("SELECT id, symbol, notes FROM watchlist WHERE symbol = ?", (symbol,)).fetchone()
        return WatchlistItem(id=row["id"], symbol=row["symbol"], notes=row["notes"])

    def remove(self, item_id: int) -> None:
        with get_connection() as connection:
            connection.execute("DELETE FROM watchlist WHERE id = ?", (item_id,))
            connection.commit()

    def add_alert(self, request: AlertCreateRequest) -> AlertItem:
        symbol = request.symbol.strip().upper().replace(".NS", "")
        with get_connection() as connection:
            cursor = connection.execute(
                "INSERT INTO alerts (symbol, alert_type, threshold, message) VALUES (?, ?, ?, ?)",
                (symbol, request.alert_type, request.threshold, request.message),
            )
            connection.commit()
            alert_id = cursor.lastrowid
        return AlertItem(
            id=alert_id,
            symbol=symbol,
            alert_type=request.alert_type,
            threshold=request.threshold,
            message=request.message,
            is_active=True,
        )

    def intelligence(self) -> WatchlistIntelligenceResponse:
        with get_connection() as connection:
            watchlist_rows = connection.execute("SELECT id, symbol, notes FROM watchlist").fetchall()
            alert_rows = connection.execute(
                "SELECT id, symbol, alert_type, threshold, message, is_active FROM alerts WHERE is_active = 1"
            ).fetchall()

        watchlist = [WatchlistItem(id=row["id"], symbol=row["symbol"], notes=row["notes"]) for row in watchlist_rows]
        alerts: list[AlertItem] = []
        triggered = 0

        for row in alert_rows:
            triggered_flag, detail = self._evaluate_alert(row)
            if triggered_flag:
                triggered += 1
            alerts.append(
                AlertItem(
                    id=row["id"],
                    symbol=row["symbol"],
                    alert_type=row["alert_type"],
                    threshold=row["threshold"],
                    message=row["message"],
                    is_active=bool(row["is_active"]),
                    triggered=triggered_flag,
                    trigger_detail=detail,
                )
            )

        summary = (
            f"Tradomate-style watchlist intelligence: {len(watchlist)} stocks tracked, "
            f"{triggered} active alert(s) triggered now."
        )

        return WatchlistIntelligenceResponse(
            watchlist=watchlist,
            alerts=alerts,
            triggered_count=triggered,
            beginner_summary=summary,
        )

    def _evaluate_alert(self, row) -> tuple[bool, str | None]:
        symbol = row["symbol"]
        alert_type = row["alert_type"]
        threshold = row["threshold"]

        try:
            if alert_type in {"price_above", "price_below"}:
                summary = self._stock_service.get_stock_summary(symbol)
                price = summary.current_price
                if price is None:
                    return False, None
                if alert_type == "price_above" and price >= threshold:
                    return True, f"Price INR {price:,.2f} is above INR {threshold:,.2f}"
                if alert_type == "price_below" and price <= threshold:
                    return True, f"Price INR {price:,.2f} is below INR {threshold:,.2f}"

            if alert_type in {"rsi_above", "rsi_below"}:
                technical = self._technical_service.analyze(symbol)
                rsi = next((item.value for item in technical.indicators if item.name.startswith("RSI")), None)
                if rsi is None:
                    return False, None
                if alert_type == "rsi_above" and rsi >= threshold:
                    return True, f"RSI {rsi:.1f} is above {threshold:.1f}"
                if alert_type == "rsi_below" and rsi <= threshold:
                    return True, f"RSI {rsi:.1f} is below {threshold:.1f}"
        except Exception:
            return False, None

        return False, None
