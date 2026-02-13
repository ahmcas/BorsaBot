# ============================================================
# config.py — Tüm ayarlar burada
# ============================================================
# Bu dosyada API anahtarlarını ve mail ayarlarını doldurun.
# ============================================================

import os

# --- API ANAHTARLARI ---
# NewsAPI için ücretsiz anahtar: https://newsapi.org/register
NEWS_API_KEY = os.environ.get("NEWS_API_KEY", "YOUR_NEWS_API_KEY_HERE")

# Alpha Vantage için ücretsiz anahtar: https://www.alphavantage.co/support/#api-key
ALPHA_VANTAGE_KEY = os.environ.get("ALPHA_VANTAGE_KEY", "YOUR_ALPHA_VANTAGE_KEY_HERE")

# --- MAIL AYARLARI (Gmail) ---
# Gmail'de 2FA açıksa → App Password yoluyla yeni şifre oluştur
# https://myaccount.google.com/apppasswords
MAIL_SENDER = os.environ.get("MAIL_SENDER", "senin_gmail_adresin@gmail.com")
MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD", "APP_PASSWORD_BURAYA")
MAIL_RECIPIENT = os.environ.get("MAIL_RECIPIENT", "alici_adres@gmail.com")  # kendin için aynı adres olabilir

# --- BORSALAR & HISSELER ---
# Yahoo Finance ticker formatı:
# Türkiye → XYZ.IS   (örn: AAPL.IS, THYAO.IS)
# ABD     → XYZ      (örn: AAPL, MSFT)
# Almanya → XYZ.DE
# Hindistan → XYZ.NS

