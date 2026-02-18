# ============================================================
# scorer.py — Master Scoring Engine (COMPLETE)
# ============================================================
# Bu modül:
# 1) Haber sentiment'i → Sektörsel skora çevirir
# 2) Teknik analizdeki her hisse skoru alır
# 3) İkisini birleştirip NIHAI skor hesaplar
# 4) En iyi 1-3 hisseyi seçer
# 5) Risk/reward analizi yapar
# ============================================================

import config
from collections import defaultdict


# ═══════════════════════════════════════════════════════════
# HISSE → SEKTÖR EŞLEŞTİRMESİ (BIST 100 + GLOBAL TOP 50)
# ═══════════════════════════════════════════════════════════

TICKER_TO_SECTOR = {
    # BIST 100 - Bankalar (11)
    "AKBANK.IS": "finans",
    "GARAN.IS": "finans",
    "ISA.IS": "finans",
    "YBANK.IS": "finans",
    "TEBNK.IS": "finans",
    "HALKB.IS": "finans",
    "PBANK.IS": "finans",
    "KLVT.IS": "finans",
    "FICOH.IS": "finans",
    "BNTAS.IS": "finans",
    "YKBNK.IS": "finans",
    
    # BIST 100 - Sigorta (3)
    "DOAS.IS": "sigortalar",
    "ACSEL.IS": "sigortalar",
    "ANELE.IS": "sigortalar",
    
    # BIST 100 - Gayrimenkul (17)
    "OZKGY.IS": "inşaat_gayrimenkul",
    "EKGYO.IS": "inşaat_gayrimenkul",
    "BLDYR.IS": "inşaat_gayrimenkul",
    "ORMA.IS": "inşaat_gayrimenkul",
    "TOASY.IS": "inşaat_gayrimenkul",
    "YAPI.IS": "inşaat_gayrimenkul",
    "RSGYO.IS": "inşaat_gayrimenkul",
    "YAPRK.IS": "inşaat_gayrimenkul",
    "INSGYO.IS": "inşaat_gayrimenkul",
    "ARSAN.IS": "inşaat_gayrimenkul",
    "ARYAP.IS": "inşaat_gayrimenkul",
    "KRGYO.IS": "inşaat_gayrimenkul",
    "SRVGY.IS": "inşaat_gayrimenkul",
    "TKFEN.IS": "inşaat_gayrimenkul",
    "DYHOL.IS": "finans",
    "ALBRK.IS": "finans",
    "TLMAN.IS": "finans",
    
    # BIST 100 - Telekom (4)
    "TCELL.IS": "telekom",
    "TTKOM.IS": "telekom",
    "TAVHL.IS": "telekom",
    "TRWF.IS": "telekom",
    
    # BIST 100 - Enerji (13)
    "AKSA.IS": "enerji",
    "TUPAS.IS": "enerji",
    "ENKA.IS": "enerji",
    "KRDMD.IS": "enerji",
    "SODA.IS": "enerji",
    "CCHOL.IS": "enerji",
    "KPGRP.IS": "enerji",
    "EGEEN.IS": "enerji",
    "ENJSA.IS": "enerji",
    "GEMIN.IS": "enerji",
    "AYGAZ.IS": "enerji",
    "PETKE.IS": "enerji",
    "IPEKE.IS": "enerji",
    
    # BIST 100 - Üretim & Sanayi (20)
    "ASELS.IS": "savunma",
    "OTKAR.IS": "otomotiv",
    "FROTO.IS": "otomotiv",
    "SISE.IS": "teknoloji",
    "ARÇEL.IS": "teknoloji",
    "VESTEL.IS": "teknoloji",
    "ULUSE.IS": "tekstil",
    "KAYNK.IS": "tekstil",
    "LCDHO.IS": "tekstil",
    "GOLTS.IS": "tekstil",
    "HMROL.IS": "tekstil",
    "MRSB.IS": "tekstil",
    "HRSGL.IS": "tekstil",
    "KORDS.IS": "tekstil",
    "HEYLL.IS": "tekstil",
    "KORDSA.IS": "tekstil",
    "PETKM.IS": "kimya",
    "ARBOS.IS": "orman",
    "EGLET.IS": "orman",
    "PSTKA.IS": "kimya",
    
    # BIST 100 - Gıda & İçecek (5)
    "ULKER.IS": "gida",
    "PENGD.IS": "gida",
    "MERKO.IS": "gida",
    "MARTI.IS": "gida",
    "BANVT.IS": "gida",
    
    # BIST 100 - Perakende & Turizm (7)
    "CARSI.IS": "perakende",
    "KOTON.IS": "perakende",
    "HATEK.IS": "gida",
    "TRST.IS": "turizm",
    "BJKAS.IS": "turizm",
    "NTHOL.IS": "turizm",
    "NTTUR.IS": "turizm",
    "KSTUR.IS": "turizm",
    "ASMK.IS": "perakende",
    "KNC.IS": "perakende",
    
    # BIST 100 - Medya
    "ARENA.IS": "medya",
    
    # Global - Teknoloji (9)
    "AAPL": "teknoloji",
    "MSFT": "teknoloji",
    "GOOGL": "teknoloji",
    "GOOG": "teknoloji",
    "AMZN": "teknoloji",
    "META": "teknoloji",
    "NVDA": "teknoloji",
    "NFLX": "teknoloji",
    "ADBE": "teknoloji",
    
    # Global - Otomotiv
    "TSLA": "otomotiv",
    
    # Global - Finans (10)
    "JPM": "finans",
    "BAC": "finans",
    "WFC": "finans",
    "MS": "finans",
    "GS": "finans",
    "V": "finans",
    "MA": "finans",
    "AXP": "finans",
    "BLK": "finans",
    "SCHW": "finans",
    
    # Global - Enerji (5)
    "XOM": "enerji",
    "CVX": "enerji",
    "COP": "enerji",
    "MPC": "enerji",
    "PSX": "enerji",
    
    # Global - Sağlık (8)
    "UNH": "sağlık",
    "JNJ": "sağlık",
    "PFE": "sağlık",
    "ABBV": "sağlık",
    "MRK": "sağlık",
    "LLY": "sağlık",
    "TMO": "sağlık",
    "AMGN": "sağlık",
    
    # Global - Tüketim & Perakende (7)
    "WMT": "perakende",
    "KO": "gida",
    "PEP": "gida",
    "MCD": "gida",
    "NKE": "teknoloji",
    "COST": "perakende",
    "HD": "perakende",
}


