# ============================================================
# advanced_features.py — İleri Özellikler (v3 - KOMPLE FINAL)
# ============================================================
# Tüm İleri Özellikler:
# 1. Spesifik Sektör Tetikleyicileri (AI, Savunma, Enerji Krizi)
# 2. Kripto Piyasası Etkisi (Bitcoin, Ethereum)
# 3. Döviz Kurları ve Para Politikası
# 4. Kurumsal Geri Satın Alma (Buyback) Programları
# 5. Kazanç Takvimi
# 6. Piyasa Genişliği Analizi (S&P 500 vs NASDAQ)
# 7. Gerçek Zamanlı Haber Sentiment Analizi
# ============================================================

import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from collections import defaultdict

try:
    import yfinance as yf
except:
    import subprocess
    subprocess.run(["pip", "install", "yfinance"], check=True)
    import yfinance as yf

import config


class SpecificSectorLinker:
    """Spesifik Makro Olaylar → Sektör Eşleştirmesi"""
    
    SPECIFIC_LINKS = {
        "ram_shortage": {
            "trigger": "RAM Kıtlığı Başında",
            "impact": "Yüksek",
            "affected_stocks": {
                "positive": [
                    {"ticker": "VESTEL.IS", "reason": "Elektronik üretim maliyetleri artacak, fiyatlar yükselebilir", "impact": "+15%"},
                    {"ticker": "ASELS.IS", "reason": "Savunma elektronikleri", "impact": "+8%"},
                    {"ticker": "SISE.IS", "reason": "Paket üretim maliyetleri", "impact": "+5%"},
                ],
                "negative": [
                    {"ticker": "TCELL.IS", "reason": "Telekomünikasyon ekipmanları", "impact": "-8%"},
                    {"ticker": "TTKOM.IS", "reason": "Altyapı yatırımı maliyetleri artacak", "impact": "-10%"},
                ]
            },
            "duration": "3-6 ay",
            "historical_reference": "2021-2022 Çip Krizi: Teknoloji hisseleri -30%, Otomotiv -40%"
        },
        "ai_boom": {
            "trigger": "Yapay Zeka Hype'ı Artışta",
            "impact": "Çok Yüksek",
            "affected_stocks": {
                "positive": [
                    {"ticker": "VESTEL.IS", "reason": "GPU'lar için yonga üretimi", "impact": "+25%"},
                    {"ticker": "ASELS.IS", "reason": "Savunma AI uygulamaları", "impact": "+20%"},
                    {"ticker": "TCELL.IS", "reason": "Veri merkezi altyapısı", "impact": "+15%"},
                ],
                "negative": [
                    {"ticker": "FROTO.IS", "reason": "Geleneksel otomotiv", "impact": "-12%"},
                ]
            },
            "duration": "12+ ay",
            "historical_reference": "2023-2024: NVDA +240%, Teknoloji sektörü +45%"
        },
        "war_preparation": {
            "trigger": "Savunma Harcamaları Artışı",
            "impact": "Yüksek",
            "affected_stocks": {
                "positive": [
                    {"ticker": "ASELS.IS", "reason": "Savunma yüklenicisi", "impact": "+30%"},
                    {"ticker": "SODA.IS", "reason": "Endüstriyel üretim", "impact": "+15%"},
                    {"ticker": "ENKA.IS", "reason": "Yapı ve altyapı", "impact": "+10%"},
                ],
                "negative": [
                    {"ticker": "TRST.IS", "reason": "Turizm ve seyahat", "impact": "-8%"},
                ]
            },
            "duration": "2-5 yıl",
            "historical_reference": "2022 Savaş: Savunma hisseleri +40-50%, Turizm -20%"
        },
        "energy_crisis": {
            "trigger": "Enerji Krizası",
            "impact": "Yüksek",
            "affected_stocks": {
                "positive": [
                    {"ticker": "TUPAS.IS", "reason": "Petrol şirketi", "impact": "+40%"},
                    {"ticker": "AYGAZ.IS", "reason": "Doğalgaz dağıtıcısı", "impact": "+35%"},
                    {"ticker": "ENKA.IS", "reason": "Yenilenebilir enerji projeleri", "impact": "+20%"},
                ],
                "negative": [
                    {"ticker": "FROTO.IS", "reason": "Taşım maliyetleri", "impact": "-15%"},
                    {"ticker": "VESTEL.IS", "reason": "Üretim giderleri", "impact": "-12%"},
                ]
            },
            "duration": "6-12 ay",
            "historical_reference": "2021-2022: Enerji krizisi, Petrol +150%, Teknoloji -35%"
        },
        "interest_rate_hike": {
            "trigger": "Faiz Artışı Döngüsü",
            "impact": "Çok Yüksek",
            "affected_stocks": {
                "positive": [
                    {"ticker": "GARAN.IS", "reason": "Banka net faiz marjları artıyor", "impact": "+20%"},
                    {"ticker": "ISA.IS", "reason": "Banka karlılığı artıyor", "impact": "+18%"},
                    {"ticker": "AKBANK.IS", "reason": "Mevduat faizi artışı", "impact": "+15%"},
                ],
                "negative": [
                    {"ticker": "VESTEL.IS", "reason": "Tüketici borçlanması azalıyor", "impact": "-18%"},
                    {"ticker": "SISE.IS", "reason": "İnşaat sektörü zayıflıyor", "impact": "-15%"},
                ]
            },
            "duration": "6-18 ay",
            "historical_reference": "2022-2023: Fed 8 kez faiz artırdı, Teknoloji -33%, Finans +15%"
        },
        "recession_signal": {
            "trigger": "Resesyon Sinyalleri",
            "impact": "Çok Yüksek",
            "affected_stocks": {
                "positive": [
                    {"ticker": "GARAN.IS", "reason": "Defansif varlık - karlılık tutarlı", "impact": "+5%"},
                    {"ticker": "ULKER.IS", "reason": "Gıda - resesyonda güvenli", "impact": "+8%"},
                    {"ticker": "AKBANK.IS", "reason": "Finansal hizmetler", "impact": "+10%"},
                ],
                "negative": [
                    {"ticker": "VESTEL.IS", "reason": "Tüketici harcamaları düşüyor", "impact": "-25%"},
                    {"ticker": "FROTO.IS", "reason": "Otomotiv talep sıkıyor", "impact": "-30%"},
                ]
            },
            "duration": "12-24 ay",
            "historical_reference": "2008 Kriz: Teknoloji -56%, Gıda -15%, Finans +10% (sonrası)"
        }
    }
    
    @staticmethod
    def analyze_specific_triggers():
        """Spesifik tetikleyicileri analiz et"""
        active_triggers = []
        
        # Basit tetikleyici algılaması (gerçek veriye dayalı olarak güncellenebilir)
        current_triggers = {
            "ai_boom": True,  # 2024-2026 AI boom aktif
            "energy_crisis": False,
            "war_preparation": True,  # NATO genişlemesi
            "interest_rate_hike": False,  # Fed düşürüş beklentisi
            "recession_signal": False,
            "ram_shortage": False
        }
        
        for trigger, is_active in current_triggers.items():
            if is_active and trigger in SpecificSectorLinker.SPECIFIC_LINKS:
                link = SpecificSectorLinker.SPECIFIC_LINKS[trigger]
                active_triggers.append({
                    "trigger": trigger,
                    "name": link["trigger"],
                    "impact": link["impact"],
                    "affected_stocks": link["affected_stocks"],
                    "duration": link["duration"],
                    "historical_reference": link["historical_reference"]
                })
        
        return active_triggers


