# ============================================================
# config.py — Konfigürasyon Dosyası (v5 - SWING TRADE UPDATE)
# ============================================================
# Tüm ayarlar burada (API anahtarları, parametreler, hisseler)
# ============================================================

import os
from dotenv import load_dotenv

# .env dosyasını yükle
load_dotenv()

# ═══════════════════════════════════════════════════════════
# API ANAHTARLARI (Environment Variables)
# ═══════════════════════════════════════════════════════════

NEWS_API_KEY = os.getenv("NEWS_API_KEY", "YOUR_NEWS_API_KEY_HERE")
ALPHA_VANTAGE_KEY = os.getenv("ALPHA_VANTAGE_KEY", "")
POLYGON_API_KEY = os.getenv("POLYGON_API_KEY", "")

# ═══════════════════════════════════════════════════════════
# EMAIL AYARLARI (Gmail SMTP)
# ═══════════════════════════════════════════════════════════

MAIL_SENDER = os.getenv("MAIL_SENDER", "your_email@gmail.com")
MAIL_PASSWORD = os.getenv("MAIL_PASSWORD", "YOUR_APP_PASSWORD_HERE")
MAIL_RECIPIENT = os.getenv("MAIL_RECIPIENT", "recipient@gmail.com")

# SMTP Sunucusu
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

# ═══════════════════════════════════════════════════════════
# BOT AYARLARI
# ═══════════════════════════════════════════════════════════

# Zamanlanmış çalışma saati
DAILY_RUN_HOUR = 9
DAILY_RUN_MINUTE = 30

# Verbose mode (tüm detayları yazsın mı?)
VERBOSE = True

# ═══════════════════════════════════════════════════════════
# TEKNİK ANALİZ PARAMETRELERİ
# ═══════════════════════════════════════════════════════════

# Veri alınacak dönem (gün cinsinden)
LOOKBACK_DAYS = 250

# RSI parametreleri
RSI_PERIOD = 21
RSI_OVERSOLD = 35
RSI_OVERBOUGHT = 65

# MACD parametreleri
MACD_FAST = 12
MACD_SLOW = 26
MACD_SIGNAL = 9

# Bollinger Bands parametreleri
BOLLINGER_PERIOD = 21
BOLLINGER_STD_DEV = 2.0

# SMA parametreleri (1 aylık = 21 iş günü, 3 aylık = 63 iş günü)
SMA_SHORT = 21
SMA_LONG = 63

# Fibonacci seviyeleri
FIBONACCI_LEVELS = [0.236, 0.382, 0.5, 0.618, 0.786]
FIBONACCI_LOOKBACK = 90

# Momentum parametresi (1 aylık)
MOMENTUM_PERIOD = 21

# Minimum Reward/Risk oranı
MIN_REWARD_RISK = 0.8

# ═══════════════════════════════════════════════════════════
# SKOR AYARLARI
# ═══════════════════════════════════════════════════════════

# Minimum alım sinyali skoru (0-100)
MIN_BUY_SCORE = 55

# Maksimum satış sinyali skoru (0-100)
MAX_SELL_SCORE = 35

# Nötr aralığı
NEUTRAL_SCORE_MIN = 45
NEUTRAL_SCORE_MAX = 55

# Maksimum öneri sayısı
MAX_RECOMMENDATIONS = 3

# ═══════════════════════════════════════════════════════════
# HİSSE LİSTESİ (BIST & GLOBAL)
# ═══════════════════════════════════════════════════════════

# BIST Türkiye Hisseleri (48 adet)
BIST_STOCKS = [
    # Finans
    "GARAN.IS", "ISCTR.IS", "AKBNK.IS", "YKBNK.IS", "VAKBN.IS",
    "TSKB.IS", "SAHOL.IS", "KCHOL.IS", "AGHOL.IS", "ISMEN.IS",

    # Enerji & Petrokimya
    "TUPRS.IS", "PETKM.IS", "ENKAI.IS", "AYGAZ.IS", "SODA.IS",
    "ODAS.IS", "TTKOM.IS",

    # Sanayi & Otomotiv
    "FROTO.IS", "TOASO.IS", "KORDS.IS", "OTKAR.IS", "VESTL.IS",
    "ARCLK.IS",

    # İnşaat & Gayrimenkul
    "INDS.IS", "EKGYO.IS", "KONTR.IS", "KRDMD.IS",

    # Perakende & Gıda
    "ULKER.IS", "BIMAS.IS", "MGROS.IS", "DOHOL.IS", "SOKM.IS",

    # Teknoloji & Savunma
    "ASELS.IS", "SISE.IS", "CCOLA.IS", "CIMSA.IS",

    # Ulaştırma & Turizm
    "THYAO.IS", "TCELL.IS", "TAVHL.IS", "PGSUS.IS", "ALARK.IS",

    # Madencilik & Kimya
    "EREGL.IS", "KOZAL.IS", "KOZAA.IS", "NUHCL.IS",
    "HEKTS.IS", "SASA.IS", "GUBRF.IS",
]

