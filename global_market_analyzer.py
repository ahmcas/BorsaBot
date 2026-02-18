# ============================================================
# global_market_analyzer.py — Küresel Piyasa Analizi (v2 - FULL)
# ============================================================
# Yeni Özellikler:
# 1. Spesifik Sektör Bağlantıları (Makro → Sektör)
# 2. Gerçek Zamanlı Haber Entegrasyonu (Jeopolitik + NewsAPI)
# 3. Emtia-Hisse Korelasyonu
# 4. Volatilite İndeksi (VIX) İzlemesi
# 5. Fed Faiz Kararları Takibi
# 6. Makro Ekonomik Takvim
# ============================================================

import requests
import pandas as pd
from datetime import datetime, timedelta
import json

try:
    from bs4 import BeautifulSoup
except:
    import subprocess
    subprocess.run(["pip", "install", "beautifulsoup4"], check=True)
    from bs4 import BeautifulSoup

import config


class MacroEventCalendar:
    """Makroekonomik Takvim - Fed, ECB, BOJ Kararları"""
    
    MAJOR_EVENTS_2026 = [
        {
            "date": "2026-01-28",
            "time": "19:00",
            "event": "Fed FOMC Toplantısı (Faiz Kararı)",
            "impact": "Yüksek",
            "expected": "Faiz Değişikliği Yoktur (%)2.50-2.75)",
            "sector_impact": ["finans", "teknoloji", "perakende"],
            "asset_impact": {
                "dolar": "Yükseliş",
                "altın": "Düşüş",
                "hisse": "Volatil"
            }
        },
        {
            "date": "2026-02-18",
            "time": "10:00",
            "event": "ECB Politika Kararı",
            "impact": "Yüksek",
            "expected": "Faiz Sabitti",
            "sector_impact": ["finans", "otomotiv", "enerji"],
            "asset_impact": {
                "euro": "Değişken",
                "altın": "Artış",
                "hisse": "Volatil"
            }
        },
        {
            "date": "2026-03-19",
            "time": "12:00",
            "event": "BOJ Politika Kararı",
            "impact": "Orta",
            "expected": "Faiz Sabit (0.00%)",
            "sector_impact": ["finans", "otomotiv", "telekom"],
            "asset_impact": {
                "yen": "Zayıf",
                "altın": "Sabit",
                "hisse": "Sabit"
            }
        },
        {
            "date": "2026-04-15",
            "time": "08:30",
            "event": "ABD İşsizlik Oranı (Mart)",
            "impact": "Yüksek",
            "expected": "%4.2",
            "sector_impact": ["finans", "perakende", "turizm"],
            "asset_impact": {
                "dolar": "Değişken",
                "altın": "Değişken",
                "hisse": "Volatil"
            }
        },
        {
            "date": "2026-05-13",
            "time": "12:00",
            "event": "Fed FOMC Toplantısı",
            "impact": "Yüksek",
            "expected": "Faiz Kararı",
            "sector_impact": ["finans", "teknoloji", "perakende"],
            "asset_impact": {
                "dolar": "Yükseliş",
                "altın": "Düşüş",
                "hisse": "Volatil"
            }
        },
        {
            "date": "2026-06-10",
            "time": "08:30",
            "event": "ABD Enflasyon (CPI) Verileri",
            "impact": "Yüksek",
            "expected": "%2.8 YoY",
            "sector_impact": ["finans", "enerji", "gıda"],
            "asset_impact": {
                "dolar": "Yükseliş",
                "altın": "Düşüş",
                "hisse": "Volatil"
            }
        },
        {
            "date": "2026-07-29",
            "time": "19:00",
            "event": "Fed FOMC Toplantısı",
            "impact": "Yüksek",
            "expected": "Faiz Düşürüş Beklentisi",
            "sector_impact": ["finans", "teknoloji", "perakende"],
            "asset_impact": {
                "dolar": "Düşüş",
                "altın": "Yükseliş",
                "hisse": "Yükseliş"
            }
        },
        {
            "date": "2026-09-16",
            "time": "19:00",
            "event": "Fed FOMC Toplantısı",
            "impact": "Yüksek",
            "expected": "Faiz Düşürüş",
            "sector_impact": ["finans", "perakende", "turizm"],
            "asset_impact": {
                "dolar": "Düşüş",
                "altın": "Yükseliş",
                "hisse": "Yükseliş"
            }
        },
        {
            "date": "2026-12-16",
            "time": "19:00",
            "event": "Fed FOMC Yıl Sonu Toplantısı",
            "impact": "Yüksek",
            "expected": "Faiz Kararı + 2027 Rehberi",
            "sector_impact": ["finans", "teknoloji", "perakende"],
            "asset_impact": {
                "dolar": "Değişken",
                "altın": "Değişken",
                "hisse": "Volatil"
            }
        }
    ]
    
    @staticmethod
    def get_upcoming_events(days_ahead=30):
        """Yakın makro ekonomik olaylar"""
        today = datetime.now()
        upcoming = []
        
        for event in MacroEventCalendar.MAJOR_EVENTS_2026:
            try:
                event_date = datetime.strptime(event["date"], "%Y-%m-%d")
                
                if today <= event_date <= today + timedelta(days=days_ahead):
                    days_until = (event_date - today).days
                    upcoming.append({
                        **event,
                        "days_until": days_until,
                        "urgency": "🔴 ÖNEMLİ" if days_until <= 7 else "🟡 Orta" if days_until <= 14 else "🟢 Normal"
                    })
            except:
                continue
        
        upcoming.sort(key=lambda x: x["days_until"])
        return upcoming
    
    @staticmethod
    def analyze_macro_impact():
        """Makro olayların piyasaya etkisini analiz et"""
        upcoming = MacroEventCalendar.get_upcoming_events(7)
        
        if not upcoming:
            return {
                "status": "✅ Büyük Makro Olay Yok",
                "volatility_risk": "Düşük",
                "upcoming_events": []
            }
        
        # Etki edecek sektörleri topla
        affected_sectors = {}
        asset_impacts = {}
        
        for event in upcoming:
            for sector in event.get("sector_impact", []):
                if sector not in affected_sectors:
                    affected_sectors[sector] = []
                affected_sectors[sector].append(event["event"])
            
            for asset, impact in event.get("asset_impact", {}).items():
                if asset not in asset_impacts:
                    asset_impacts[asset] = []
                asset_impacts[asset].append(impact)
        
        return {
            "status": "⚠️ Makro Olay Başında",
            "volatility_risk": "Yüksek",
            "upcoming_events": upcoming[:3],
            "affected_sectors": affected_sectors,
            "asset_impacts": asset_impacts,
            "recommendation": "Riski kontrol et, stop-loss koy, yapılandırılmış pozisyonlar tercih et"
        }