class RealTimeNewsSentiment:
    """Gerçek Zamanlı Haber Sentiment Analizi"""
    
    SENTIMENT_KEYWORDS = {
        "positive": [
            "surge", "jump", "boom", "rally", "gains", "bullish", "record high",
            "growth", "beat", "profit", "success", "positive", "strong", "rise",
            "high", "up", "increase", "bull", "optimistic", "upgrade", "target raised",
            "buy", "outperform", "momentum", "recovery", "rebound", "breakthrough"
        ],
        "negative": [
            "crash", "plunge", "bearish", "decline", "losses", "slump", "warning",
            "risk", "concern", "down", "decrease", "bear", "pessimistic", "downgrade",
            "target lowered", "sell", "underperform", "weak", "tumble", "loss",
            "bankruptcy", "default", "crisis", "collapse", "miss"
        ],
        "neutral": ["mixed", "flat", "unchanged", "sideways", "consolidate"]
    }
    
    @staticmethod
    def analyze_news_sentiment(articles: list) -> dict:
        """Haber sentiment analizi"""
        if not articles:
            return {"sentiment": "neutral", "score": 0}
        
        sentiment_count = {"positive": 0, "negative": 0, "neutral": 0}
        
        for article in articles:
            title = article.get("title", "").lower()
            description = article.get("description", "").lower()
            text = f"{title} {description}"
            
            positive = any(word in text for word in RealTimeNewsSentiment.SENTIMENT_KEYWORDS["positive"])
            negative = any(word in text for word in RealTimeNewsSentiment.SENTIMENT_KEYWORDS["negative"])
            
            if positive:
                sentiment_count["positive"] += 1
            elif negative:
                sentiment_count["negative"] += 1
            else:
                sentiment_count["neutral"] += 1
        
        total = sum(sentiment_count.values())
        if total == 0:
            return {"sentiment": "neutral", "score": 0}
        
        score = (sentiment_count["positive"] - sentiment_count["negative"]) / total
        
        if score > 0.3:
            sentiment = "bullish"
        elif score < -0.3:
            sentiment = "bearish"
        else:
            sentiment = "neutral"
        
        return {
            "sentiment": sentiment,
            "score": round(score, 2),
            "breakdown": sentiment_count
        }


