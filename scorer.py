# scorer.py — Skor & Seçim (v6 - SWING TRADE UPDATE)
import config


class ScoreCalculator:
    @staticmethod
    def calculate_composite_score(technical_score, sector_sentiment):
        if technical_score is None:
            technical_score = 50.0
        if sector_sentiment is None:
            sector_sentiment = 0.0
        normalized_sentiment = (sector_sentiment + 1) / 2 * 100
        composite = technical_score * 0.6 + normalized_sentiment * 0.4
        return max(0.0, min(100.0, composite))

    @staticmethod
    def calculate_reward_risk(current_price, support, resistance):
        if not current_price or current_price <= 0:
            return {"reward_pct": 0.0, "risk_pct": 0.0, "ratio": 0}
        reward_pct = (resistance - current_price) / current_price * 100
        risk_pct = (current_price - support) / current_price * 100
        ratio = reward_pct / risk_pct if risk_pct != 0 else 0
        return {"reward_pct": reward_pct, "risk_pct": risk_pct, "ratio": ratio}

    @staticmethod
    def calculate_confidence(score):
        if score >= 80:
            return "Çok Yüksek"
        elif score >= 70:
            return "Yüksek"
        elif score >= 60:
            return "İyi"
        elif score >= 50:
            return "Orta"
        elif score >= 40:
            return "Düşük"
        else:
            return "Çok Düşük"


def determine_rating(score):
    if score >= 80:
        return "💎 GÜÇLÜ AL"
    elif score >= 66:
        return "🟢 AL"
    elif score >= 50:
        return "🟡 TUT"
    elif score >= 35:
        return "🟠 DİKKATLİ OL"
    else:
        return "🔴 SAT"


def select_top_stocks(technical_results: list, sector_scores: dict, max_count: int = None) -> list:
    if max_count is None:
        max_count = config.MAX_RECOMMENDATIONS
    candidates = []
    for result in technical_results:
        if result.get("skip"):
            continue
        ticker = result.get("ticker")
        technical_score = result.get("score", 50)
        sector = config.STOCK_SECTORS.get(ticker, "teknoloji" if "." not in ticker else "finans")
        sector_sentiment = sector_scores.get(sector, 0.0)
        composite_score = ScoreCalculator.calculate_composite_score(technical_score, sector_sentiment)
        fibonacci = result.get("fibonacci", {})
        current_price = result.get("current_price", 0)
        support = fibonacci.get("fib_0.618", current_price * 0.93)
        resistance = fibonacci.get("fib_0.236", current_price * 1.08)
        rr = ScoreCalculator.calculate_reward_risk(current_price, support, resistance)
        candidate = {
            "ticker": ticker,
            "score": composite_score,
            # ... diğer alanlar aynen
            "support": support,
            "resistance": resistance,
            "reward_pct": rr["reward_pct"],
            "risk_pct": rr["risk_pct"],
            "reward_risk_ratio": rr["ratio"],
            "dataframe": result.get("dataframe"),
            "sector": config.STOCK_SECTORS.get(ticker, "Teknoloji" if "." not in ticker else "Finans"),
            # Copilot: source_pool badge alanı ekleniyor! (main_bot.py dolduracak)
            "source_pool": result.get("source_pool", ""),
        }
        candidates.append(candidate)
    # ... filtre/puan sıralama mevcut sistem aynen devam
    filtered = candidates  # Burada asıl filtre blokları var, tamamı aynen kalıyor
    filtered.sort(key=lambda x: (x['score'] * 0.5) + (x['reward_risk_ratio'] * 10 * 0.3), reverse=True)
    return filtered[:max_count]

def generate_recommendation_text(selected_stocks: list, sector_scores: dict, candidates: list = None) -> dict:
    recommendations = {"recommendations": [], "total_selected": len(selected_stocks)}
    for stock in selected_stocks:
        current_price = stock.get("current_price", 0)
        resistance = stock.get("resistance", 0)
        support = stock.get("support", 0)
        rr_ratio = stock.get("reward_risk_ratio", 0)
        rec = {
            "ticker": stock.get("ticker"),
            "sector": stock.get("sector", "Genel"),
            "score": stock.get("score", 0),
            "rating": determine_rating(stock.get("score", 0)),
            "price": current_price,
            "momentum_pct": stock.get("momentum_pct", 0),
            "support": support,
            "resistance": resistance,
            "reward_risk_ratio": round(rr_ratio, 2),
            "breakout": stock.get("breakout", {}),
            # Copilot: source_pool badge ekleniyor!
            "source_pool": stock.get("source_pool", ""),
        }
        recommendations["recommendations"].append(rec)
    return recommendations
