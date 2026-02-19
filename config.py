# ============================================================
# config.py — Konfigürasyon Dosyası (v4 - KOMPLE FINAL)
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
LOOKBACK_DAYS = 200

# RSI parametreleri
RSI_PERIOD = 14
RSI_OVERSOLD = 30
RSI_OVERBOUGHT = 70

# MACD parametreleri
MACD_FAST = 12
MACD_SLOW = 26
MACD_SIGNAL = 9

# Bollinger Bands parametreleri
BOLLINGER_PERIOD = 20
BOLLINGER_STD_DEV = 2.0

# SMA parametreleri
SMA_SHORT = 20
SMA_LONG = 50

# Fibonacci seviyeleri
FIBONACCI_LEVELS = [0.236, 0.382, 0.5, 0.618, 0.786]
FIBONACCI_LOOKBACK = 60

# ═══════════════════════════════════════════════════════════
# SKOR AYARLARI
# ═══════════════════════════════════════════════════════════

# Minimum alım sinyali skoru (0-100)
MIN_BUY_SCORE = 65

# Maksimum satış sinyali skoru (0-100)
MAX_SELL_SCORE = 35

# Nötr aralığı
NEUTRAL_SCORE_MIN = 45
NEUTRAL_SCORE_MAX = 55

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
    print(f"  - RSI: {RSI_PERIOD}")
    print(f"  - MACD: {MACD_FAST}/{MACD_SLOW}/{MACD_SIGNAL}")
    print(f"  - Bollinger: {BOLLINGER_PERIOD}/{BOLLINGER_STD_DEV}")
    
    print(f"\n📧 Email ayarları:")
    print(f"  - Gönderici: {MAIL_SENDER}")
    print(f"  - Alıcı: {MAIL_RECIPIENT}")
    print(f"  - SMTP: {SMTP_SERVER}:{SMTP_PORT}")