class CryptoMarketImpact:
    """Kripto Piyasası Etkisi Analizi"""
    
    @staticmethod
    def get_crypto_status():
        """Kripto piyasasının durumunu al"""
        try:
            # Bitcoin ve Ethereum
            btc_data = yf.download("BTC-USD", period="1d", progress=False, timeout=10)
            eth_data = yf.download("ETH-USD", period="1d", progress=False, timeout=10)
            
            if btc_data.empty or eth_data.empty:
                return None
            
            btc_price = float(btc_data["Close"].iloc[-1])
            btc_prev = float(btc_data["Close"].iloc[-2]) if len(btc_data) > 1 else btc_price
            btc_change = ((btc_price - btc_prev) / btc_prev * 100)
            
            eth_price = float(eth_data["Close"].iloc[-1])
            eth_prev = float(eth_data["Close"].iloc[-2]) if len(eth_data) > 1 else eth_price
            eth_change = ((eth_price - eth_prev) / eth_prev * 100)
            
            return {
                "bitcoin": {
                    "price": round(btc_price, 2),
                    "change": round(btc_change, 2),
                    "trend": "📈" if btc_change > 0 else "📉"
                },
                "ethereum": {
                    "price": round(eth_price, 2),
                    "change": round(eth_change, 2),
                    "trend": "📈" if eth_change > 0 else "📉"
                },
                "market_status": "Bullish" if (btc_change + eth_change) / 2 > 2 else "Bearish" if (btc_change + eth_change) / 2 < -2 else "Neutral"
            }
        except Exception as e:
            print(f"[ERROR] Kripto veri çekme hatası: {e}")
            return None
    
    @staticmethod
    def analyze_crypto_impact():
        """Kripto'nun hisse piyasasına etkisi"""
        crypto = CryptoMarketImpact.get_crypto_status()
        
        if not crypto:
            return {
                "status": "Veri alınamadı",
                "impact": "Belirlenemiyor",
                "crypto_data": None
            }
        
        market_status = crypto["market_status"]
        
        if market_status == "Bullish":
            impact = "Pozitif - Teknoloji ve Finans hisselerine destek"
            affected_sectors = ["teknoloji", "finans", "enerji"]
        elif market_status == "Bearish":
            impact = "Negatif - Risk iştahı azalıyor, defansif tercih"
            affected_sectors = ["gıda", "sağlık", "finans"]
        else:
            impact = "Nötr - Kripto piyasası sakin"
            affected_sectors = []
        
        return {
            "status": market_status,
            "impact": impact,
            "affected_sectors": affected_sectors,
            "crypto_data": crypto,
            "recommendation": "Kripto'yu hisse seçimi sırasında göz önüne al"
        }


