# ============================================================
# global_market_analyzer.py — Küresel Piyasa Analizi (v4 - KOMPLE FINAL)
# ============================================================
# Tüm Özellikleri:
# 1. ABD Dış Borcu Analizi
# 2. Emtia Fiyatları (5 çeşit)
# 3. Emtia Rekor Analizi + Geçmiş Olaylar
# 4. Jeopolitik Olay Takibi
# 5. Borsa Tatil Takvimi
# 6. Makro Ekonomik Takvim
# 7. VIX Volatilite İndeksi
# 8. Sektör Tavsiyesi (Makro + VIX)
# 9. Emtia-Hisse Korelasyonları
# 10. Tedarik Zinciri Monitoring
# 11. Jeopolitik NewsAPI Integration
# ============================================================

import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
from collections import defaultdict

try:
    from bs4 import BeautifulSoup
except:
    import subprocess
    subprocess.run(["pip", "install", "beautifulsoup4"], check=True)
    from bs4 import BeautifulSoup

try:
    import yfinance as yf
except:
    import subprocess
    subprocess.run(["pip", "install", "yfinance"], check=True)
    import yfinance as yf

import config


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
                if record and record.get('value'):
                    try:
                        debt_data.append({
                            "year": int(record['date']),
                            "debt": float(record['value']),
                            "debt_billion": float(record['value']) / 1e9
                        })
                    except:
                        continue
            
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
                level = "🟠 ÇOK YÜKSEK"
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
    """Emtia Analizi (Altın, Gümüş, Bakır, Petrol, Doğalgaz)"""
    
    # Emtiaların geçmiş önemli olayları
    COMMODITY_EVENTS = {
        "gold": [
            {"date": "2008-09-15", "event": "Lehman Brothers Çöküşü", "impact": "Altın +25% (6 ay)"},
            {"date": "2020-03-16", "event": "COVID-19 Crash", "impact": "Altın +15% (3 ay)"},
            {"date": "2022-02-24", "event": "Rusya-Ukrayna Savaşı", "impact": "Altın +5% (1 ay)"},
            {"date": "2023-03-10", "event": "SVB Bankası Çöküşü", "impact": "Altın +3% (2 hafta)"},
            {"date": "2024-08-05", "event": "Yen Carry Trade Crash", "impact": "Altın -5% (1 hafta)"},
        ],
        "silver": [
            {"date": "2008-09-15", "event": "Finansal Kriz", "impact": "Gümüş +40% (6 ay)"},
            {"date": "2020-08-06", "event": "Teknoloji Balonları", "impact": "Gümüş +55% (6 ay)"},
            {"date": "2021-01-28", "event": "GameStop-Meme Stock", "impact": "Gümüş Volatil +100%"},
            {"date": "2023-03-10", "event": "SVB Çöküşü", "impact": "Gümüş +8% (1 ay)"},
        ],
        "copper": [
            {"date": "2008-09-15", "event": "Finansal Kriz", "impact": "Bakır -58% (6 ay)"},
            {"date": "2020-03-18", "event": "COVID Taşıyıcısı", "impact": "Bakır -40% (3 hafta)"},
            {"date": "2020-11-01", "event": "Yeniden Açılış", "impact": "Bakır +80% (6 ay)"},
            {"date": "2022-02-24", "event": "Savaş Kaygısı", "impact": "Bakır +10% (1 ay)"},
            {"date": "2023-01-15", "event": "Çin Açılışı", "impact": "Bakır +25% (2 ay)"},
        ],
        "oil": [
            {"date": "2008-09-15", "event": "Finansal Kriz", "impact": "Petrol -78% (6 ay)"},
            {"date": "2014-06-20", "event": "Şale Devrim", "impact": "Petrol -60% (6 ay)"},
            {"date": "2020-04-20", "event": "Negative Oil Prices", "impact": "Petrol Çöküşü -300%"},
            {"date": "2022-02-24", "event": "Rusya-Ukrayna", "impact": "Petrol +50% (2 ay)"},
            {"date": "2023-09-18", "event": "Suudi Kesinti", "impact": "Petrol +10% (1 ay)"},
        ],
        "natural_gas": [
            {"date": "2021-09-01", "event": "Avrupa Krizesi", "impact": "Doğalgaz +400% (3 ay)"},
            {"date": "2022-02-24", "event": "Savaş", "impact": "Doğalgaz +300% (1 ay)"},
            {"date": "2023-08-01", "event": "Kapalı Gazdan Çıkış", "impact": "Doğalgaz -50% (4 ay)"},
        ]
    }
    
    @staticmethod
    def get_commodity_prices():
        """Emtia fiyatlarını çek (yfinance üzerinden)"""
        try:
            commodities = {
                "gold": "GC=F",
                "silver": "SI=F",
                "copper": "HG=F",
                "oil": "CL=F",
                "natural_gas": "NG=F"
            }
            
            prices = {}
            
            for name, ticker in commodities.items():
                try:
                    data = yf.download(ticker, period="1d", progress=False, timeout=10)
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
                except Exception as e:
                    continue
            
            return prices if prices else None
            
        except Exception as e:
            print(f"[ERROR] Commodity fiyatları çekme hatası: {e}")
            return None
    
    @staticmethod
    def analyze_commodity_records():
        """Emtiaların rekor seviyelerini analiz et"""
        try:
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
                    data = yf.download(ticker, period="10y", progress=False, timeout=10)
                    
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
                except Exception as e:
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
        },
        {
            "date": "2024-10-01",
            "event": "BRICS Genişlemesi",
            "impact": ["Dolar -2%", "Altın +3%", "Petrol +1%", "Gelişmekte Olan Pazarlar +5%"],
            "duration": "Uzun vadeli",
            "status": "Gözlem"
        },
        {
            "date": "2025-06-15",
            "event": "Avrupa Savunma Harcamaları Artışı",
            "impact": ["Savunma Hisseleri +15%", "Enerji +5%", "Avro +2%"],
            "duration": "2-3 yıl",
            "status": "Planlanan"
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
                {"date": "2026-01-01", "event": "Yeni Yıl", "impact": "Kapalı"},
                {"date": "2026-04-23", "event": "Ulusal Egemenlik Günü", "impact": "Kapalı"},
                {"date": "2026-05-01", "event": "İşçi Bayramı", "impact": "Kapalı"},
                {"date": "2026-07-15", "event": "Demokrasi Günü", "impact": "Kapalı"},
                {"date": "2026-08-30", "event": "Zafer Bayramı", "impact": "Kapalı"},
                {"date": "2026-10-29", "event": "Cumhuriyet Bayramı", "impact": "Kapalı"},
            ]
        }
    }
    
    @staticmethod
    def get_upcoming_holidays(days_ahead=30):
        """Önümüzdeki tatilleri listele"""
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
            "upcoming_holidays": upcoming[:3],
            "recommendation": "Risk pozisyonlarını azalt, likidite sıkıntısı yaşanabilir"
        }


