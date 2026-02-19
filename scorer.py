# ============================================================
# scorer.py — Skor Hesaplama ve Seçim (v4 - KOMPLE FINAL)
# ============================================================
# İşlevler:
# 1. Teknik + Haber skorları birleştir
# 2. En iyi hisseleri seç
# 3. Fallback mekanizması (hiç hisse seçilmemişse)
# 4. Öneriler üret
# ============================================================

import config


class ScoreCalculator:
    """Skor hesaplama"""
    
    @staticmethod
    def calculate_composite_score(technical_score: float, sector_sentiment: float) -> float:
        """Teknik + Haber skoru birleştir"""
        try:
            if technical_score is None:
                technical_score = 50.0
            
            if sector_sentiment is None or abs(sector_sentiment) < 0.01:
                sector_sentiment = 0.0
            
            # Haber skorunu 0-100 aralığına çevir
            news_score = 50 + (sector_sentiment * 50)
            news_score = max(0, min(100, news_score))
            
            # Ağırlıklandırılmış ortalama
            # Teknik %60, Haber %40
            composite = (technical_score * 0.6) + (news_score * 0.4)
            
            # Sınırla ve round
            composite = max(0, min(100, composite))
            
            return round(composite, 1)
        
        except Exception as e:
            return 50.0
    
    @staticmethod
    def calculate_confidence(score: float, rsi: float, macd_histogram: float) -> str:
        """Güven seviyesi belirle"""
        
        try:
            confidence_base = "Orta"
            
            if score > 80:
                confidence_base = "Çok Yüksek"
            elif score > 70:
                confidence_base = "Yüksek"
            elif score > 60:
                confidence_base = "İyi"
            elif score > 50:
                confidence_base = "Orta"
            elif score > 40:
                confidence_base = "Düşük"
            else:
                confidence_base = "Çok Düşük"
            
            return confidence_base
        
        except Exception as e:
            return "Bilinmiyor"
    
    @staticmethod
    def calculate_reward_risk(current_price: float, support: float, resistance: float) -> dict:
        """Reward/Risk oranı hesapla"""
        try:
            if not current_price or not support or not resistance:
                return {"reward_pct": 0, "risk_pct": 0, "ratio": 0}
            
            if current_price == 0:
                return {"reward_pct": 0, "risk_pct": 0, "ratio": 0}
            
            reward = ((resistance - current_price) / current_price) * 100
            risk = ((current_price - support) / current_price) * 100
            
            ratio = reward / risk if risk > 0 else 0
            
            return {
                "reward_pct": round(reward, 2),
                "risk_pct": round(risk, 2),
                "ratio": round(ratio, 2)
            }
        
        except Exception as e:
            return {"reward_pct": 0, "risk_pct": 0, "ratio": 0}


def select_top_stocks(technical_results: list, sector_scores: dict, max_count: int = 5) -> list:
    """En iyi hisseleri seç (FALLBACK İLE)"""
    
    try:
        candidates = []
        
        for result in technical_results:
            # Başarısız analizleri atla
            if result.get("skip"):
                continue
            
            ticker = result.get("ticker")
            technical_score = result.get("score", 50)
            
            # Haber skoru (sektörüne göre)
            sector_sentiment = 0.0
            if "." in ticker:
                # Türkçe hisse (BIST)
                sector_sentiment = sector_scores.get("finans", 0.0)
            else:
                # Global hisse
                sector_sentiment = sector_scores.get("teknoloji", 0.0)
            
            # Composite skor
            composite_score = ScoreCalculator.calculate_composite_score(
                technical_score, 
                sector_sentiment
            )
            
            # Fibonacci seviyeleri
            fibonacci = result.get("fibonacci", {})
            current_price = result.get("current_price", 0)
            
            # Support/Resistance
            if fibonacci:
                support = fibonacci.get("fib_0.618", current_price * 0.95)
                resistance = fibonacci.get("fib_0.236", current_price * 1.05)
            else:
                support = current_price * 0.95 if current_price > 0 else 0
                resistance = current_price * 1.05 if current_price > 0 else 0
            
            # Reward/Risk
            rr = ScoreCalculator.calculate_reward_risk(
                current_price,
                support,
                resistance
            )
            
            candidate = {
                "ticker": ticker,
                "score": composite_score,
                "technical_score": technical_score,
                "sector_sentiment": sector_sentiment,
                "current_price": current_price,
                "rsi": result.get("rsi"),
                "macd_histogram": result.get("macd_histogram"),
                "bollinger_position": result.get("bollinger_position"),
                "sma_short": result.get("sma_short"),
                "sma_long": result.get("sma_long"),
                "momentum_pct": result.get("momentum_pct"),
                "trend": result.get("trend", "Bilinmiyor"),
                "signals": result.get("signals", []),
                "fibonacci": fibonacci,
                "support": support,
                "resistance": resistance,
                "reward_pct": rr.get("reward_pct", 0),
                "risk_pct": rr.get("risk_pct", 0),
                "reward_risk_ratio": rr.get("ratio", 0),
                "confidence": ScoreCalculator.calculate_confidence(
                    composite_score,
                    result.get("rsi"),
                    result.get("macd_histogram")
                ),
                "dataframe": result.get("dataframe"),
                "sector": "Teknoloji" if not "." in ticker else "Finans"
            }
            
            candidates.append(candidate)
            print(f"   📊 {ticker:10s} Skor: {composite_score:6.1f}")
        
        if not candidates:
            print(f"\n⚠️  Hiçbir hisse analiz edilmedi")
            return []
        
        # Skor'a göre sırala
        candidates.sort(key=lambda x: x["score"], reverse=True)
        
        # EN İYİ N TANESINI SEÇ
        selected = candidates[:max_count]
        
        if selected:
            print(f"\n✅ {len(selected)} hisse seçildi:")
            for i, stock in enumerate(selected, 1):
                print(f"   {i}. {stock['ticker']:10s} - Skor: {stock['score']:6.1f}")
        else:
            print(f"\n⚠️  Hiçbir hisse seçilmedi")
            # FALLBACK: EN İYİ OLANINI SÇ
            if candidates:
                selected = [candidates[0]]
                print(f"\n   Fallback seçim: {candidates[0]['ticker']} seçildi (Skor: {candidates[0]['score']})")
        
        return selected
    
    except Exception as e:
        print(f"❌ Hisse seçim hatası: {e}")
        return []