TURKISH_STOCKS = [
    TURKISH_STOCKS = [
    "AEFES.IS",  # Anadolu Efes
    "AGHOL.IS",  # Anadolu Grubu Holding
    "AHGAZ.IS",  # Ahlatcı Doğalgaz
    "AKBNK.IS",  # Akbank
    "AKCNS.IS",  # Akçansa Çimento
    "AKFGY.IS",  # Akfen GYO
    "AKSA.IS",   # Aksa Enerji
    "AKSEN.IS",  # Aksa Enerji Üretim
    "ALARK.IS",  # Alarko Holding
    "ALBRK.IS",  # Albaraka Türk
    "ARCLK.IS",  # Arçelik
    "ASELS.IS",  # Aselsan
    "ASTOR.IS",  # Astor Enerji
    "BIMAS.IS",  # BİM
    "BRISA.IS",  # Brisa
    "CCOLA.IS",  # Coca-Cola İçecek
    "CIMSA.IS",  # Çimsa
    "DOAS.IS",   # Doğuş Otomotiv
    "DOHOL.IS",  # Doğan Holding
    "ECILC.IS",  # Eczacıbaşı İlaç
    "EGEEN.IS",  # Ege Endüstri
    "EKGYO.IS",  # Emlak Konut GYO
    "ENJSA.IS",  # Enerjisa
    "ENKAI.IS",  # Enka İnşaat
    "EREGL.IS",  # Ereğli Demir Çelik
    "FROTO.IS",  # Ford Otosan
    "GARAN.IS",  # Garanti BBVA
    "GUBRF.IS",  # Gübretaş
    "HALKB.IS",  # Halkbank
    "HEKTS.IS",  # Hektaş
    "ISCTR.IS",  # İş Bankası C
    "ISDMR.IS",  # İskenderun Demir Çelik
    "KCHOL.IS",  # Koç Holding
    "KOZAA.IS",  # Koza Anadolu
    "KOZAL.IS",  # Koza Altın
    "KRDMD.IS",  # Kardemir D
    "MAVI.IS",   # Mavi Giyim
    "MGROS.IS",  # Migros
    "ODAS.IS",   # Odaş Enerji
    "OTKAR.IS",  # Otokar
    "OYAKC.IS",  # Oyak Çimento
    "PETKM.IS",  # Petkim
    "PGSUS.IS",  # Pegasus
    "SAHOL.IS",  # Sabancı Holding
    "SASA.IS",   # Sasa Polyester
    "SISE.IS",   # Şişecam
    "SOKM.IS",   # Şok Marketler
    "TAVHL.IS",  # TAV Havalimanları
    "TCELL.IS",  # Turkcell
    "THYAO.IS",  # Türk Hava Yolları
    "TKFEN.IS",  # Tekfen Holding
    "TOASO.IS",  # Tofaş
    "TSKB.IS",   # TSKB
    "TTKOM.IS",  # Türk Telekom
    "TTRAK.IS",  # Türk Traktör
    "TUPRS.IS",  # Tüpraş
    "ULKER.IS",  # Ülker
    "VAKBN.IS",  # Vakıfbank
    "VESBE.IS",  # Vestel Beyaz Eşya
    "VESTL.IS",  # Vestel
    "YKBNK.IS",  # Yapı Kredi
    "ZOREN.IS"   # Zorlu Enerji
]

GLOBAL_STOCKS = [
    GLOBAL_STOCKS = [
    "AAPL",   # Apple
    "MSFT",   # Microsoft
    "AMZN",   # Amazon
    "GOOGL",  # Alphabet (Google)
    "NVDA",   # Nvidia
    "META",   # Meta Platforms
    "TSLA",   # Tesla
    "BRK.B",  # Berkshire Hathaway
    "JPM",    # JPMorgan Chase
    "V",      # Visa
    "MA",     # Mastercard
    "UNH",    # UnitedHealth
    "JNJ",    # Johnson & Johnson
    "XOM",    # Exxon Mobil
    "WMT",    # Walmart
    "PG",     # Procter & Gamble
    "HD",     # Home Depot
    "BAC",    # Bank of America
    "CVX",    # Chevron
    "LLY",    # Eli Lilly
    "AVGO",   # Broadcom
    "MRK",    # Merck
    "ABBV",   # AbbVie
    "KO",     # Coca-Cola
    "PEP",    # PepsiCo
    "COST",   # Costco
    "ADBE",   # Adobe
    "CRM",    # Salesforce
    "NFLX",   # Netflix
    "AMD",    # Advanced Micro Devices
    "INTC",   # Intel
    "CSCO",   # Cisco
    "ORCL",   # Oracle
    "QCOM",   # Qualcomm
    "TXN",    # Texas Instruments
    "NKE",    # Nike
    "DIS",    # Disney
    "PFE",    # Pfizer
    "T",      # AT&T
    "VZ",     # Verizon
    "UBER",   # Uber
    "PLTR",   # Palantir
    "SHOP",   # Shopify
    "BABA",   # Alibaba
    "NVO",    # Novo Nordisk
    "ASML",   # ASML Holding
    "TM",     # Toyota
    "SAP",    # SAP
    "SONY",   # Sony
    "BA"      # Boeing
]

ALL_STOCKS = TURKISH_STOCKS + GLOBAL_STOCKS

# --- ANALIZ PARAMETRELERI ---
# Fibonacci seviyeler (yüzde olarak)
FIBONACCI_LEVELS = [0.236, 0.382, 0.500, 0.618, 0.786]

# Teknik indikatör dönemleri
RSI_PERIOD = 14
MACD_FAST = 12
MACD_SLOW = 26
MACD_SIGNAL = 9
BOLLINGER_PERIOD = 20
SMA_SHORT = 20
SMA_LONG = 50

# Skor ağırlıkları (toplam = 100)
WEIGHT_TECHNICAL = 40   # Teknik analiz ağırlığı
WEIGHT_FUNDAMENTAL = 30 # Temel analiz ağırlığı
WEIGHT_NEWS_SENTIMENT = 20 # Haber analiz ağırlığı
WEIGHT_MOMENTUM = 10    # Momentum ağırlığı

# --- ZAMANLAMA ---
# Her gün saat kaç'ta analiz yapılsın (24h format)
DAILY_RUN_HOUR = 9
DAILY_RUN_MINUTE = 30