class MacroEventCalendar:
    """Makroekonomik Takvim - Fed, ECB, BOJ Kararları"""
    
    MAJOR_EVENTS_2026 = [
        {
            "date": "2026-01-28",
            "time": "19:00",
            "event": "Fed FOMC Toplantısı (Faiz Kararı)",
            "impact": "Yüksek",
            "expected": "Faiz Değişikliği Yoktur (%2.50-2.75)",
            "sector_impact": ["finans", "teknoloji", "perakende"],
            "asset_impact": {
                "dolar": "Yükseliş",
                "altın": "Düşüş",
                "hisse": "Volatil"
            }
        },
        {
            "date": "2026-02-12",
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
            vix_data = yf.download("^VIX", period="1d", progress=False, timeout=10)
            
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
                "current": 15,
                "level": "Orta (Kaygılı)",
                "impact": "VIX verileri alınamadı",
                "recommendation": "Normal strateji devam",
                "sectors": {"balanced": ["finans", "teknoloji"]}
            }
        
        current = vix["current"]
        
        if current < 12:
            impact = "Çok Düşük - Piyasa Sakin"
            sectors = {"risk_on": ["teknoloji", "perakende", "turizm"]}
            recommendation = "Agresif pozisyonlar alabilirsin"
        elif current < 15:
            impact = "Düşük - Normal"
            sectors = {"balanced": ["finans", "teknoloji", "perakende"]}
            recommendation = "Dengeli portföy tutabilirsin"
        elif current < 20:
            impact = "Orta - Artan Kaygı"
            sectors = {"defensive": ["finans", "gıda", "sağlık"]}
            recommendation = "Defansif pozisyonları artır"
        elif current < 30:
            impact = "Yüksek - Piyasa Paniklemesi"
            sectors = {"defensive": ["gıda", "sağlık", "finans"]}
            recommendation = "Riski minimize et, altın al"
        else:
            impact = "Çok Yüksek - Kriz Ortamı"
            sectors = {"crisis_mode": ["nakit", "altın", "gıda"]}
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
            "positive_sectors": ["enerji", "gıda", "finans"],
            "negative_sectors": ["teknoloji", "perakende"],
            "explanation": "Enflasyon, emtia ve savunma sektörlerini güçlendirir"
        },
        "inflation_down": {
            "positive_sectors": ["teknoloji", "perakende"],
            "negative_sectors": ["enerji"],
            "explanation": "Enflasyon düşüşü, büyüme hisselerini destekler"
        },
        "war_geopolitics": {
            "positive_sectors": ["savunma", "enerji"],
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
                "ISA.IS",  # İş Bankası
                "GARAN.IS",  # Garanti
                "AKBANK.IS"  # Akbank
            ],
            "negative": [
                "TCELL.IS",
                "VESTEL.IS"
            ],
            "explanation": "Altın yükselirse dolar zayıf, finans hisseleri düşer"
        },
        "oil": {
            "positive": [
                "TUPAS.IS",
                "ENKA.IS",
                "AYGAZ.IS"
            ],
            "negative": [
                "FROTO.IS",
                "OTKAR.IS",
                "TCELL.IS"
            ],
            "explanation": "Petrol yükselirse taşım maliyetleri artır"
        },
        "copper": {
            "positive": [
                "ASELS.IS",
                "SISE.IS",
                "ARÇEL.IS"
            ],
            "negative": [],
            "explanation": "Bakır endüstriyel talep göstergesidir"
        },
        "silver": {
            "positive": [
                "ASELS.IS",
                "VESTEL.IS",
                "SISE.IS"
            ],
            "negative": [],
            "explanation": "Gümüş endüstriyel kullanım göstergesidir"
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
                "US sanctions",
                "BRICS",
                "NATO"
            ]
            
            all_news = []
            
            for keyword in keywords:
                url = "https://newsapi.org/v2/everything"
                params = {
                    "q": keyword,
                    "sortBy": "publishedAt",
                    "language": "en",
                    "apiKey": api_key,
                    "pageSize": 3
                }
                
                try:
                    response = requests.get(url, params=params, timeout=10)
                    data = response.json()
                    
                    if data.get("articles"):
                        for article in data["articles"][:1]:
                            all_news.append({
                                "keyword": keyword,
                                "title": article.get("title", ""),
                                "description": article.get("description", "")[:100],
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
    """Tedarik Zinciri Takibi"""
    
    SUPPLY_CHAIN_INDICATORS = {
        "ram_shortage": {
            "status": "normal",
            "indicator_value": 50,
            "impact": {
                "positive_sectors": ["gıda", "finans"],
                "negative_sectors": ["teknoloji", "otomotiv"]
            },
            "explanation": "RAM kıtlığı → Teknoloji maliyetleri artır"
        },
        "chip_shortage": {
            "status": "normal",
            "indicator_value": 45,
            "impact": {
                "positive_sectors": ["finans"],
                "negative_sectors": ["teknoloji", "otomotiv", "telekom"]
            },
            "explanation": "Çip kıtlığı → Otomotiv ve teknoloji etkilenir"
        },
        "shipping_delays": {
            "status": "normal",
            "indicator_value": 40,
            "impact": {
                "positive_sectors": ["gıda"],
                "negative_sectors": ["perakende", "otomotiv"]
            },
            "explanation": "Gemi gecikmesi → Maliyetler artır"
        },
        "energy_crisis": {
            "status": "normal",
            "indicator_value": 55,
            "impact": {
                "positive_sectors": ["enerji"],
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
        overall_score = 0
        
        for indicator, data in SupplyChainMonitor.SUPPLY_CHAIN_INDICATORS.items():
            overall_score += data["indicator_value"]
            
            if data["status"] != "normal":
                overall_impact = "Bozuk"
                
                for pos_sector in data["impact"]["positive_sectors"]:
                    affected_sectors[pos_sector].append(f"✓ {indicator}: {data['explanation']}")
                
                for neg_sector in data["impact"]["negative_sectors"]:
                    affected_sectors[neg_sector].append(f"✗ {indicator}: {data['explanation']}")
        
        overall_score = overall_score / len(SupplyChainMonitor.SUPPLY_CHAIN_INDICATORS)
        
        return {
            "status": overall_impact,
            "overall_score": round(overall_score, 1),
            "affected_sectors": dict(affected_sectors),
            "recommendation": "Tedarik zinciri sorunları var, teknoloji hisselerinden kaçın" if overall_impact == "Bozuk" else "Normal koşullar"
        }


# ═══════════════════════════════════════════════════════════
# Helper Fonksiyonlar
# ═══════════════════════════════════════════════════════════

def calculate_trend(data):
    """Trend hesapla"""
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


def run_advanced_global_analysis():
    """Tüm ileri küresel analizi çalıştır"""
    print("\n" + "="*70)
    print("🔬 İLERİ KÜRESEL PIYASA ANALİZİ")
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
                print(f"   {event['urgency']} {event['date']}: {event['event'][:40]}...")
    
    # 2. VIX Analizi
    print("\n📊 Volatilite İndeksi (VIX)...")
    vix_impact = VIXAnalyzer.analyze_vix_impact()
    if vix_impact:
        result["vix"] = vix_impact
        print(f"✅ VIX: {vix_impact.get('current', 'N/A')} - {vix_impact.get('level', 'N/A')}")
    
    # 3. Tedarik Zinciri
    print("\n🏭 Tedarik Zinciri Takibi...")
    supply_chain = SupplyChainMonitor.analyze_supply_chain()
    if supply_chain:
        result["supply_chain"] = supply_chain
        print(f"✅ {supply_chain['status']} (Skor: {supply_chain['overall_score']}/100)")
    
    # 4. Jeopolitik Haberler
    print("\n📡 Jeopolitik Haberler (NewsAPI)...")
    geo_news = GeopoliticalNewsIntegration.get_geopolitical_news()
    if geo_news:
        result["geopolitical_news"] = geo_news
        print(f"✅ {len(geo_news)} jeopolitik haber bulundu")
    else:
        print("⚠️ Jeopolitik haberler alınamadı")
    
    return result


if __name__ == "__main__":
    print("🌍 KÜRESEL PIYASA ANALİZLERİ BAŞLANIYOR...\n")
    
    # Temel analiz
    global_analysis = run_global_analysis()
    
    # İleri analiz
    advanced_analysis = run_advanced_global_analysis()
    
    print("\n✅ Tüm küresel analizler tamamlandı!")