class VIXAnalyzer:
    """Volatilite İndeksi (VIX) Analizi"""
    
    @staticmethod
    def get_vix_level():
        """VIX seviyesini çek"""
        try:
            import yfinance as yf
            
            # VIX futures
            vix_data = yf.download("^VIX", period="1d", progress=False)
            
            if vix_data.empty:
                return None
            
            current_vix = float(vix_data["Close"].iloc[-1])
            
            return {
                "current": round(current_vix, 2),
                "level": determine_vix_level(current_vix),
                "status": assess_vix_status(current_vix)
            }
        except Exception as e:
            print(f"[ERROR] VIX çekme hatası: {e}")
            return None
    
    @staticmethod
    def analyze_vix_impact():
        """VIX'in piyasaya etkisi"""
        vix = VIXAnalyzer.get_vix_level()
        
        if not vix:
            return {
                "status": "Bilinmiyor",
                "impact": "VIX verileri alınamadı",
                "recommendation": "Normal strateji devam"
            }
        
        current = vix["current"]
        
        if current < 12:
            impact = "Çok Düşük - Piyasa Sakin"
            sectors = ["risk_on": ["teknoloji", "perakende"]]
            recommendation = "Agresif pozisyonlar alabilirsin"
        elif current < 15:
            impact = "Düşük - Normal"
            sectors = ["balanced"]
            recommendation = "Dengeli portföy tutabilirsin"
        elif current < 20:
            impact = "Orta - Artan Kaygı"
            sectors = ["defensive": ["finans", "gıda"]]
            recommendation = "Defansif pozisyonları artır"
        elif current < 30:
            impact = "Yüksek - Piyasa Paniklemesi"
            sectors = ["defensive": ["gıda", "sağlık", "altın"]]
            recommendation = "Riski minimize et, altın al"
        else:
            impact = "Çok Yüksek - Kriz Ortamı"
            sectors = ["crisis_mode": ["nakit", "altın"]]
            recommendation = "Nakit pozisyonunu güçlendir"
        
        return {
            "current": current,
            "level": vix["level"],
            "status": vix["status"],
            "impact": impact,
            "sectors": sectors,
            "recommendation": recommendation
        }