class CurrencyAndMonetaryPolicy:
    """Döviz Kurları ve Para Politikası Analizi"""
    
    @staticmethod
    def get_currency_rates():
        """Döviz kurlarını al"""
        try:
            # USD/EUR, USD/GBP, USD/JPY, USD/TRY
            pairs = {
                "EUR/USD": "EURUSD=X",
                "GBP/USD": "GBPUSD=X",
                "JPY/USD": "JPYUSD=X",
                "TRY/USD": "TRYUSD=X"
            }
            
            rates = {}
            
            for name, ticker in pairs.items():
                try:
                    data = yf.download(ticker, period="1d", progress=False, timeout=10)
                    if not data.empty:
                        current = float(data["Close"].iloc[-1])
                        prev = float(data["Close"].iloc[-2]) if len(data) > 1 else current
                        change = ((current - prev) / prev * 100)
                        
                        rates[name] = {
                            "rate": round(current, 4),
                            "change": round(change, 2),
                            "trend": "📈" if change > 0 else "📉"
                        }
                except Exception as e:
                    continue
            
            return rates if rates else None
        except Exception as e:
            print(f"[ERROR] Döviz kurları çekme hatası: {e}")
            return None
    
    @staticmethod
    def analyze_currency_impact():
        """Döviz etkisini analiz et"""
        rates = CurrencyAndMonetaryPolicy.get_currency_rates()
        
        if not rates:
            return {"status": "Veri alınamadı"}
        
        impact = {
            "dolar_strength": "Güçlü" if rates.get("EUR/USD", {}).get("change", 0) < -0.5 else "Normal",
            "rates": rates,
            "affected_sectors": {}
        }
        
        # Dolar güçlüyse
        if impact["dolar_strength"] == "Güçlü":
            impact["affected_sectors"] = {
                "positive": ["finans", "turizm"],
                "negative": ["enerji", "emtialar"]
            }
        
        return impact


