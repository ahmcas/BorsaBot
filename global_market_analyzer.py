# ============================================================
# global_market_analyzer.py — Küresel Piyasa Analizi (v1)
# ============================================================
# Bu modül:
# 1. ABD dış borcu takip eder
# 2. Commodity (bakır, gümüş, altın) fiyatlarını analiz eder
# 3. Jeopolitik olayları izler
# 4. Dünya borsa tatillerini takip eder
# 5. Küresel makroekonomik olayları izler
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


class USDebtAnalyzer:
    """ABD Dış Borcu Analizi"""
    
    @staticmethod
    def get_us_debt():
        """ABD dış borcunu çek"""
        try:
            # Dünya Bankası API
            url = "https://api.worldbank.org/v2/country/USA/indicator/DT.DOD.DECT.CD"
            params = {
                "format": "json",
                "date": "2020:2026"
            }
            
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            if len(data) < 2:
                return None
            
            records = data[1]
            debt_data = []
            
            for record in records:
                if record['value']:
                    debt_data.append({
                        "year": int(record['date']),
                        "debt": float(record['value']),
                        "debt_billion": float(record['value']) / 1e9
                    })
            
            debt_data.sort(key=lambda x: x['year'])
            
            if not debt_data:
                return None
            
            return {
                "current": debt_data[-1],
                "previous": debt_data[-2] if len(debt_data) > 1 else None,
                "all": debt_data,
                "trend": calculate_trend(debt_data)
            }
            
        except Exception as e:
            print(f"[ERROR] US Debt çekme hatası: {e}")
            return None
    
    @staticmethod
    def analyze_debt_impact():
        """Borç seviyesinin piyasaya etkisini analiz et"""
        try:
            debt_info = USDebtAnalyzer.get_us_debt()
            
            if not debt_info:
                return {
                    "level": "Bilinmiyor",
                    "risk": "Orta",
                    "impact": "Belirsiz",
                    "recommendation": "ABD borç verileri alınamadı"
                }
            
            current_debt = debt_info['current']['debt_billion']
            trend = debt_info['trend']
            
            # Borç seviyeleri
            if current_debt > 35000:  # 35 Trilyon USD
                level = "🔴 AŞIRI YÜKSEK"
                risk = "Çok Yüksek"
                impact = "USD zayıflaması, enflasyon baskısı, faiz artışları"
                recommendation = "Dolar cinsinden pozisyonları azalt, altın/gümüş al"
            elif current_debt > 30000:
                level = "🟠 ÇOOK YÜKSEK"
                risk = "Yüksek"
                impact = "Piyasa volatilitesi artar, para değer kaybeder"
                recommendation = "Risk pozisyonlarını azalt"
            elif current_debt > 25000:
                level = "🟡 YÜKSEK"
                risk = "Orta-Yüksek"
                impact = "Faiz artışı baskısı, dolar weak"
                recommendation = "Diversifikasyon önemli"
            else:
                level = "🟢 KONTROL ALTINDA"
                risk = "Düşük"
                impact = "Normal piyasa ortamı"
                recommendation = "Normal strateji devam"
            
            return {
                "level": level,
                "current_debt_billion": round(current_debt, 1),
                "risk": risk,
                "impact": impact,
                "recommendation": recommendation,
                "trend": trend,
                "historical": debt_info.get('all', [])
            }
            
        except Exception as e:
            print(f"[ERROR] Debt impact analizi hatası: {e}")
            return None