# Global Hisseler (45 adet)
GLOBAL_STOCKS = [
    # Teknoloji (Mega Cap)
    "AAPL", "MSFT", "NVDA", "GOOGL", "META",
    
    # Teknoloji (Large Cap)
    "TSLA", "AVGO", "AMD", "ASML", "MU",
    
    # Finans (Large Cap)
    "JPM", "BAC", "WFC", "GS", "MS",
    
    # Enerji
    "XOM", "CVX", "COP", "SLB", "EOG",
    
    # Sağlık & Pharma
    "JNJ", "UNH", "PFE", "AZN", "LLY",
    
    # Ticaret & Perakende
    "WMT", "AMZN", "HD", "NKE", "MCD",
    
    # Telekomünikasyon
    "VZ", "T", "TMUS", "CMCSA", "CHTR",
    
    # Otomotiv
    "TM", "HMC", "BMW", "VWAGY", "GELYF",
    
    # İndeks
    "SPY", "QQQ", "IWM", "EEM"
]

# Tüm Hisseler
ALL_STOCKS = BIST_STOCKS + GLOBAL_STOCKS

# ═══════════════════════════════════════════════════════════
# EMTİA LİSTESİ
# ═══════════════════════════════════════════════════════════

COMMODITIES = {
    "Altın": "GC=F",
    "Gümüş": "SI=F",
    "Bakır": "HG=F",
    "Ham Petrol (WTI)": "CL=F",
    "Brent Petrol": "BZ=F",
    "Doğalgaz": "NG=F",
    "Platin": "PL=F",
    "Paladyum": "PA=F",
}

# ═══════════════════════════════════════════════════════════
# BORSA TATİL TAKVİMİ 2026
# ═══════════════════════════════════════════════════════════

MARKET_HOLIDAYS_2026 = {
    "SSE Shanghai": [
        {"name": "Çin Yeni Yılı", "start": "2026-02-16", "end": "2026-02-23", "impact": "high"},
        {"name": "İşçi Bayramı", "start": "2026-05-01", "end": "2026-05-05", "impact": "medium"},
        {"name": "Ulusal Gün", "start": "2026-10-01", "end": "2026-10-07", "impact": "high"},
    ],
    "HKEX Hong Kong": [
        {"name": "Ay Yeni Yılı", "start": "2026-02-17", "end": "2026-02-19", "impact": "high"},
        {"name": "Paskalya", "start": "2026-04-03", "end": "2026-04-07", "impact": "medium"},
    ],
    "TSE Tokyo": [
        {"name": "Yeni Yıl", "start": "2026-01-01", "end": "2026-01-05", "impact": "medium"},
        {"name": "Altın Hafta", "start": "2026-04-29", "end": "2026-05-06", "impact": "high"},
    ],
    "NYSE/NASDAQ": [
        {"name": "Memorial Day", "start": "2026-05-25", "end": "2026-05-25", "impact": "low"},
        {"name": "Bağımsızlık Günü", "start": "2026-07-03", "end": "2026-07-03", "impact": "low"},
        {"name": "Thanksgiving", "start": "2026-11-26", "end": "2026-11-27", "impact": "medium"},
    ],
}

# ═══════════════════════════════════════════════════════════
# JEOPOLİTİK ANAHTAR KELİMELER
# ═══════════════════════════════════════════════════════════

GEOPOLITICAL_KEYWORDS = [
    "war", "conflict", "sanctions", "tariff", "trade war",
    "NATO", "military", "invasion", "nuclear", "embargo",
    "coup", "protest", "crisis", "tension", "missile",
]

