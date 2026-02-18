# ============================================================
# scorer.py — Master Scoring Engine (v3 - FINAL)
# ============================================================

import config
from collections import defaultdict


# Hisse → Sektör Eşleştirmesi
TICKER_TO_SECTOR = {
    # Bankalar
    "AKBANK.IS": "finans", "GARAN.IS": "finans", "ISA.IS": "finans",
    "YBANK.IS": "finans", "TEBNK.IS": "finans", "HALKB.IS": "finans",
    "PBANK.IS": "finans",
    
    # Sigorta
    "DOAS.IS": "sigortalar", "ACSEL.IS": "sigortalar",
    
    # Telekom
    "TCELL.IS": "telekom", "TTKOM.IS": "telekom",
    
    # Enerji
    "AKSA.IS": "enerji", "TUPAS.IS": "enerji", "ENKA.IS": "enerji",
    "SODA.IS": "enerji", "CCHOL.IS": "enerji", "KRDMD.IS": "enerji",
    "AYGAZ.IS": "enerji", "PETKE.IS": "enerji",
    
    # Gayrimenkul
    "EKGYO.IS": "inşaat_gayrimenkul", "BLDYR.IS": "inşaat_gayrimenkul",
    "ORMA.IS": "inşaat_gayrimenkul", "TOASY.IS": "inşaat_gayrimenkul",
    "YAPI.IS": "inşaat_gayrimenkul", "RSGYO.IS": "inşaat_gayrimenkul",
    "TKFEN.IS": "inşaat_gayrimenkul", "ARSAN.IS": "inşaat_gayrimenkul",
    
    # Üretim
    "ASELS.IS": "savunma", "OTKAR.IS": "otomotiv", "FROTO.IS": "otomotiv",
    "SISE.IS": "teknoloji", "ARÇEL.IS": "teknoloji", "VESTEL.IS": "teknoloji",
    "ULUSE.IS": "tekstil", "KAYNK.IS": "tekstil", "LCDHO.IS": "tekstil",
    "GOLTS.IS": "tekstil", "HMROL.IS": "tekstil", "MRSB.IS": "tekstil",
    "KORDSA.IS": "tekstil", "HATEK.IS": "gida", "PETKM.IS": "kimya",
    
    # Gıda
    "ULKER.IS": "gida", "PENGD.IS": "gida", "MERKO.IS": "gida",
    
    # Turizm
    "TRST.IS": "turizm", "KOTON.IS": "perakende", "NTHOL.IS": "turizm",
    
    # Perakende
    "CARSI.IS": "perakende", "ASMK.IS": "perakende",
    
    # Diğer
    "DYHOL.IS": "finans", "TLMAN.IS": "finans",
    
    # Global - Teknoloji
    "AAPL": "teknoloji", "MSFT": "teknoloji", "GOOGL": "teknoloji",
    "AMZN": "teknoloji", "META": "teknoloji", "NVDA": "teknoloji",
    "TSLA": "otomotiv", "NFLX": "teknoloji", "CRM": "teknoloji",
    "ADBE": "teknoloji", "AVGO": "teknoloji", "QCOM": "teknoloji",
    
    # Global - Finans
    "JPM": "finans", "BAC": "finans", "WFC": "finans", "MS": "finans",
    "GS": "finans", "V": "finans", "MA": "finans", "AXP": "finans",
    "BLK": "finans", "SCHW": "finans",
    
    # Global - Enerji
    "XOM": "enerji", "CVX": "enerji", "COP": "enerji",
    "MPC": "enerji", "PSX": "enerji",
    
    # Global - Sağlık
    "UNH": "sağlık", "JNJ": "sağlık", "PFE": "sağlık",
    "ABBV": "sağlık", "MRK": "sağlık", "LLY": "sağlık",
    "TMO": "sağlık", "AMGN": "sağlık",
    
    # Global - Tüketim
    "WMT": "perakende", "KO": "gida", "PEP": "gida",
    "MCD": "gida", "NKE": "teknoloji", "COST": "perakende",
    "HD": "perakende", "LOW": "perakende",
}


def map_sector_score_to_stock(ticker: str, sector_scores: dict) -> float:
    """Bir hissenin sektörünün haber sentiment skoru nedir?"""
    sector = TICKER_TO_SECTOR.get(ticker, "genel")
    score = sector_scores.get(sector, sector_scores.get("genel", 0.0))
    return float(score)


def calculate_final_score(ticker: str, technical_score: float, sector_scores: dict) -> dict:
    """Nihai skor hesapla"""
    try:
        # Teknik skor normalize
        tech_normalized = technical_score / 100.0

        # Sektörel haber skoru normalize
        sector_score = map_sector_score_to_stock(ticker, sector_scores)
        sector_normalized = (float(sector_score) + 1.0) / 2.0  # -1,+1 → 0,1

        # Momentum factor
        momentum_factor = 0.5

        # Ağırlıklı skor
        total_weight = config.WEIGHT_TECHNICAL + config.WEIGHT_FUNDAMENTAL + \
                      config.WEIGHT_NEWS_SENTIMENT + config.WEIGHT_MOMENTUM

        final_raw = (
            (tech_normalized * config.WEIGHT_TECHNICAL) +
            (sector_normalized * config.WEIGHT_NEWS_SENTIMENT) +
            (tech_normalized * config.WEIGHT_FUNDAMENTAL) +
            (momentum_factor * config.WEIGHT_MOMENTUM)
        ) / total_weight

        # 0-100 arası normalize
        final_score = final_raw * 100.0
        final_score = max(0, min(100, final_score))

        # Rating ve confidence
        if final_score >= 70:
            rating = "🔥 GÜÇLÜ AL"
            confidence = "Yüksek"
        elif final_score >= 58:
            rating = "📈 AL"
            confidence = "Orta-Yüksek"
        elif final_score >= 48:
            rating = "⚖️ İZLE"
            confidence = "Orta"
        elif final_score >= 38:
            rating = "📉 KAVI"
            confidence = "Orta-Düşük"
        else:
            rating = "🚫 SAT"
            confidence = "Düşük"

        return {
            "final_score": round(final_score, 1),
            "technical_score": round(technical_score, 1),
            "sector_score": round(float(sector_score), 3),
            "rating": rating,
            "confidence": confidence,
            "sector": TICKER_TO_SECTOR.get(ticker, "genel")
        }

    except Exception as e:
        print(f"[ERROR] Skor hesaplama hatası ({ticker}): {e}")
        return {
            "final_score": 0,
            "technical_score": technical_score,
            "sector_score": 0,
            "rating": "❓ Bilinmiyor",
            "confidence": "Düşük",
            "sector": "genel"
        }