class CommodityAnalyzer:
    """Emtia Analizi (Altın, Gümüş, Bakır, Petrol)"""
    
    # Emtiaların geçmiş önemli olayları
    COMMODITY_EVENTS = {
        "gold": [
            {"date": "2008-09-15", "event": "Lehman Brothers Çöküşü", "impact": "Altın +25% (6 ay)"},
            {"date": "2020-03-16", "event": "COVID-19 Crash", "impact": "Altın +15% (3 ay)"},
            {"date": "2022-02-24", "event": "Rusya-Ukrayna Savaşı", "impact": "Altın +5% (1 ay)"},
            {"date": "2023-03-10", "event": "SVB Bankası Çöküşü", "impact": "Altın +3% (2 hafta)"},
        ],
        "silver": [
            {"date": "2008-09-15", "event": "Finansal Kriz", "impact": "Gümüş +40% (6 ay)"},
            {"date": "2020-08-06", "event": "Teknoloji Balonları", "impact": "Gümüş +55% (6 ay)"},
            {"date": "2021-01-28", "event": "GameStop-Meme Stock", "impact": "Gümüş Volatil"},
        ],
        "copper": [
            {"date": "2008-09-15", "event": "Finansal Kriz", "impact": "Bakır -58% (6 ay)"},
            {"date": "2020-03-18", "event": "COVID Taşıyıcısı", "impact": "Bakır -40% (3 hafta)"},
            {"date": "2021-05-20", "event": "Yeniden Açılış", "impact": "Bakır +80% (6 ay)"},
            {"date": "2022-02-24", "event": "Savaş Kaygısı", "impact": "Bakır +10% (1 ay)"},
        ],
        "oil": [
            {"date": "2008-09-15", "event": "Finansal Kriz", "impact": "Petrol -78% (6 ay)"},
            {"date": "2020-04-20", "event": "Negative Oil Prices", "impact": "Petrol Çöküşü"},
            {"date": "2022-02-24", "event": "Rusya-Ukrayna", "impact": "Petrol +50% (2 ay)"},
            {"date": "2023-09-18", "event": "İran Görüşmeler", "impact": "Petrol +10% (1 ay)"},
        ]
    }
    
    @staticmethod
    def get_commodity_prices():
        """Emtia fiyatlarını çek (yfinance üzerinden)"""
        try:
            import yfinance as yf
            
            commodities = {
                "gold": "GC=F",      # Gold Futures
                "silver": "SI=F",    # Silver Futures
                "copper": "HG=F",    # Copper Futures
                "oil": "CL=F",       # Crude Oil Futures
                "natural_gas": "NG=F" # Natural Gas Futures
            }
            
            prices = {}
            
            for name, ticker in commodities.items():
                try:
                    data = yf.download(ticker, period="1d", progress=False)
                    if not data.empty:
                        current = float(data["Close"].iloc[-1])
                        prev_close = float(data["Close"].iloc[-2]) if len(data) > 1 else current
                        change_pct = ((current - prev_close) / prev_close * 100) if prev_close != 0 else 0
                        
                        prices[name] = {
                            "ticker": ticker,
                            "current": round(current, 2),
                            "change": round(change_pct, 2),
                            "trend": "📈" if change_pct > 0 else "📉"
                        }
                except:
                    continue
            
            return prices if prices else None
            
        except Exception as e:
            print(f"[ERROR] Commodity fiyatları çekme hatası: {e}")
            return None
    
    @staticmethod
    def analyze_commodity_records():
        """Emtiaların rekor seviyelerini analiz et"""
        try:
            import yfinance as yf
            
            commodities = {
                "altın": ("GC=F", "gold"),
                "gümüş": ("SI=F", "silver"),
                "bakır": ("HG=F", "copper"),
                "petrol": ("CL=F", "oil"),
            }
            
            records = {}
            
            for name, (ticker, key) in commodities.items():
                try:
                    # 10 yıllık veri
                    data = yf.download(ticker, period="10y", progress=False)
                    
                    if not data.empty:
                        current = float(data["Close"].iloc[-1])
                        all_time_high = float(data["High"].max())
                        all_time_low = float(data["Low"].min())
                        
                        # Rekor kırıldı mı?
                        is_record = current >= all_time_high * 0.95
                        
                        records[key] = {
                            "name": name,
                            "current": round(current, 2),
                            "all_time_high": round(all_time_high, 2),
                            "all_time_low": round(all_time_low, 2),
                            "is_record": is_record,
                            "distance_to_high": round((all_time_high - current) / all_time_high * 100, 1),
                            "events": CommodityAnalyzer.COMMODITY_EVENTS.get(key, [])
                        }
                except:
                    continue
            
            return records if records else None
            
        except Exception as e:
            print(f"[ERROR] Commodity records analizi hatası: {e}")
            return None