SUPPLY_DEMAND_KEYWORDS = {
    "shortage": {"impact": "bullish", "sectors": ["teknoloji", "enerji"]},
    "supply chain": {"impact": "mixed", "sectors": ["otomotiv", "teknoloji"]},
    "record demand": {"impact": "bullish", "sectors": ["enerji", "teknoloji"]},
    "surplus": {"impact": "bearish", "sectors": ["enerji"]},
    "chip shortage": {"impact": "bullish", "sectors": ["teknoloji"]},
    "oil crisis": {"impact": "bullish", "sectors": ["enerji"]},
    "ram shortage": {"impact": "bullish", "sectors": ["teknoloji"]},
    "ev demand": {"impact": "bullish", "sectors": ["otomotiv"]},
    "gold record": {"impact": "bullish", "sectors": ["madencilik"]},
}

# ═══════════════════════════════════════════════════════════
# EMTİA REKOR BAĞLAM BİLGİ BANKASI
# ═══════════════════════════════════════════════════════════

COMMODITY_RECORD_CONTEXT = {
    "GC=F": {
        "name": "Altın",
        "record_meaning": "Riskten kaçış, enflasyon korkusu, merkez bankası alımları",
        "affected_sectors": ["madencilik", "finans"],
        "historical_impact": "Altın rekor kırdığında genelde hisse piyasaları baskı altına girer, güvenli liman talebi artar",
    },
    "SI=F": {
        "name": "Gümüş",
        "record_meaning": "Sanayi talebi + yatırım talebi, solar panel üretimi artışı",
        "affected_sectors": ["teknoloji", "enerji", "madencilik"],
        "historical_impact": "Gümüş rekoru sanayi canlanmasının ve yeşil enerji yatırımlarının habercisi olabilir",
    },
    "HG=F": {
        "name": "Bakır",
        "record_meaning": "Küresel ekonomik canlanma, inşaat ve altyapı yatırımları",
        "affected_sectors": ["inşaat_gayrimenkul", "enerji", "madencilik"],
        "historical_impact": "Bakır 'Dr. Copper' olarak bilinir — ekonominin sağlık göstergesi, rekor küresel büyüme sinyali",
    },
    "CL=F": {
        "name": "Ham Petrol",
        "record_meaning": "Arz kısıntısı, jeopolitik gerilim, talep artışı",
        "affected_sectors": ["enerji", "ulaştırma"],
        "historical_impact": "Petrol rekoru enflasyonu tetikler, merkez bankalarını faiz artışına zorlar, tüketici harcamalarını kısar",
    },
    "BZ=F": {
        "name": "Brent Petrol",
        "record_meaning": "Global enerji arz-talep dengesi bozulması",
        "affected_sectors": ["enerji", "ulaştırma"],
        "historical_impact": "Brent rekoru Avrupa ve Asya piyasalarını daha fazla etkiler",
    },
    "NG=F": {
        "name": "Doğalgaz",
        "record_meaning": "Kış talebi, LNG ihracat artışı, arz kesintisi",
        "affected_sectors": ["enerji"],
        "historical_impact": "Doğalgaz rekoru enerji maliyetlerini artırır, sanayi üretimini baskılar",
    },
    "PL=F": {
        "name": "Platin",
        "record_meaning": "Otomotiv katalitik konvertör talebi, hidrojen ekonomisi",
        "affected_sectors": ["otomotiv", "madencilik"],
        "historical_impact": "Platin rekoru otomotiv sektörü canlanması ve yeşil enerji dönüşümüne işaret eder",
    },
    "PA=F": {
        "name": "Paladyum",
        "record_meaning": "Otomotiv talebi, Rusya arz riski",
        "affected_sectors": ["otomotiv", "madencilik"],
        "historical_impact": "Paladyum rekoru genelde Rusya-Batı gerilimi dönemlerinde görülür",
    },
}

# ═══════════════════════════════════════════════════════════
# DXY (DOLAR ENDEKSİ) VE ABD BORÇ
# ═══════════════════════════════════════════════════════════

DXY_TICKER = "DX-Y.NYB"
US_DEBT_TRILLION = 38.8  # Manuel güncelleme veya API ile
US_DEBT_GDP_RATIO = 124  # %

# ═══════════════════════════════════════════════════════════
# SEKTÖR AYARLARI
# ═══════════════════════════════════════════════════════════

PRIMARY_SECTORS = [
    "finans",
    "teknoloji",
    "enerji",
    "sağlık"
]