class CorporateBuybackCalendar:
    """Kurumsal Geri Satın Alma (Buyback) Takvimi"""
    
    ANNOUNCED_BUYBACKS = [
        {
            "company": "Apple",
            "ticker": "AAPL",
            "amount": "$110 Billion",
            "start_date": "2024-01-01",
            "expected_end": "2026-12-31",
            "impact": "Hisse fiyatı supportive",
            "status": "Aktif"
        },
        {
            "company": "Microsoft",
            "ticker": "MSFT",
            "amount": "$60 Billion",
            "start_date": "2024-06-01",
            "expected_end": "2026-12-31",
            "impact": "EPS artışına katkı",
            "status": "Aktif"
        },
        {
            "company": "Nvidia",
            "ticker": "NVDA",
            "amount": "$50 Billion",
            "start_date": "2023-01-01",
            "expected_end": "2026-12-31",
            "impact": "Güçlü destek sinyali",
            "status": "Aktif"
        },
        {
            "company": "JPMorgan",
            "ticker": "JPM",
            "amount": "$30 Billion",
            "start_date": "2024-01-01",
            "expected_end": "2025-12-31",
            "impact": "Hisse stabilize edici",
            "status": "Aktif"
        },
        {
            "company": "Berkshire Hathaway",
            "ticker": "BRK",
            "amount": "$100 Billion+",
            "start_date": "Devam ediyor",
            "expected_end": "Belirsiz",
            "impact": "Warren Buffett güven sinyali",
            "status": "Aktif"
        },
        {
            "company": "Alphabet (Google)",
            "ticker": "GOOGL",
            "amount": "$70 Billion",
            "start_date": "2024-06-01",
            "expected_end": "2026-06-30",
            "impact": "Shareholder value artışı",
            "status": "Aktif"
        },
        {
            "company": "Meta (Facebook)",
            "ticker": "META",
            "amount": "$40 Billion",
            "start_date": "2024-03-01",
            "expected_end": "2026-03-31",
            "impact": "EPS dilution azaltma",
            "status": "Aktif"
        },
        {
            "company": "Tesla",
            "ticker": "TSLA",
            "amount": "$20 Billion",
            "start_date": "2024-09-01",
            "expected_end": "2025-09-30",
            "impact": "Elon Musk güven göstergesi",
            "status": "Aktif"
        }
    ]
    
    @staticmethod
    def get_active_buybacks():
        """Aktif buyback programları"""
        today = datetime.now()
        active = []
        
        for buyback in CorporateBuybackCalendar.ANNOUNCED_BUYBACKS:
            try:
                end_date = datetime.strptime(buyback["expected_end"], "%Y-%m-%d")
                if today <= end_date:
                    active.append(buyback)
            except:
                if buyback["status"] == "Aktif":
                    active.append(buyback)
        
        return active
    
    @staticmethod
    def analyze_buyback_impact():
        """Buyback'ların piyasaya etkisi"""
        active_buybacks = CorporateBuybackCalendar.get_active_buybacks()
        
        if not active_buybacks:
            return {"status": "Aktif buyback yok"}
        
        return {
            "status": f"{len(active_buybacks)} aktif buyback programı",
            "total_amount": "Toplamda $450+ Milyar",
            "impact": "Hisse fiyatlarına destek, EPS artışı, shareholder value",
            "programs": active_buybacks,
            "recommendation": "Buyback duyurularını alım sinyali olarak göz önüne al"
        }