class GeopoliticalAnalyzer:
    """Jeopolitik Olay Analizi"""
    
    # Önemli jeopolitik olaylar ve etkileri
    GEOPOLITICAL_EVENTS = [
        {
            "date": "2022-02-24",
            "event": "Rusya-Ukrayna Savaşı Başlangıcı",
            "impact": ["Petrol +50%", "Gaz +300%", "Altın +10%", "Teknoloji -15%"],
            "duration": "24+ ay",
            "status": "Devam ediyor"
        },
        {
            "date": "2023-10-07",
            "event": "Hamas-İsrail Savaşı",
            "impact": ["Ortadoğu Volatil", "Petrol +5%", "Savunma Hisseleri +8%", "Teknoloji -2%"],
            "duration": "6+ ay",
            "status": "Devam ediyor"
        },
        {
            "date": "2024-04-14",
            "event": "İran-İsrail Gerginliği",
            "impact": ["Petrol +3%", "Altın +2%", "Risk Appetite -5%"],
            "duration": "Devam eden",
            "status": "Monitorleniyor"
        },
        {
            "date": "2025-01-20",
            "event": "Trump 2. Dönem (Tarife Tehdidi)",
            "impact": ["Teknoloji -5%", "Enerji +3%", "Altın +8%", "Dolar +2%"],
            "duration": "Başlangıç",
            "status": "Aktif"
        },
        {
            "date": "2026-02-00",
            "event": "Çin Teknoloji İnovasyonları",
            "impact": ["Teknoloji Volatil", "Yarı İletken +/-10%", "AI Hisseler Volatil"],
            "duration": "Devam eden",
            "status": "Gözlem"
        }
    ]
    
    @staticmethod
    def get_current_geopolitical_status():
        """Şu an aktif jeopolitik olaylar"""
        return [event for event in GeopoliticalAnalyzer.GEOPOLITICAL_EVENTS 
                if event["status"] in ["Devam ediyor", "Aktif", "Monitorleniyor"]]
    
    @staticmethod
    def analyze_impact_on_markets():
        """Jeopolitik olayların piyasaya etkisi"""
        events = GeopoliticalAnalyzer.get_current_geopolitical_status()
        
        risk_sectors = []
        opportunity_sectors = []
        
        for event in events:
            impacts = event["impact"]
            
            for impact in impacts:
                if "+" in impact:
                    opportunity_sectors.append(impact)
                elif "-" in impact:
                    risk_sectors.append(impact)
        
        return {
            "events": events,
            "risk_sectors": risk_sectors,
            "opportunity_sectors": opportunity_sectors,
            "overall_sentiment": "Yüksek Volatilite" if len(events) > 2 else "Normal"
        }


