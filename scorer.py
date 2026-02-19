# ============================================================
# scorer.py — Skor & Seçim (v5 - KOMPLE FINAL)
# ============================================================

import config


class ScoreCalculator:
    """Skor Hesaplama"""
    
    @staticmethod
    def calculate_composite_score(technical_score: float, sector_sentiment: float) -> float:
        """Teknik + Haber Skoru"""
        try:
            if technical_score is None:
                technical_score = 50.0
            
            if sector_sentiment is None or abs(sector_sentiment) < 0.01:
                sector_sentiment = 0.0
            
            news_score = 50 + (sector_sentiment * 50)
            news_score = max(0, min(100, news_score))
            
            composite = (technical_score * 0.6) + (news_score * 0.4)
            
            return round(max(0, min(100, composite)), 1)
        
        except:
            return 50.0
    
    @staticmethod
    def calculate_confidence(score: float) -> str:
        """Güven Seviyesi"""
        if score > 80:
            return "Çok Yüksek"
        elif score > 70:
            return "Yüksek"
        elif score > 60:
            return "İyi"
        elif score > 50:
            return "Orta"
        elif score > 40:
            return "Düşük"
        else:
            return "Çok Düşük"
    
    @staticmethod
    def calculate_reward_risk(current_price: float, support: float, resistance: float) -> dict:
        """Reward/Risk"""
        try:
            if not current_price or current_price == 0:
                return {"reward_pct": 0, "risk_pct": 0, "ratio": 0}
            
            reward = ((resistance - current_price) / current_price) * 100
            risk = ((current_price - support) / current_price) * 100
            
            ratio = reward / risk if risk > 0 else 0
            
            return {
                "reward_pct": round(reward, 2),
                "risk_pct": round(risk, 2),
                "ratio": round(ratio, 2)
            }
        
        except:
            return {"reward_pct": 0, "risk_pct": 0, "ratio": 0}


def select_top_stocks(technical_results: list, sector_scores: dict, max_count: int = 5) -> list:
    """En İyi Hisseleri Seç"""
    
    try:
        candidates = []
        
        for result in technical_results:
            if result.get("skip"):
                continue
            
            ticker = result.get("ticker")
            technical_score = result.get("score", 50)
            
            # Haber skoru
            sector = config.STOCK_SECTORS.get(ticker, "teknoloji" if "." not in ticker else "finans")
            sector_sentiment = sector_scores.get(sector, 0.0)
            
            # Composite skor
            composite_score = ScoreCalculator.calculate_composite_score(technical_score, sector_sentiment)
            
            # Support/Resistance (Fibonacci'den)
            fibonacci = result.get("fibonacci", {})
            current_price = result.get("current_price", 0)
            
            support = fibonacci.get("fib_0.618", current_price * 0.95)
            resistance = fibonacci.get("fib_0.236", current_price * 1.05)
            
            rr = ScoreCalculator.calculate_reward_risk(current_price, support, resistance)
            
            candidate = {
                "ticker": ticker,
                "score": composite_score,
                "technical_score": technical_score,
                "sector_sentiment": sector_sentiment,
                "current_price": current_price,
                "rsi": result.get("rsi"),
                "macd_histogram": result.get("macd_histogram"),
                "macd_line": result.get("macd_line"),
                "signal_line": result.get("signal_line"),
                "bollinger_position": result.get("bollinger_position"),
                "bollinger_upper": result.get("bollinger_upper"),
                "bollinger_middle": result.get("bollinger_middle"),
                "bollinger_lower": result.get("bollinger_lower"),
                "sma_short": result.get("sma_short"),
                "sma_long": result.get("sma_long"),
                "momentum_pct": result.get("momentum_pct"),
                "atr": result.get("atr"),
                "trend": result.get("trend", "Nötr"),
                "trend_strength": result.get("trend_strength"),
                "signals": result.get("signals", []),
                "fibonacci": fibonacci,
                "support": support,
                "resistance": resistance,
                "reward_pct": rr["reward_pct"],
                "risk_pct": rr["risk_pct"],
                "confidence": ScoreCalculator.calculate_confidence(composite_score),
                "dataframe": result.get("dataframe"),
                "sector": config.STOCK_SECTORS.get(ticker, "Teknoloji" if "." not in ticker else "Finans")
            }
            
            candidates.append(candidate)
        
        if not candidates:
            return []
        
        candidates.sort(key=lambda x: x["score"], reverse=True)
        selected = candidates[:max_count]
        
        print(f"✅ {len(selected)} hisse seçildi:")
        for i, stock in enumerate(selected, 1):
            print(f"   {i}. {stock['ticker']:10s} - Skor: {stock['score']:6.1f}")
        
        return selected
    
    except Exception as e:
        print(f"❌ Seçim hatası: {e}")
        return []


def generate_recommendation_text(selected_stocks: list, sector_scores: dict) -> dict:
    """Öneriler Oluştur"""
    
    try:
        recommendations = {"recommendations": [], "total_selected": len(selected_stocks)}
        
        for stock in selected_stocks:
            rec = {
                "ticker": stock.get("ticker"),
                "sector": stock.get("sector", "Genel"),
                "score": stock.get("score", 0),
                "rating": determine_rating(stock.get("score", 0)),
                "price": stock.get("current_price", 0),
                "rsi": stock.get("rsi"),
                "macd_histogram": stock.get("macd_histogram"),
                "macd_line": stock.get("macd_line"),
                "signal_line": stock.get("signal_line"),
                "bollinger_position": stock.get("bollinger_position"),
                "bollinger_upper": stock.get("bollinger_upper"),
                "bollinger_middle": stock.get("bollinger_middle"),
                "bollinger_lower": stock.get("bollinger_lower"),
                "sma_short": stock.get("sma_short"),
                "sma_long": stock.get("sma_long"),
                "momentum_pct": stock.get("momentum_pct", 0),
                "atr": stock.get("atr"),
                "trend": stock.get("trend", "Nötr"),
                "trend_strength": stock.get("trend_strength"),
                "support": stock.get("support", 0),
                "resistance": stock.get("resistance", 0),
                "reward_pct": stock.get("reward_pct", 0),
                "risk_pct": stock.get("risk_pct", 0),
                "confidence": stock.get("confidence", "Orta"),
                "signals": stock.get("signals", []),
                "fibonacci": stock.get("fibonacci", {})
            }
            recommendations["recommendations"].append(rec)
        
        return recommendations
    
    except:
        return {"recommendations": [], "total_selected": 0}


def determine_rating(score: float) -> str:
    """Rating Belirle"""
    if score >= 80:
        return "🔥 GÜÇLÜ AL"
    elif score >= 70:
        return "🟢 AL"
    elif score >= 60:
        return "🟡 TUT"
    elif score >= 40:
        return "🟠 AZALT"
    else:
        return "🔴 SAT"


if __name__ == "__main__":
    print("✅ scorer.py yüklendi")