SECONDARY_SECTORS = [
    "perakende",
    "gıda",
    "telekom",
    "otomotiv",
    "sigortalar",
    "turizm",
    "savunma",
    "inşaat_gayrimenkul"
]

ALL_SECTORS = PRIMARY_SECTORS + SECONDARY_SECTORS

# ═══════════════════════════════════════════════════════════
# SEKTÖR MAPPING (Hisse → Sektör)
# ═══════════════════════════════════════════════════════════

STOCK_SECTORS = {
    # BIST - Finans
    "GARAN.IS": "finans",
    "ISCTR.IS": "finans",
    "AKBNK.IS": "finans",
    "YKBNK.IS": "finans",
    "VAKBN.IS": "finans",
    "TSKB.IS": "finans",
    "SAHOL.IS": "finans",
    "KCHOL.IS": "finans",
    "AGHOL.IS": "finans",
    "ISMEN.IS": "finans",
    # BIST - Enerji & Petrokimya
    "TUPRS.IS": "enerji",
    "PETKM.IS": "enerji",
    "ENKAI.IS": "enerji",
    "AYGAZ.IS": "enerji",
    "SODA.IS": "enerji",
    "ODAS.IS": "enerji",
    "KRDMD.IS": "enerji",
    # BIST - Telekom
    "TTKOM.IS": "telekom",
    "TCELL.IS": "telekom",
    # BIST - Sanayi & Otomotiv
    "FROTO.IS": "otomotiv",
    "TOASO.IS": "otomotiv",
    "KORDS.IS": "otomotiv",
    "OTKAR.IS": "otomotiv",
    "VESTL.IS": "teknoloji",
    "ARCLK.IS": "teknoloji",
    # BIST - İnşaat & Gayrimenkul
    "INDS.IS": "inşaat_gayrimenkul",
    "EKGYO.IS": "inşaat_gayrimenkul",
    "KONTR.IS": "inşaat_gayrimenkul",
    "CIMSA.IS": "inşaat_gayrimenkul",
    "NUHCL.IS": "inşaat_gayrimenkul",
    # BIST - Perakende & Gıda
    "ULKER.IS": "gıda",
    "CCOLA.IS": "gıda",
    "GUBRF.IS": "gıda",
    "BIMAS.IS": "perakende",
    "MGROS.IS": "perakende",
    "SOKM.IS": "perakende",
    "DOHOL.IS": "finans",
    # BIST - Teknoloji & Savunma
    "ASELS.IS": "savunma",
    "SISE.IS": "teknoloji",
    "SASA.IS": "teknoloji",
    "ALARK.IS": "teknoloji",
    "HEKTS.IS": "sağlık",
    # BIST - Ulaştırma & Turizm
    "THYAO.IS": "ulaştırma",
    "TAVHL.IS": "ulaştırma",
    "PGSUS.IS": "ulaştırma",
    # BIST - Madencilik
    "EREGL.IS": "enerji",
    "KOZAL.IS": "madencilik",
    "KOZAA.IS": "madencilik",
    # Global - Teknoloji
    "AAPL": "teknoloji",
    "MSFT": "teknoloji",
    "NVDA": "teknoloji",
    "GOOGL": "teknoloji",
    "META": "teknoloji",
    "TSLA": "otomotiv",
    "AVGO": "teknoloji",
    "AMD": "teknoloji",
    "ASML": "teknoloji",
    "MU": "teknoloji",
    "AMZN": "teknoloji",
    # Global - Finans
    "JPM": "finans",
    "BAC": "finans",
    "WFC": "finans",
    "GS": "finans",
    "MS": "finans",
    # Global - Enerji
    "XOM": "enerji",
    "CVX": "enerji",
    "COP": "enerji",
    "SLB": "enerji",
    "EOG": "enerji",
    # Global - Sağlık
    "JNJ": "sağlık",
    "UNH": "sağlık",
    "PFE": "sağlık",
    "AZN": "sağlık",
    "LLY": "sağlık",
    # Global - Perakende & Gıda
    "WMT": "perakende",
    "HD": "perakende",
    "NKE": "perakende",
    "MCD": "gıda",
    # Global - Telekom
    "VZ": "telekom",
    "T": "telekom",
    "TMUS": "telekom",
    "CMCSA": "telekom",
    "CHTR": "telekom",
    # Global - Otomotiv
    "TM": "otomotiv",
    "HMC": "otomotiv",
    "BMW": "otomotiv",
    "VWAGY": "otomotiv",
    "GELYF": "otomotiv",
    # İndeks
    "SPY": "indeks",
    "QQQ": "indeks",
    "IWM": "indeks",
    "EEM": "indeks",
}

