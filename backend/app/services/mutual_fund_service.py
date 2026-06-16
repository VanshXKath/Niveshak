from __future__ import annotations

import json
from pathlib import Path

from backend.app.models.mutual_fund import (
    FundRecommendation,
    MutualFundRecommendationRequest,
    MutualFundRecommendationResponse,
)

FUNDS_PATH = Path(__file__).resolve().parent.parent / "data" / "mutual_funds.json"


class MutualFundService:
    def recommend(self, request: MutualFundRecommendationRequest) -> MutualFundRecommendationResponse:
        catalog = self._load_catalog()
        picks = self._pick_funds(request, catalog)
        profile = (
            f"Goal: {request.goal.replace('_', ' ')} | Risk: {request.risk_appetite} | "
            f"Horizon: {request.investment_horizon_years} years | SIP: INR {request.monthly_sip:,.0f}"
        )

        recommendations: list[FundRecommendation] = []
        sip_split = request.monthly_sip / max(len(picks), 1)
        for fund in picks:
            recommendations.append(
                FundRecommendation(
                    category=fund["category"],
                    risk=fund["risk"],
                    horizon_years=fund["horizon_years"],
                    example_funds=fund["example_funds"],
                    why=fund["why"],
                    suggested_sip=round(sip_split, 2),
                )
            )

        beginner = (
            "Groww-style goal-based fund shortlist. These are educational category examples, not investment advice. "
            "Verify latest fund factsheets on AMFI or fund house websites before investing."
        )

        return MutualFundRecommendationResponse(
            profile_summary=profile,
            recommendations=recommendations,
            beginner_summary=beginner,
        )

    def _pick_funds(self, request: MutualFundRecommendationRequest, catalog: list[dict]) -> list[dict]:
        risk = request.risk_appetite.lower()
        goal = request.goal.lower()

        if goal in {"emergency_fund", "emergency"} or risk == "low":
            return [item for item in catalog if "Liquid" in item["category"] or "Debt" in item["category"]][:2]

        if goal in {"tax_saving", "tax"}:
            return [item for item in catalog if "ELSS" in item["category"]][:2]

        if risk == "high" and request.investment_horizon_years >= 7:
            return [item for item in catalog if item["category"] in {"Mid Cap", "Flexi Cap"}][:2]

        if request.investment_horizon_years >= 5:
            return [item for item in catalog if item["category"] in {"Large Cap Index", "Flexi Cap"}][:2]

        return catalog[:2]

    def _load_catalog(self) -> list[dict]:
        try:
            with FUNDS_PATH.open(encoding="utf-8") as file:
                return json.load(file)
        except (OSError, json.JSONDecodeError):
            return []