def map_sector_score_to_stock(ticker: str, sector_scores: dict) -> float:
    """
    Bir hissenin sektörünün haber sentiment skoru nedir?
    Döndürür: -1.0 ile +1.0 arası float
    """
    sector = TICKER_TO_SECTOR.get(ticker, "genel")
    score = sector_scores.get(sector, sector_scores.get("genel", 0.0))
    return float(score)


def calculate_final_score(ticker: str, technical_score: float,
                          sector_scores: dict) -> dict:
    """
    Nihai skor hesaplar.

    Formül:
    final = (teknik * 0.40) + (sektör_haber * 0.20) + (temel * 0.30) + (momentum * 0.10)

    Ağırlıklar config.py'den alınır.
    """
    try:
        # Teknik skor: 0-100 → 0-1 normalize
        tech_normalized = technical_score / 100.0

        # Sektörel haber skoru: -1 ile +1 → 0 ile 1 normalize
        sector_score = map_sector_score_to_stock(ticker, sector_scores)
        sector_normalized = (float(sector_score) + 1.0) / 2.0  # -1,+1 → 0,1

        # Momentum factor: Teknik skor içinde zaten yansıtıldı
        momentum_factor = 0.5  # Default neutral

        # Ağırlıklı skor hesapla
        # Temel analiz proxy olarak teknik skor kullanılıyor (API sınırlaması nedeniyle)
        total_weight = config.WEIGHT_TECHNICAL + config.WEIGHT_FUNDAMENTAL + \
                      config.WEIGHT_NEWS_SENTIMENT + config.WEIGHT_MOMENTUM

        final_raw = (
            (tech_normalized * config.WEIGHT_TECHNICAL) +
            (sector_normalized * config.WEIGHT_NEWS_SENTIMENT) +
            (tech_normalized * config.WEIGHT_FUNDAMENTAL) +  # Proxy
            (momentum_factor * config.WEIGHT_MOMENTUM)
        ) / total_weight

        # 0-100 arası normalize
        final_score = final_raw * 100.0
        final_score = max(0, min(100, final_score))

        # Rating ve confidence belirle
        if final_score >= 70:
            rating = "🔥 GÜÇLÜ AL"
            confidence = "Yüksek"
        elif final_score >= 58:
            rating = "�� AL"
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