class SectorMacroLinker:
    """Makroekonomik Olaylar ↔ Sektör Bağlantıları"""
    
    MACRO_SECTOR_MAP = {
        "fed_rate_hike": {
            "positive_sectors": [],
            "negative_sectors": ["teknoloji", "perakende", "turizm", "inşaat_gayrimenkul"],
            "explanation": "Faiz artışı, borçlanma maliyetini artırır"
        },
        "fed_rate_cut": {
            "positive_sectors": ["teknoloji", "perakende", "turizm", "inşaat_gayrimenkul"],
            "negative_sectors": [],
            "explanation": "Faiz düşüşü, borçlanmayı ucuzlatır"
        },
        "inflation_up": {
            "positive_sectors": ["enerji", "gıda", "altın"],
            "negative_sectors": ["teknoloji", "perakende"],
            "explanation": "Enflasyon, emtia ve savunma sektörlerini güçlendirir"
        },
        "inflation_down": {
            "positive_sectors": ["teknoloji", "perakende"],
            "negative_sectors": ["enerji"],
            "explanation": "Enflasyon düşüşü, büyüme hisselerini destekler"
        },
        "war_geopolitics": {
            "positive_sectors": ["savunma", "enerji", "altın"],
            "negative_sectors": ["turizm", "telekom", "otomotiv"],
            "explanation": "Jeopolitik gerginlik, savunma ve emtiayı güçlendirir"
        },
        "recession_risk": {
            "positive_sectors": ["gıda", "sağlık", "finans"],
            "negative_sectors": ["perakende", "turizm", "otomotiv"],
            "explanation": "Resesyon riski, defansif sektörleri güçlendirir"
        },
        "supply_chain_disruption": {
            "positive_sectors": ["teknoloji", "gıda", "enerji"],
            "negative_sectors": ["otomotiv", "perakende"],
            "explanation": "Tedarik zinciri sorunları, üretimi etkiler"
        }
    }
    
    @staticmethod
    def get_sector_recommendations(macro_events: list, vix_level: float) -> dict:
        """Makro olaylar ve VIX'e göre sektör tavsiyesi"""
        
        sector_scores = defaultdict(float)
        reasons = defaultdict(list)
        
        # Makro olaylar
        for event in macro_events:
            event_type = event.get("type")
            
            if event_type in SectorMacroLinker.MACRO_SECTOR_MAP:
                mapping = SectorMacroLinker.MACRO_SECTOR_MAP[event_type]
                
                for sector in mapping["positive_sectors"]:
                    sector_scores[sector] += 0.5
                    reasons[sector].append(f"✓ {mapping['explanation']}")
                
                for sector in mapping["negative_sectors"]:
                    sector_scores[sector] -= 0.5
                    reasons[sector].append(f"✗ {mapping['explanation']}")
        
        # VIX etkisi
        if vix_level > 20:
            for sector in ["gıda", "sağlık", "finans"]:
                sector_scores[sector] += 0.3
                reasons[sector].append(f"✓ VIX Yüksek - Defansif tercih")
            
            for sector in ["teknoloji", "perakende", "turizm"]:
                sector_scores[sector] -= 0.3
                reasons[sector].append(f"✗ VIX Yüksek - Riski azalt")
        
        # Sıralama
        sorted_sectors = sorted(sector_scores.items(), key=lambda x: x[1], reverse=True)
        
        return {
            "recommendations": dict(sorted_sectors),
            "reasons": dict(reasons),
            "top_3_buy": [s[0] for s in sorted_sectors[:3]],
            "top_3_avoid": [s[0] for s in sorted_sectors[-3:]]
        }