# ═══════════════════════════════════════════════════════════
# VERİTABANI AYARLARI
# ═══════════════════════════════════════════════════════════

DATABASE_FILE = os.getenv("DATABASE_FILE", "performance.db")
ENABLE_DATABASE = os.getenv("ENABLE_DATABASE", "true").lower() == "true"

# ═══════════════════════════════════════════════════════════
# LOG AYARLARI
# ═══════════════════════════════════════════════════════════

LOG_FILE = os.getenv("LOG_FILE", "logs/borsa_bot.log")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Log klasörü oluştur
os.makedirs("logs", exist_ok=True)
os.makedirs("charts", exist_ok=True)

# ═══════════════════════════════════════════════════════════
# PROXY AYARLARI (İsteğe bağlı)
# ═══════════════════════════════════════════════════════════

USE_PROXY = os.getenv("USE_PROXY", "false").lower() == "true"
PROXY_URL = os.getenv("PROXY_URL", "")

PROXIES = None
if USE_PROXY and PROXY_URL:
    PROXIES = {
        "http": PROXY_URL,
        "https": PROXY_URL,
    }

# ═══════════════════════════════════════════════════════════
# VALIDATION
# ═══════════════════════════════════════════════════════════

def validate_config():
    """Konfigürasyon kontrolü"""
    errors = []
    
    # API Keys
    if NEWS_API_KEY == "YOUR_NEWS_API_KEY_HERE":
        errors.append("⚠️  NEWS_API_KEY tanımlanmamış")
    
    # Email
    if MAIL_SENDER == "your_email@gmail.com":
        errors.append("⚠️  MAIL_SENDER tanımlanmamış")
    
    if MAIL_PASSWORD == "YOUR_APP_PASSWORD_HERE":
        errors.append("⚠️  MAIL_PASSWORD tanımlanmamış")
    
    if MAIL_RECIPIENT == "recipient@gmail.com":
        errors.append("⚠️  MAIL_RECIPIENT tanımlanmamış")
    
    # Hisseler
    if not ALL_STOCKS or len(ALL_STOCKS) == 0:
        errors.append("❌ Hiçbir hisse tanımlanmamış")
    
    return errors


# Config kontrolü
if __name__ == "__main__":
    errors = validate_config()
    
    if errors:
        print("🔍 Konfigürasyon Uyarıları:")
        for error in errors:
            print(f"  {error}")
    else:
        print("✅ Konfigürasyon doğru")
    
    print(f"\n📊 Yüklenen hisseler:")
    print(f"  - BIST: {len(BIST_STOCKS)}")
    print(f"  - Global: {len(GLOBAL_STOCKS)}")
    print(f"  - Toplam: {len(ALL_STOCKS)}")
    
    print(f"\n📈 Teknik analiz ayarları:")
    print(f"  - Lookback: {LOOKBACK_DAYS} gün")
    print(f"  - RSI: {RSI_PERIOD} (oversold:{RSI_OVERSOLD}, overbought:{RSI_OVERBOUGHT})")
    print(f"  - MACD: {MACD_FAST}/{MACD_SLOW}/{MACD_SIGNAL}")
    print(f"  - Bollinger: {BOLLINGER_PERIOD}/{BOLLINGER_STD_DEV}")
    print(f"  - SMA: {SMA_SHORT}/{SMA_LONG}")
    print(f"  - Momentum: {MOMENTUM_PERIOD} gün")
    print(f"  - Min Buy Score: {MIN_BUY_SCORE}")
    print(f"  - Min R/R: {MIN_REWARD_RISK}")
    print(f"  - Max Öneriler: {MAX_RECOMMENDATIONS}")
    print(f"  - Emtia sayısı: {len(COMMODITIES)}")
    
    print(f"\n📧 Email ayarları:")
    print(f"  - Gönderici: {MAIL_SENDER}")
    print(f"  - Alıcı: {MAIL_RECIPIENT}")
    print(f"  - SMTP: {SMTP_SERVER}:{SMTP_PORT}")