def select_top_stocks(all_analysis: list, sector_scores: dict, max_count: int = 3) -> list:
    """En iyi 1-3 hisseyi seç"""
    try:
        scored = []
        
        for stock in all_analysis:
            ticker = stock.get("ticker", "")
            tech_score = stock.get("score", 0)

            if tech_score == 0 or tech_score is None or stock.get("skip"):
                continue

            final = calculate_final_score(ticker, tech_score, sector_scores)
            stock.update(final)
            scored.append(stock)

        # Sort by score
        scored.sort(key=lambda x: x.get("final_score", 0), reverse=True)

        # Sektör çeşitlendirmesi ile seç
        selected = []
        used_sectors = set()

        for stock in scored:
            if len(selected) >= max_count:
                break

            # Minimum threshold
            if stock.get("final_score", 0) < 50:
                continue

            # Rating kontrolü
            rating = stock.get("rating", "")
            if "AL" not in rating and "🔥" not in rating:
                continue

            # Sektör çeşitlendirmesi
            sector = stock.get("sector", "genel")
            if sector in used_sectors:
                continue

            selected.append(stock)
            used_sectors.add(sector)

        # Hiçbiri seçilmediyse best'i al
        if not selected and scored:
            best = scored[0]
            if best.get("final_score", 0) >= 40:
                selected.append(best)

        return selected

    except Exception as e:
        print(f"[ERROR] Hisse seçimi hatası: {e}")
        return []


def generate_recommendation_text(selected: list, sector_scores: dict) -> dict:
    """Son kullanıcı için önerileri oluştur"""
    try:
        recommendations = []

        for i, stock in enumerate(selected, 1):
            ticker = stock.get("ticker", "")
            price = stock.get("current_price", 0)
            score = stock.get("final_score", 0)
            rating = stock.get("rating", "")
            sector = stock.get("sector", "genel")
            signals = stock.get("signals", [])
            fib = stock.get("fibonacci", {})
            confidence = stock.get("confidence", "Bilinmiyor")
            
            # Teknik göstergeler
            rsi = stock.get("rsi", "N/A")
            macd = stock.get("macd_histogram", "N/A")
            bollinger = stock.get("bollinger_position", "N/A")
            sma_short = stock.get("sma_short", "N/A")
            sma_long = stock.get("sma_long", "N/A")
            momentum = stock.get("momentum_pct", "N/A")

            # Fibonacci
            current = fib.get("current", price)
            support = fib.get("fib_0.382", 0)
            resistance = fib.get("fib_0.618", 0)

            # Risk/Reward
            if support > 0 and resistance > 0 and current > 0:
                try:
                    risk = round((current - support) / current * 100, 1)
                    reward = round((resistance - current) / current * 100, 1)
                    rr_ratio = round(reward / risk, 2) if risk > 0 else 0
                except:
                    risk = reward = rr_ratio = 0
            else:
                risk = reward = rr_ratio = 0

            rec = {
                "rank": i,
                "ticker": ticker,
                "sector": sector,
                "price": price,
                "score": score,
                "rating": rating,
                "confidence": confidence,
                "signals": signals[:5],
                "support": support,
                "resistance": resistance,
                "risk_pct": risk,
                "reward_pct": reward,
                "risk_reward_ratio": rr_ratio,
                "rsi": rsi,
                "macd_histogram": macd,
                "bollinger_position": bollinger,
                "sma_short": sma_short,
                "sma_long": sma_long,
                "momentum_pct": momentum,
                "fibonacci": fib,
            }

            recommendations.append(rec)

        return {
            "recommendations": recommendations,
            "total_selected": len(selected),
            "market_mood": determine_market_mood(sector_scores),
            "sector_scores": sector_scores
        }

    except Exception as e:
        print(f"[ERROR] Recommendation oluşturma hatası: {e}")
        return {
            "recommendations": [],
            "total_selected": 0,
            "market_mood": "⚪ Belirsiz",
            "sector_scores": sector_scores
        }


def determine_market_mood(sector_scores: dict) -> str:
    """Genel piyasa duygu analizi"""
    try:
        if not sector_scores:
            return "⚪ Belirsiz"

        avg_all = sum(sector_scores.values()) / len(sector_scores)
        avg_all = float(avg_all)

        if avg_all >= 0.3:
            return "🟢 ÇOK OLUMLU"
        elif avg_all >= 0.1:
            return "🟢 OLUMLU"
        elif avg_all >= -0.1:
            return "🟡 KARIŞIK"
        elif avg_all >= -0.3:
            return "🔴 OLUMSUZ"
        else:
            return "🔴 ÇOK OLUMSUZ"

    except Exception as e:
        print(f"[ERROR] Market mood belirleme hatası: {e}")
        return "⚪ Belirsiz"