class ExchangeHolidayTracker:
    """Borsa Tatil Takvimi"""
    
    MAJOR_EXCHANGES = {
        "NYSE": {
            "name": "New York Stock Exchange",
            "region": "ABD",
            "holidays_2026": [
                {"date": "2026-01-01", "event": "Yeni Yıl", "impact": "Kapalı"},
                {"date": "2026-01-19", "event": "Martin Luther King Jr. Day", "impact": "Kapalı"},
                {"date": "2026-02-16", "event": "Presidents' Day", "impact": "Kapalı"},
                {"date": "2026-03-27", "event": "Good Friday", "impact": "Kapalı"},
                {"date": "2026-05-25", "event": "Memorial Day", "impact": "Kapalı"},
                {"date": "2026-07-03", "event": "Independence Day (Friday)", "impact": "Kapalı"},
                {"date": "2026-09-07", "event": "Labor Day", "impact": "Kapalı"},
                {"date": "2026-11-26", "event": "Thanksgiving", "impact": "Kapalı"},
                {"date": "2026-12-25", "event": "Christmas", "impact": "Kapalı"},
            ]
        },
        "SSE": {
            "name": "Shanghai Stock Exchange",
            "region": "Çin",
            "holidays_2026": [
                {"date": "2026-01-01", "event": "Yeni Yıl", "impact": "Kapalı"},
                {"date": "2026-01-29-02-06", "event": "Çin Yeni Yılı (Spring Festival)", "impact": "1 hafta kapalı"},
                {"date": "2026-04-04-06", "event": "Qingming Festival", "impact": "3 gün kapalı"},
                {"date": "2026-06-10", "event": "Dragon Boat Festival", "impact": "3 gün kapalı"},
                {"date": "2026-09-15", "event": "Mid-Autumn Festival", "impact": "3 gün kapalı"},
                {"date": "2026-10-01-07", "event": "Ulusal Tatil", "impact": "1 hafta kapalı"},
            ]
        },
        "LSE": {
            "name": "London Stock Exchange",
            "region": "İngiltere",
            "holidays_2026": [
                {"date": "2026-01-01", "event": "New Year's Day", "impact": "Kapalı"},
                {"date": "2026-04-10", "event": "Good Friday", "impact": "Kapalı"},
                {"date": "2026-04-13", "event": "Easter Monday", "impact": "Kapalı"},
                {"date": "2026-05-04", "event": "Early May Bank Holiday", "impact": "Kapalı"},
                {"date": "2026-05-25", "event": "Spring Bank Holiday", "impact": "Kapalı"},
                {"date": "2026-08-31", "event": "Summer Bank Holiday", "impact": "Kapalı"},
                {"date": "2026-12-25", "event": "Christmas Day", "impact": "Kapalı"},
                {"date": "2026-12-28", "event": "Boxing Day (observed)", "impact": "Kapalı"},
            ]
        },
        "TSE": {
            "name": "Tokyo Stock Exchange",
            "region": "Japonya",
            "holidays_2026": [
                {"date": "2026-01-01", "event": "New Year's Day", "impact": "Kapalı"},
                {"date": "2026-01-12", "event": "Coming of Age Day", "impact": "Kapalı"},
                {"date": "2026-02-11", "event": "Foundation Day", "impact": "Kapalı"},
                {"date": "2026-03-20", "event": "Vernal Equinox", "impact": "Kapalı"},
                {"date": "2026-04-29", "event": "Showa Day", "impact": "Kapalı"},
                {"date": "2026-05-03", "event": "Constitution Day", "impact": "Kapalı"},
                {"date": "2026-07-23", "event": "Marine Day", "impact": "Kapalı"},
                {"date": "2026-09-21", "event": "Autumn Equinox", "impact": "Kapalı"},
                {"date": "2026-10-12", "event": "Sports Day", "impact": "Kapalı"},
                {"date": "2026-11-03", "event": "Culture Day", "impact": "Kapalı"},
                {"date": "2026-11-23", "event": "Labor Thanksgiving Day", "impact": "Kapalı"},
            ]
        },
        "BIST": {
            "name": "Borsa Istanbul",
            "region": "Türkiye",
            "holidays_2026": [
                {"date": "2026-01-01", "event": "New Year", "impact": "Kapalı"},
                {"date": "2026-04-23", "event": "National Sovereignty Day", "impact": "Kapalı"},
                {"date": "2026-05-01", "event": "Labor Day", "impact": "Kapalı"},
                {"date": "2026-07-15", "event": "Democracy Day", "impact": "Kapalı"},
                {"date": "2026-08-30", "event": "Victory Day", "impact": "Kapalı"},
                {"date": "2026-10-29", "event": "Republic Day", "impact": "Kapalı"},
            ]
        }
    }
    
    @staticmethod
    def get_upcoming_holidays(days_ahead=30):
        """Önümüzdeki tatilleri listele"""
        from datetime import datetime, timedelta
        
        today = datetime.now()
        upcoming_holidays = []
        
        for exchange, details in ExchangeHolidayTracker.MAJOR_EXCHANGES.items():
            for holiday in details.get("holidays_2026", []):
                try:
                    holiday_date = datetime.strptime(holiday["date"].split("-")[0], "%Y-%m-%d")
                    
                    if today <= holiday_date <= today + timedelta(days=days_ahead):
                        upcoming_holidays.append({
                            "exchange": exchange,
                            "region": details["region"],
                            "date": holiday["date"],
                            "event": holiday["event"],
                            "impact": holiday["impact"],
                            "days_until": (holiday_date - today).days
                        })
                except:
                    continue
        
        upcoming_holidays.sort(key=lambda x: x["days_until"])
        return upcoming_holidays
    
    @staticmethod
    def analyze_holiday_impact():
        """Yakın tatillerin volatiliteye etkisi"""
        upcoming = ExchangeHolidayTracker.get_upcoming_holidays(14)
        
        if not upcoming:
            return {
                "status": "✅ Normal Operasyon",
                "volatility_risk": "Düşük",
                "upcoming_holidays": []
            }
        
        return {
            "status": "⚠️ Yakın Tatil",
            "volatility_risk": "Yüksek - Beklentiler artabilir",
            "upcoming_holidays": upcoming[:3],  # İlk 3 tatil
            "recommendation": "Risk pozisyonlarını azalt, likidite sıkıntısı yaşanabilir"
        }