def generate_recommendation_text(selected_stocks: list, sector_scores: dict) -> dict:
    """Hisse önerileri metin oluştur"""
    
    try:
        recommendations = {
            "recommendations": [],
            "total_selected": len(selected_stocks)
        }
        
        for stock in selected_stocks:
            try:
                rec = {
                    "ticker": stock.get("ticker"),
                    "sector": stock.get("sector", "Genel"),
                    "score": stock.get("score", 0),
                    "rating": determine_rating(stock.get("score", 0)),
                    "price": stock.get("current_price", 0),
                    "rsi": stock.get("rsi"),
                    "macd_histogram": stock.get("macd_histogram"),
                    "bollinger_position": stock.get("bollinger_position"),
                    "sma_short": stock.get("sma_short"),
                    "sma_long": stock.get("sma_long"),
                    "momentum_pct": stock.get("momentum_pct", 0),
                    "trend": stock.get("trend", "Bilinmiyor"),
                    "support": stock.get("support", 0),
                    "resistance": stock.get("resistance", 0),
                    "reward_pct": stock.get("reward_pct", 0),
                    "risk_pct": stock.get("risk_pct", 0),
                    "confidence": stock.get("confidence", "Orta"),
                    "signals": stock.get("signals", [])
                }
                
                recommendations["recommendations"].append(rec)
            
            except Exception as e:
                continue
        
        return recommendations
    
    except Exception as e:
        print(f"⚠️  Öneri oluşturma hatası: {e}")
        return {"recommendations": [], "total_selected": 0}


def determine_rating(score: float) -> str:
    """Puan'a göre rating belirle"""
    
    try:
        if score >= 80:
            return "🟢🟢🟢 KAUFEN (Alım)"
        elif score >= 70:
            return "🟢🟢 ÜBERGEWICHT (Yükseltme)"
        elif score >= 60:
            return "🟡 HALTEN (Bekle)"
        elif score >= 40:
            return "🟠 UNTERGEWICHT (Düşürme)"
        else:
            return "🔴 VERKAUFEN (Satış)"
    
    except Exception as e:
        return "❓ Bilinmiyor"


def get_sector_recommendation(sector_scores: dict) -> dict:
    """Sektör önerileri"""
    
    try:
        recommendations = {}
        
        for sector, score in sector_scores.items():
            if sector == "genel":
                continue
            
            if score > 0.3:
                recommendation = "📈 BUY"
            elif score < -0.3:
                recommendation = "📉 SELL"
            else:
                recommendation = "➡️ HOLD"
            
            recommendations[sector] = {
                "score": round(score, 3),
                "recommendation": recommendation
            }
        
        return recommendations
    
    except Exception as e:
        return {}


if __name__ == "__main__":
    print("✅ scorer.py yüklendi başarıyla")