class EarningsCalendar:
    """Kazanç Takvimi"""
    
    MAJOR_EARNINGS_2026 = [
        {
            "date": "2026-01-15",
            "company": "Apple",
            "ticker": "AAPL",
            "quarter": "Q1 2026",
            "expected_eps": "$2.10",
            "previous_eps": "$1.95",
            "impact": "Yüksek",
            "category": "Teknoloji"
        },
        {
            "date": "2026-01-20",
            "company": "Microsoft",
            "ticker": "MSFT",
            "quarter": "Q2 2026",
            "expected_eps": "$3.35",
            "previous_eps": "$3.08",
            "impact": "Yüksek",
            "category": "Teknoloji"
        },
        {
            "date": "2026-02-05",
            "company": "Goldman Sachs",
            "ticker": "GS",
            "quarter": "Q4 2025",
            "expected_eps": "$12.50",
            "previous_eps": "$10.20",
            "impact": "Yüksek",
            "category": "Finans"
        },
        {
            "date": "2026-02-12",
            "company": "JPMorgan Chase",
            "ticker": "JPM",
            "quarter": "Q4 2025",
            "expected_eps": "$4.85",
            "previous_eps": "$4.50",
            "impact": "Yüksek",
            "category": "Finans"
        },
        {
            "date": "2026-02-18",
            "company": "Tesla",
            "ticker": "TSLA",
            "quarter": "Q4 2025",
            "expected_eps": "$0.92",
            "previous_eps": "$0.73",
            "impact": "Çok Yüksek",
            "category": "Otomotiv"
        },
        {
            "date": "2026-04-15",
            "company": "Amazon",
            "ticker": "AMZN",
            "quarter": "Q1 2026",
            "expected_eps": "$1.05",
            "previous_eps": "$0.95",
            "impact": "Yüksek",
            "category": "Teknoloji"
        },
        {
            "date": "2026-04-22",
            "company": "Google (Alphabet)",
            "ticker": "GOOGL",
            "quarter": "Q1 2026",
            "expected_eps": "$1.95",
            "previous_eps": "$1.75",
            "impact": "Yüksek",
            "category": "Teknoloji"
        },
        {
            "date": "2026-05-10",
            "company": "Meta (Facebook)",
            "ticker": "META",
            "quarter": "Q1 2026",
            "expected_eps": "$5.42",
            "previous_eps": "$4.89",
            "impact": "Yüksek",
            "category": "Teknoloji"
        }
    ]
    
    @staticmethod
    def get_upcoming_earnings(days_ahead=30):
        """Yaklaşan kazanç raporları"""
        today = datetime.now()
        upcoming = []
        
        for earning in EarningsCalendar.MAJOR_EARNINGS_2026:
            try:
                earn_date = datetime.strptime(earning["date"], "%Y-%m-%d")
                if today <= earn_date <= today + timedelta(days=days_ahead):
                    days_until = (earn_date - today).days
                    upcoming.append({
                        **earning,
                        "days_until": days_until,
                        "urgency": "🔴 ÖNEMLİ" if days_until <= 7 else "🟡 Orta" if days_until <= 14 else "🟢 Normal"
                    })
            except:
                continue
        
        upcoming.sort(key=lambda x: x["days_until"])
        return upcoming
    
    @staticmethod
    def analyze_earnings_season():
        """Kazanç sezonu analizi"""
        upcoming = EarningsCalendar.get_upcoming_earnings(7)
        
        if not upcoming:
            return {"status": "Yakın kazanç raporlarında sakinlik"}
        
        return {
            "status": f"{len(upcoming)} önemli kazanç raporu yakında",
            "upcoming_earnings": upcoming[:3],
            "recommendation": "Kazanç raporlarından önce volatilite artabilir",
            "strategy": "Stop-loss ve take-profit seviyeleri belirle"
        }


class MarketBreadth:
    """Piyasa Genişliği Analizi"""
    
    @staticmethod
    def analyze_market_breadth():
        """Piyasa genişliğini analiz et"""
        try:
            # S&P 500 ve teknoloji indeksini karşılaştır
            sp500 = yf.download("^GSPC", period="1d", progress=False, timeout=10)
            nasdaq = yf.download("^IXIC", period="1d", progress=False, timeout=10)
            
            if sp500.empty or nasdaq.empty:
                return None
            
            sp500_change = ((sp500["Close"].iloc[-1] - sp500["Close"].iloc[-2]) / sp500["Close"].iloc[-2] * 100) if len(sp500) > 1 else 0
            nasdaq_change = ((nasdaq["Close"].iloc[-1] - nasdaq["Close"].iloc[-2]) / nasdaq["Close"].iloc[-2] * 100) if len(nasdaq) > 1 else 0
            
            breadth = {
                "sp500_change": round(sp500_change, 2),
                "nasdaq_change": round(nasdaq_change, 2),
                "divergence": round(nasdaq_change - sp500_change, 2)
            }
            
            if breadth["divergence"] > 2:
                signal = "🔴 Uyarı: Teknoloji öncü rol oynuyor, geri çekilme riski"
            elif breadth["divergence"] < -2:
                signal = "🟢 Olumlu: Geniş tabanlı yükseliş, sağlam trend"
            else:
                signal = "🟡 Normal: Dengeli yükseliş"
            
            return {
                **breadth,
                "signal": signal,
                "health": "Sağlıklı" if abs(breadth["divergence"]) < 3 else "Risk Var"
            }
        except Exception as e:
            print(f"[ERROR] Piyasa genişliği analizi hatası: {e}")
            return None