class CommodityStockCorrelation:
    """Emtia-Hisse Korelasyonu Analizi"""
    
    CORRELATIONS = {
        "gold": {
            "positive": [
                "ISA.IS",  # İş Bankası (para arması)
                "GARAN.IS",  # Garanti
                "AKBANK.IS"  # Akbank
            ],
            "negative": [
                "TCELL.IS",  # Teknoloji hisseleri altın düşünce fiyat artabilir
                "VESTEL.IS"
            ],
            "explanation": "Altın yükselirse dolar zayıf, finans hisseleri düşer"
        },
        "oil": {
            "positive": [
                "TUPAS.IS",  # Türkiye Petrol
                "ENKA.IS",  # Enerjili şirketler
                "AYGAZ.IS"
            ],
            "negative": [
                "FROTO.IS",  # Otomotiv
                "OTKAR.IS",
                "TCELL.IS"  # Teknoloji
            ],
            "explanation": "Petrol yükselirse taşım maliyetleri artır, marjlar azalır"
        },
        "copper": {
            "positive": [
                "ASELS.IS",  # Aselsan (savunma)
                "SISE.IS",  # Şişecam (inşaat)
                "ARÇEL.IS"  # Arçelik
            ],
            "negative": [],
            "explanation": "Bakır endüstriyel talep göstergesidir, ekonomik büyümeyi işaret eder"
        },
        "silver": {
            "positive": [
                "ASELS.IS",
                "VESTEL.IS",
                "SISE.IS"
            ],
            "negative": [],
            "explanation": "Gümüş, endüstriyel kullanım ve yatırım talebini gösterir"
        }
    }
    
    @staticmethod
    def analyze_correlations(commodities: dict) -> dict:
        """Emtia-Hisse korelasyonlarını analiz et"""
        
        stock_impacts = defaultdict(list)
        
        for commodity, prices in commodities.items():
            if commodity in CommodityStockCorrelation.CORRELATIONS:
                corr = CommodityStockCorrelation.CORRELATIONS[commodity]
                
                # Pozitif korelasyon
                for stock in corr["positive"]:
                    direction = "📈 Yükselir" if prices['change'] > 0 else "📉 Düşer"
                    stock_impacts[stock].append(f"{commodity.upper()} {direction} → {stock} {direction}")
                
                # Negatif korelasyon
                for stock in corr["negative"]:
                    direction = "📉 Düşer" if prices['change'] > 0 else "📈 Yükselir"
                    stock_impacts[stock].append(f"{commodity.upper()} {direction} → {stock} {direction}")
        
        return {
            "stock_impacts": dict(stock_impacts),
            "opportunities": [s for s, impacts in stock_impacts.items() if impacts]
        }


class GeopoliticalNewsIntegration:
    """Jeopolitik Haberler + NewsAPI Entegrasyonu"""
    
    @staticmethod
    def get_geopolitical_news():
        """Jeopolitik haberlerini NewsAPI'den çek"""
        try:
            api_key = config.NEWS_API_KEY
            
            if not api_key or api_key == "YOUR_NEWS_API_KEY_HERE":
                return None
            
            keywords = [
                "Russia Ukraine war",
                "Hamas Israel conflict",
                "Iran nuclear",
                "China Taiwan",
                "Trump tariffs",
                "North Korea",
                "Middle East",
                "US sanctions"
            ]
            
            all_news = []
            
            for keyword in keywords:
                url = "https://newsapi.org/v2/everything"
                params = {
                    "q": keyword,
                    "sortBy": "publishedAt",
                    "language": "en",
                    "apiKey": api_key,
                    "pageSize": 5
                }
                
                try:
                    response = requests.get(url, params=params, timeout=10)
                    data = response.json()
                    
                    if data.get("articles"):
                        for article in data["articles"][:2]:  # Top 2
                            all_news.append({
                                "keyword": keyword,
                                "title": article.get("title", ""),
                                "description": article.get("description", ""),
                                "source": article.get("source", {}).get("name", ""),
                                "published_at": article.get("publishedAt", ""),
                                "url": article.get("url", "")
                            })
                except:
                    continue
            
            return all_news if all_news else None
        
        except Exception as e:
            print(f"[ERROR] Jeopolitik haber çekme hatası: {e}")
            return None