def calculate_trend(data):
    """Trend hesapla (artan/azalan/sabit)"""
    if len(data) < 2:
        return "Bilinmiyor"
    
    first = data[0]['debt_billion']
    last = data[-1]['debt_billion']
    
    change_pct = ((last - first) / first * 100)
    
    if change_pct > 10:
        return "📈 Hızlı Artış"
    elif change_pct > 2:
        return "📈 Yavaş Artış"
    elif change_pct < -10:
        return "📉 Hızlı Düşüş"
    elif change_pct < -2:
        return "📉 Yavaş Düşüş"
    else:
        return "⟶ Sabit"


def run_global_analysis():
    """Tüm küresel analizi çalıştır"""
    print("\n" + "="*70)
    print("🌍 KÜRESEL PIYASA ANALİZİ")
    print("="*70)
    
    result = {}
    
    # 1. US Debt
    print("\n📊 ABD Dış Borcu Analizi...")
    us_debt = USDebtAnalyzer.analyze_debt_impact()
    if us_debt:
        result["us_debt"] = us_debt
        print(f"✅ {us_debt['level']}")
    
    # 2. Commodities
    print("\n🏭 Emtia Fiyatları...")
    commodities = CommodityAnalyzer.get_commodity_prices()
    if commodities:
        result["commodities"] = commodities
        print(f"✅ {len(commodities)} emtia fiyatlandı")
    
    # 3. Commodity Records
    print("\n📈 Emtia Rekor Analizi...")
    records = CommodityAnalyzer.analyze_commodity_records()
    if records:
        result["commodity_records"] = records
        print(f"✅ {len(records)} emtia analiz edildi")
    
    # 4. Geopolitics
    print("\n🗺️ Jeopolitik Olay Analizi...")
    geopolitical = GeopoliticalAnalyzer.analyze_impact_on_markets()
    if geopolitical:
        result["geopolitical"] = geopolitical
        print(f"✅ {len(geopolitical['events'])} aktif olay")
    
    # 5. Holiday Impact
    print("\n📅 Borsa Tatil Analizi...")
    holidays = ExchangeHolidayTracker.analyze_holiday_impact()
    if holidays:
        result["exchange_holidays"] = holidays
        print(f"✅ {len(holidays.get('upcoming_holidays', []))} yakın tatil")
    
    return result


if __name__ == "__main__":
    analysis = run_global_analysis()
    print("\n✅ Küresel analiz tamamlandı")