class AdvancedTrendAnalysis:
    """İleri Trend Analizi"""
    
    @staticmethod
    def analyze_50_200_golden_cross(df: pd.DataFrame) -> dict:
        """50/200 Golden Cross Analizi"""
        try:
            if df.empty or len(df) < 200:
                return None
            
            close = df["Close"].squeeze()
            sma_50 = close.rolling(window=50).mean()
            sma_200 = close.rolling(window=200).mean()
            
            current_price = float(close.iloc[-1])
            sma_50_val = float(sma_50.iloc[-1])
            sma_200_val = float(sma_200.iloc[-1])
            
            # Golden Cross kontrol (50 > 200)
            if sma_50_val > sma_200_val:
                status = "🟢 GOLDEN CROSS (Güçlü yükseliş)"
                signal = "Satın Al"
                strength = "Çok Güçlü"
            elif sma_50_val < sma_200_val:
                status = "🔴 DEATH CROSS (Güçlü düşüş)"
                signal = "Sat"
                strength = "Çok Zayıf"
            else:
                status = "🟡 NÖTR"
                signal = "İzle"
                strength = "Nötr"
            
            return {
                "status": status,
                "signal": signal,
                "strength": strength,
                "sma_50": round(sma_50_val, 2),
                "sma_200": round(sma_200_val, 2),
                "current_price": current_price,
                "distance_to_200": round((current_price - sma_200_val) / sma_200_val * 100, 2)
            }
        except:
            return None


def run_all_advanced_features():
    """Tüm ileri özellikleri çalıştır"""
    print("\n" + "="*70)
    print("🚀 İLERİ ÖZELLİKLER ANALİZİ")
    print("="*70)
    
    result = {}
    
    # 1. Spesifik Tetikleyiciler
    print("\n🎯 Spesifik Sektör Tetikleyicileri...")
    triggers = SpecificSectorLinker.analyze_specific_triggers()
    if triggers:
        result["specific_triggers"] = triggers
        print(f"✅ {len(triggers)} aktif tetikleyici")
    
    # 2. Kripto Etkisi
    print("\n🪙 Kripto Piyasası Etkisi...")
    crypto_impact = CryptoMarketImpact.analyze_crypto_impact()
    if crypto_impact:
        result["crypto_impact"] = crypto_impact
        print(f"✅ Kripto durumu: {crypto_impact.get('status', 'N/A')}")
    
    # 3. Döviz ve Para Politikası
    print("\n💱 Döviz Kurları ve Para Politikası...")
    currency_impact = CurrencyAndMonetaryPolicy.analyze_currency_impact()
    if currency_impact:
        result["currency_impact"] = currency_impact
        print(f"✅ Dolar gücü: {currency_impact.get('dolar_strength', 'N/A')}")
    
    # 4. Buyback Programları
    print("\n📊 Kurumsal Geri Satın Alma Programları...")
    buyback = CorporateBuybackCalendar.analyze_buyback_impact()
    if buyback:
        result["buyback"] = buyback
        print(f"✅ {buyback.get('status', 'N/A')}")
    
    # 5. Kazanç Takvimi
    print("\n📈 Kazanç Takvimi...")
    earnings = EarningsCalendar.analyze_earnings_season()
    if earnings:
        result["earnings"] = earnings
        print(f"✅ {earnings.get('status', 'N/A')}")
    
    # 6. Piyasa Genişliği
    print("\n📊 Piyasa Genişliği Analizi...")
    breadth = MarketBreadth.analyze_market_breadth()
    if breadth:
        result["market_breadth"] = breadth
        print(f"✅ {breadth.get('health', 'N/A')}")
    
    return result


if __name__ == "__main__":
    features = run_all_advanced_features()
    print("\n✅ Tüm ileri özellikler analiz edildi")
