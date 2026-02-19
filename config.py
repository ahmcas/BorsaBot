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

# BIST Türkiye Hisseleri (47 adet)
BIST_STOCKS = [
    # Finans
    "GARAN.IS", "ISABANK.IS", "AKBANK.IS", "YKBNK.IS", "PAGB.IS",
    "SEKB.IS", "TCELL.IS", "SISE.IS", "CCOLA.IS", "AEFKS.IS",
    
    # Enerji & Ulaştırma
    "TUPAS.IS", "ARÇEL.IS", "ENKA.IS", "AYGAZ.IS", "SODA.IS",
    "NTTUR.IS", "OTKAR.IS", "FROTO.IS", "VESTEL.IS", "KORDS.IS",
    
    # İnşaat & Gayrimenkul
    "INDS.IS", "TOASO.IS", "ORKA.IS", "ORKIM.IS", "YABNK.IS",
    
    # Perakende & Gıda
    "ULKER.IS", "GRNT.IS", "VAKBN.IS", "PSDTC.IS", "DOHOL.IS",
    
    # Teknoloji & Medya
    "PRIM.IS", "ASELS.IS", "ISMEN.IS", "PARLX.IS", "ENTEL.IS",
    
    # Diğer
    "BIMAS.IS", "EREGL.IS", "TSKB.IS", "ALARK.IS", "NUHCL.IS",
    "GOLTS.IS", "GENIL.IS", "GEREL.IS", "TRNFP.IS"
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