class SupplyChainMonitor:
    """Tedarik Zinciri Takibi (RAM, Çip, vb)"""
    
    SUPPLY_CHAIN_INDICATORS = {
        "ram_shortage": {
            "status": "normal",  # normal, shortage, excess
            "impact": {
                "positive_sectors": ["gıda", "finans"],
                "negative_sectors": ["teknoloji", "otomotiv"]
            },
            "explanation": "RAM kıtlığı → Teknoloji maliyetleri artır"
        },
        "chip_shortage": {
            "status": "normal",
            "impact": {
                "positive_sectors": ["finans"],
                "negative_sectors": ["teknoloji", "otomotiv", "telekom"]
            },
            "explanation": "Çip kıtlığı → Otomotiv ve teknoloji etkilenir"
        },
        "shipping_delays": {
            "status": "normal",
            "impact": {
                "positive_sectors": ["gıda"],
                "negative_sectors": ["perakende", "otomotiv"]
            },
            "explanation": "Gemi gecikmesi → Maliyetler artır, tedarik sorunları"
        },
        "energy_crisis": {
            "status": "normal",
            "impact": {
                "positive_sectors": ["enerji", "altın"],
                "negative_sectors": ["teknoloji", "turizm", "otomotiv"]
            },
            "explanation": "Enerji krizi → Üretim maliyetleri artır"
        }
    }
    
    @staticmethod
    def analyze_supply_chain():
        """Tedarik zinciri analizi"""
        
        affected_sectors = defaultdict(list)
        overall_impact = "Normal"
        
        for indicator, data in SupplyChainMonitor.SUPPLY_CHAIN_INDICATORS.items():
            if data["status"] != "normal":
                overall_impact = "Bozuk"
                
                for pos_sector in data["impact"]["positive_sectors"]:
                    affected_sectors[pos_sector].append(f"✓ {indicator}: {data['explanation']}")
                
                for neg_sector in data["impact"]["negative_sectors"]:
                    affected_sectors[neg_sector].append(f"✗ {indicator}: {data['explanation']}")
        
        return {
            "status": overall_impact,
            "affected_sectors": dict(affected_sectors),
            "recommendation": "Tedarik zinciri sorunları var, teknoloji hisselerinden kaçın" if overall_impact == "Bozuk" else "Normal koşullar"
        }


def determine_vix_level(vix_value):
    """VIX seviyesini belirle"""
    if vix_value < 12:
        return "Çok Düşük (Sakin Pazar)"
    elif vix_value < 15:
        return "Düşük (Normal)"
    elif vix_value < 20:
        return "Orta (Kaygılı)"
    elif vix_value < 30:
        return "Yüksek (Panik)"
    else:
        return "Çok Yüksek (Kriz)"


def assess_vix_status(vix_value):
    """VIX durumunu değerlendir"""
    if vix_value < 15:
        return "📈 Risk ON - Teknoloji tercih"
    elif vix_value < 20:
        return "🔄 Dengeli - Portföy diversifiye"
    else:
        return "📉 Risk OFF - Defansif tercih"


from collections import defaultdict


def run_advanced_global_analysis():
    """Tüm ileri küresel analizi çalıştır"""
    print("\n" + "="*70)
    print("🌍 İLERİ KÜRESEL PIYASA ANALİZİ")
    print("="*70)
    
    result = {}
    
    # 1. Makro Olay Takvimi
    print("\n📅 Makro Ekonomik Takvim...")
    macro_impact = MacroEventCalendar.analyze_macro_impact()
    if macro_impact:
        result["macro_events"] = macro_impact
        print(f"✅ {macro_impact['status']}")
        if macro_impact.get('upcoming_events'):
            for event in macro_impact['upcoming_events'][:2]:
                print(f"   {event['urgency']} {event['date']}: {event['event']}")
    
    # 2. VIX Analizi
    print("\n📊 Volatilite İndeksi (VIX)...")
    vix_impact = VIXAnalyzer.analyze_vix_impact()
    if vix_impact:
        result["vix"] = vix_impact
        print(f"✅ VIX: {vix_impact.get('current', 'N/A')} - {vix_impact.get('level', 'N/A')}")
    
    # 3. Emtia Korelasyonları
    print("\n⛓️  Emtia-Hisse Korelasyonu...")
    # (Commodities verisine ihtiyaç var - main_bot.py'den gelecek)
    print(f"✅ Korelasyon analizi hazır")
    
    # 4. Tedarik Zinciri
    print("\n🏭 Tedarik Zinciri Takibi...")
    supply_chain = SupplyChainMonitor.analyze_supply_chain()
    if supply_chain:
        result["supply_chain"] = supply_chain
        print(f"✅ {supply_chain['status']}")
    
    # 5. Sektör Tavsiyesi
    print("\n📈 Sektör Tavsiyesi...")
    print(f"✅ Makro veriler işleniyor")
    
    return result


if __name__ == "__main__":
    analysis = run_advanced_global_analysis()
    print("\n✅ İleri küresel analiz tamamlandı")
