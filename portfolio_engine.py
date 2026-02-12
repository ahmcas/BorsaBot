import math
from typing import List, Dict

class PortfolioEngine:
    """
    Adaptive Risk + Allocation + System Strength Engine
    """

    def __init__(self, total_capital: float = 100000):
        self.total_capital = total_capital
        self.max_risk_per_trade = 0.02  # %2 risk

    # ---------------------------------------------------
    # 1️⃣ CONFIDENCE SCORE
    # ---------------------------------------------------
    def calculate_confidence(self, rec: Dict, signal_stats: Dict = None) -> float:

        base_score = rec.get("final_score", 50)
        volatility = rec.get("volatility", 5) or 5
        alpha = rec.get("alpha_vs_benchmark", 0)

        win_rate_weight = 1.0

        if signal_stats:
            signals = rec.get("signals", [])
            weights = []

            for sig in signals:
                if sig in signal_stats:
                    weights.append(signal_stats[sig]["win_rate"] / 100)

            if weights:
                win_rate_weight = sum(weights) / len(weights)

        confidence = (base_score * win_rate_weight * (1 + alpha/100)) / (volatility if volatility != 0 else 1)

        return round(confidence, 2)

    # ---------------------------------------------------
    # 2️⃣ MARKET REGIME CASH RULE
    # ---------------------------------------------------
    def determine_cash_ratio(self, regime: str) -> float:

        mapping = {
            "STRONG_BULL": 0.10,
            "BULL": 0.25,
            "NEUTRAL": 0.50,
            "BEAR": 0.70,
            "CRISIS": 0.85
        }

        return mapping.get(regime, 0.50)

    # ---------------------------------------------------
    # 3️⃣ POSITION SIZING
    # ---------------------------------------------------
    def calculate_position_size(self, entry_price: float, atr: float) -> Dict:

        stop_price = entry_price - (atr * 1.5)
        risk_per_share = entry_price - stop_price

        if risk_per_share <= 0:
            return {"shares": 0, "stop_price": stop_price}

        capital_risk = self.total_capital * self.max_risk_per_trade
        shares = capital_risk / risk_per_share

        return {
            "shares": math.floor(shares),
            "stop_price": round(stop_price, 2)
        }

    # ---------------------------------------------------
    # 4️⃣ PORTFOLIO ALLOCATION
    # ---------------------------------------------------
    def allocate_portfolio(self, recommendations: List[Dict], regime: str) -> Dict:

        cash_ratio = self.determine_cash_ratio(regime)
        investable_capital = self.total_capital * (1 - cash_ratio)

        # confidence hesapla
        for rec in recommendations:
            rec["confidence"] = self.calculate_confidence(rec)

        total_confidence = sum(r["confidence"] for r in recommendations if r["confidence"] > 0)

        allocations = []

        for rec in recommendations:
            if total_confidence == 0:
                weight = 0
            else:
                weight = rec["confidence"] / total_confidence

            allocation_amount = investable_capital * weight

            atr = rec.get("atr", rec.get("volatility", 5))
            entry = rec.get("entry_price", rec.get("price"))

            position = self.calculate_position_size(entry, atr)

            allocations.append({
                "ticker": rec.get("ticker"),
                "weight_pct": round(weight * 100, 2),
                "allocation_amount": round(allocation_amount, 2),
                "shares": position["shares"],
                "entry_price": entry,
                "stop_price": position["stop_price"],
                "confidence": rec["confidence"]
            })

        return {
            "cash_ratio_pct": round(cash_ratio * 100, 2),
            "cash_amount": round(self.total_capital * cash_ratio, 2),
            "positions": allocations
        }

    # ---------------------------------------------------
    # 5️⃣ SYSTEM STRENGTH SCORE
    # ---------------------------------------------------
    def calculate_system_strength(self, performance_report: Dict) -> Dict:

        win_rate = performance_report.get("win_rate", 0)
        avg_return = performance_report.get("avg_return_pct", 0)

        score = (win_rate * 0.6) + (avg_return * 4)

        score = max(0, min(score, 100))

        if score >= 75:
            risk_level = "LOW"
        elif score >= 50:
            risk_level = "MEDIUM"
        else:
            risk_level = "HIGH"

        return {
            "system_strength_score": round(score, 2),
            "risk_level": risk_level
        }