def select_top_stocks(all_analysis: list, sector_scores: dict,
                      max_count: int = 3) -> list:
    """
    Tüm hisseleri skor alarak en iyi 1-3'ünü seçer.

    Seçim kriterleri:
    1) Nihai skor en yüksek olanlar
    2) Minimum skor threshold'u: 50 (altında olan hiçbiri seçilmez)
    3) Sektör çeşitlendirmesi: Aynı sektörden max 1 hisse
    4) Rating'i "AL" veya yukarısı olmalı
    """
    try:
        # Her hisse için nihai skor hesapla
        scored = []
        
        for stock in all_analysis:
            ticker = stock.get("ticker", "")
            tech_score = stock.get("score", 0)

            if tech_score == 0 or tech_score is None:
                continue

            final = calculate_final_score(ticker, tech_score, sector_scores)
            stock.update(final)
            scored.append(stock)

        # Final score'a göre sort (yüksek → düşük)
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

            # Rating kontrolü (sadece AL veya yukarısı)
            rating = stock.get("rating", "")
            if "AL" not in rating and "🔥" not in rating:
                continue

            # Sektör çeşitlendirmesi
            sector = stock.get("sector", "genel")
            if sector in used_sectors:
                continue  # Bu sektörden zaten seçtik

            selected.append(stock)
            used_sectors.add(sector)

        # Hiçbiri seçilmediyse en yüksek scored'u al (threshold düşür)
        if not selected and scored:
            best = scored[0]
            if best.get("final_score", 0) >= 40:
                selected.append(best)

        return selected

    except Exception as e:
        print(f"[ERROR] Hisse seçimi hatası: {e}")
        return []


def generate_recommendation_text(selected: list, sector_scores: dict,
                                  news_summary: list = None) -> dict:
    """
    Son kullanıcı için okunabilir önerileri oluşturur.
    Email'e gönderilecek recommendation'ları hazırlar.
    """
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

            # Fibonacci destek/direnç
            current = fib.get("current", price)
            support = fib.get("fib_0.382", 0)
            resistance = fib.get("fib_0.618", 0)

            # Risk/Reward hesapla
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
                "signals": signals[:5],  # Max 5 sinyal
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
            "analysis_date": None
        }

    except Exception as e:
        print(f"[ERROR] Recommendation oluşturma hatası: {e}")
        return {
            "recommendations": [],
            "total_selected": 0,
            "market_mood": "⚪ Belirsiz",
            "analysis_date": None
        }


def determine_market_mood(sector_scores: dict) -> str:
    """Genel piyasa duygu analizi."""
    try:
        if not sector_scores:
            return "⚪ Belirsiz"

        avg_all = sum(sector_scores.values()) / len(sector_scores)
        avg_all = float(avg_all)

        if avg_all >= 0.3:
            return "🟢 Çok Olumlu - Piyasalar yukarı baskı altında"
        elif avg_all >= 0.1:
            return "🟢 Olumlu - Genel pozitif sinyaller var"
        elif avg_all >= -0.1:
            return "🟡 Karışık - Piyasa yönü belirsiz"
        elif avg_all >= -0.3:
            return "🔴 Olumsuz - Dikkatli olun"
        else:
            return "🔴 Çok Olumsuz - Yüksek risk dönem"

    except Exception as e:
        print(f"[ERROR] Market mood belirleme hatası: {e}")
        return "⚪ Belirsiz"
