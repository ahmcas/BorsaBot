# ============================================================
# config.py — Tüm ayarlar burada
# ============================================================
# Bu dosyada API anahtarlarını ve tüm konfigurasyonu düzenleyin.
# ============================================================

import os

# ═══════════════════════════════════════════════════════════
# API ANAHTARLARI
# ═══════════════════════════════════════════════════════════

# NewsAPI - Haber analizi için
# Ücretsiz anahtar: https://newsapi.org/register
# Ücretsiz plan: 100 çağrı/gün (yeterli)
NEWS_API_KEY = os.environ.get("NEWS_API_KEY", "YOUR_NEWS_API_KEY_HERE")

# Alpha Vantage - Teknik veriler için (isteğe bağlı)
# Ücretsiz anahtar: https://www.alphavantage.co/support/#api-key
# Ücretsiz plan: 5 çağrı/dakika
ALPHA_VANTAGE_KEY = os.environ.get("ALPHA_VANTAGE_KEY", "YOUR_ALPHA_VANTAGE_KEY_HERE")

# IEX Cloud - Global hisseler için (built-in public key)
# Public test key varsayılan olarak kullanılıyor
IEX_API_KEY = os.environ.get("IEX_API_KEY", "pk_test8aac109e59f84982a89a6f2ca628d7e0")

# Polygon.io - Global hisseler için (isteğe bağlı)
# Ücretsiz anahtar: https://polygon.io
POLYGON_API_KEY = os.environ.get("POLYGON_API_KEY", "YOUR_POLYGON_API_KEY_HERE")

# ═══════════════════════════════════════════════════════════
# MAIL AYARLARI (Gmail SMTP)
# ═══════════════════════════════════════════════════════════

# Gmail gönderici adresi
MAIL_SENDER = os.environ.get("MAIL_SENDER", "your_email@gmail.com")

# Gmail Uygulama Şifresi (normal şifre DEĞİL!)
# Oluştur: https://myaccount.google.com/apppasswords
# (Gmail'de 2FA açık olmalı)
MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD", "YOUR_APP_PASSWORD_HERE")

# Email alıcı adresi (kendiniz olabilir)
MAIL_RECIPIENT = os.environ.get("MAIL_RECIPIENT", "recipient@gmail.com")

# ═══════════════════════════════════════════════════════════
# BIST 100 - TÜRKIYE BORSA HİSSELERİ
# ═══════════════════════════════════════════════════════════
# Çoklu kaynaklardan veri alabilir
# Kaynak sırası: Yahoo Finance → Alpha Vantage → IEX → Polygon

TURKISH_STOCKS = [
    # Top 10 - En Büyük Hisseler
    "AKBANK.IS",   # Akbank
    "GARAN.IS",    # Garanti BBVA
    "ISA.IS",      # İş Bankası
    "YBANK.IS",    # Yapı ve Kredi
    "TCELL.IS",    # Turkcell
    "TTKOM.IS",    # Türk Telekom
    "ASELS.IS",    # Aselsan
    "SISE.IS",     # Şişecam
    "TUPAS.IS",    # Türkiye Petrol
    "ARÇEL.IS",    # Arçelik

    # 11-20: Büyük Hisseler
    "ENKA.IS",     # Enka
    "EKGYO.IS",    # Emlak Konut
    "VESTEL.IS",   # Vestel
    "ULKER.IS",    # Ülker
    "TOASY.IS",    # Toasan
    "PETKM.IS",    # Petkim
    "BLDYR.IS",    # Bilder
    "AYGAZ.IS",    # Aygaz
    "KORDSA.IS",   # Kordsa
    "OTKAR.IS",    # Otokar

    # 21-30: Orta Büyüklük
    "AKSA.IS",     # Aksa Enerji
    "FROTO.IS",    # Ford Otomotiv
    "TEBNK.IS",    # TEB Bank
    "HALKB.IS",    # Halkbank
    "DOAS.IS",     # Doğa Sigorta
    "PENGD.IS",    # Penguen
    "SODA.IS",     # Soda Sanayii
    "RSGYO.IS",    # Resorpia
    "ORMA.IS",     # Orma
    "TRST.IS",     # Türsab

    # 31-40: Orta Küçüklük
    "PBANK.IS",    # Pera Bank
    "ACSEL.IS",    # Açık Sigorta
    "CCHOL.IS",    # Çelebi
    "KRDMD.IS",    # Karadeniz
    "TLMAN.IS",    # Turk Limanları
    "DYHOL.IS",    # Doğan Holding
    "TKFEN.IS",    # TkFen
    "KOTON.IS",    # Koton
    "NTHOL.IS",    # Net Turizm
    "CARSI.IS",    # Çarşı

    # 41-50: Küçük Hisseler
    "MERKO.IS",    # Merkez
    "ULUSE.IS",    # Ulusal
    "KAYNK.IS",    # Kaynak
    "LCDHO.IS",    # Leçar
    "GOLTS.IS",    # Goldaş
    "HMROL.IS",    # Hamrolı
    "MRSB.IS",     # Marsan
    "ARSAN.IS",    # Arsan
    "YAPI.IS",     # Yapı
    "ASMK.IS",     # Asım

    # 51+ : En Küçük Hisseler
    "KLVT.IS",     # Kültür Yatırım
    "YKBNK.IS",    # YK Bankası
    "BANVT.IS",    # Banvit
    "FICOH.IS",    # Ficohsa
    "BNTAS.IS",    # Bürokrat
    "INDAG.IS",    # İnda
    "OZKGY.IS",    # Özak Gayrimenkul
    "YAPRK.IS",    # Yapıkredi Konut
    "INSGYO.IS",   # İnş Gayrimenkul
    "ARYAP.IS",    # Ar Yapı
    "KRGYO.IS",    # Karma
    "SRVGY.IS",    # Seren
    "KORDS.IS",    # Kordindir
    "IPEKE.IS",    # İpek Enerji
    "HATEK.IS",    # Hatek
    "TAVHL.IS",    # Tavahlı
    "ENJSA.IS",    # Enerjisa
    "EGEEN.IS",    # Egeen Enerji
    "GEMIN.IS",    # Gemin
    "PETKE.IS",    # Petkim
    "EGLET.IS",    # Egeli
    "ARBOS.IS",    # Arbos
    "NTTUR.IS",    # Turtur
    "MARTI.IS",    # Martı
    "KNC.IS",      # Konç
    "KSTUR.IS",    # Ksu
    "BJKAS.IS",    # Bilmece
    "ARENA.IS",    # Arena
    "BAGFS.IS",    # Bagfas
    "ALBRK.IS",    # Albayrak
    "TURSH.IS",    # Türsüz
    "HERTT.IS",    # Hertz
    "TRTUR.IS",    # Turtur
    "HAPPF.IS",    # Happy
    "PLAVT.IS",    # Plavaton
    "SEFKR.IS",    # Sefkirin
    "TKFYE.IS",    # Takfiye
    "DIFSH.IS",    # Difesh
]

# ═══════════════════════════════════════════════════════════
# GLOBAL TOP 50 HİSSELER (S&P 500 / NASDAQ)
# ═══════════════════════════════════════════════════════════

GLOBAL_STOCKS = [
    # Mega Cap Teknoloji (10)
    "AAPL",        # Apple
    "MSFT",        # Microsoft
    "GOOGL",       # Google
    "AMZN",        # Amazon
    "META",        # Meta (Facebook)
    "NVDA",        # Nvidia
    "TSLA",        # Tesla
    "NFLX",        # Netflix
    "CRM",         # Salesforce
    "ADBE",        # Adobe

    # Finans & Bankacılık (10)
    "JPM",         # JPMorgan Chase
    "BAC",         # Bank of America
    "WFC",         # Wells Fargo
    "MS",          # Morgan Stanley
    "GS",          # Goldman Sachs
    "V",           # Visa
    "MA",          # Mastercard
    "AXP",         # American Express
    "BLK",         # BlackRock
    "SCHW",        # Charles Schwab

    # Enerji (5)
    "XOM",         # Exxon Mobil
    "CVX",         # Chevron
    "COP",         # ConocoPhillips
    "MPC",         # Marathon Petroleum
    "PSX",         # Phillips 66

    # Sağlık & İlaç (8)
    "UNH",         # UnitedHealth
    "JNJ",         # Johnson & Johnson
    "PFE",         # Pfizer
    "ABBV",        # AbbVie
    "MRK",         # Merck
    "LLY",         # Eli Lilly
    "TMO",         # Thermo Fisher
    "AMGN",        # Amgen

    # Tüketim & Perakende (7)
    "WMT",         # Walmart
    "KO",          # Coca-Cola
    "PEP",         # PepsiCo
    "MCD",         # McDonald's
    "NKE",         # Nike
    "COST",        # Costco
    "HD",          # Home Depot

    # Diğer (Teknoloji, Telekomünikasyon, vb)
    "AVGO",        # Broadcom
    "QCOM",        # Qualcomm
    "CSCO",        # Cisco
    "ORCL",        # Oracle
    "IBM",         # IBM
]

# ═══════════════════════════════════════════════════════════
# TÜM HİSSELER (BIST + GLOBAL)
# ═══════════════════════════════════════════════════════════

ALL_STOCKS = TURKISH_STOCKS + GLOBAL_STOCKS

print(f"✅ Toplam hisse sayısı: {len(ALL_STOCKS)}")
print(f"   - BIST Türkiye: {len(TURKISH_STOCKS)}")
print(f"   - Global: {len(GLOBAL_STOCKS)}")

# ═══════════════════════════════════════════════════════════
# TEKNİK ANALİZ PARAMETRELERI
# ═══════════════════════════════════════════════════════════

# Fibonacci Seviyeleri (% olarak)
FIBONACCI_LEVELS = [0.236, 0.382, 0.500, 0.618, 0.786]

# RSI (Relative Strength Index)
RSI_PERIOD = 14

# MACD (Moving Average Convergence Divergence)
MACD_FAST = 12
MACD_SLOW = 26
MACD_SIGNAL = 9

# Bollinger Bands
BOLLINGER_PERIOD = 20
BOLLINGER_STD_DEV = 2.0

# Simple Moving Averages
SMA_SHORT = 20    # Kısa dönem
SMA_LONG = 50     # Uzun dönem

# ═══════════════════════════════════════════════════════════
# SKOR HESAPLAMA AĞIRLIKLARI
# ═══════════════════════════════════════════════════════════
# Toplam = 100 olmalı

WEIGHT_TECHNICAL = 40       # Teknik analiz ağırlığı
WEIGHT_FUNDAMENTAL = 30     # Temel analiz ağırlığı (proxy)
WEIGHT_NEWS_SENTIMENT = 20  # Haber sentiment ağırlığı
WEIGHT_MOMENTUM = 10        # Momentum ağırlığı

# Kontrol et
assert (WEIGHT_TECHNICAL + WEIGHT_FUNDAMENTAL + 
        WEIGHT_NEWS_SENTIMENT + WEIGHT_MOMENTUM == 100), \
    "Ağırlıkların toplamı 100 olmalı!"

# ═══════════════════════════════════════════════════════════
# ZAMANLAMA AYARLARI
# ═══════════════════════════════════════════════════════════

# Her gün çalışma saati (24 saat format)
DAILY_RUN_HOUR = 9       # Saat
DAILY_RUN_MINUTE = 30    # Dakika
# Türkiye saati: 09:30 (UTC+3)
# UTC: 06:30

# Pazartesi-Cuma'da çalış (Hafta sonu kapalı)
RUN_ON_WEEKDAYS = True   # Pazartesi=0, Cumartesi=5, Pazar=6

# ═══════════════════════════════════════════════════════════
# VERİ ÇEKME AYARLARI
# ═══════════════════════════════════════════════════════════

# Geçmiş veriler kaç günlük olsun
LOOKBACK_DAYS = 200      # Son 200 günlük veriler

# Fibonacci hesaplaması için backtrack
FIBONACCI_LOOKBACK = 60  # Son 60 günde high/low bul

# ═══════════════════════════════════════════════════════════
# EMAIL AYARLARI (Gmail SMTP)
# ═══════════════════════════════════════════════════════════

# SMTP Sunucusu
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

# Email Konu
EMAIL_SUBJECT_TEMPLATE = "📊 Borsa Analiz - {date}"

# HTML Email mi yoksa Plain Text mi
USE_HTML_EMAIL = True

# ═══════════════════════════════════════════════════════════
# PERFORMANS TAKIP AYARLARI
# ═══════════════════════════════════════════════════════════

# Performans kontrolü için gün sayıları
PERFORMANCE_CHECK_DAYS = [7, 14, 30]  # 7, 14, 30 gün sonra kontrol et

# Başarı kriteri (% kazanç)
SUCCESS_THRESHOLD = 5.0  # %5 ve üzeri başarı

# Neutral bölge (% kazanç arası)
NEUTRAL_THRESHOLD = 0.0  # 0% - 5% arası neutral

# ═══════════════════════════════════════════════════════════
# GRAFİK AYARLARI
# ═══════════════════════════════════════════════════════════

# Grafik klasörü
CHART_DIR = "charts"

# DPI (kalite)
CHART_DPI = 150

# Figsize
CHART_WIDTH = 14
CHART_HEIGHT = 10

# ═══════════════════════════════════════════════════════════
# SEKTÖR AYARLARI
# ═══════════════════════════════════════════════════════════

# Aynı sektörden max hisse sayısı (diversifikasyon)
MAX_SAME_SECTOR = 1

# Minimum skor threshold (altında olan seçilmez)
MIN_SCORE_THRESHOLD = 50

# ═══════════════════════════════════════════════════════════
# LOG AYARLARI
# ═══════════════════════════════════════════════════════════

# Log dosyası
LOG_FILE = "borsa_bot.log"

# Log seviyesi: DEBUG, INFO, WARNING, ERROR
LOG_LEVEL = "INFO"

# ═══════════════════════════════════════════════════════════
# YAZICI AYARI (Debug)
# ═══════════════════════════════════════════════════════════

# Verbose mode (tüm detayları göster)
VERBOSE = True

# Hızlı test için sadece 2 hisse
QUICK_TEST_MODE = False
QUICK_TEST_STOCKS = ["AKBANK.IS", "AAPL"]

# ═════════���═════════════════════════════════════════════════
# RENKLER & STİL
# ═══════════════════════════════════════════════════════════

# Terminal renkleri
COLOR_SUCCESS = "\033[92m"    # Yeşil
COLOR_WARNING = "\033[93m"    # Sarı
COLOR_ERROR = "\033[91m"      # Kırmızı
COLOR_INFO = "\033[94m"       # Mavi
COLOR_RESET = "\033[0m"       # Normal

# ═══════════════════════════════════════════════════════════
# ADVANCED SETTINGS
# ═══════════════════════════════════════════════════════════

# Timeout değerleri (saniye)
API_TIMEOUT = 30
SMTP_TIMEOUT = 30

# Retry sayısı (başarısız olursa kaç kere tekrar denesini)
MAX_RETRIES = 2

# Rate limiting (saniye/istek)
API_RATE_LIMIT = 0.5

# Paralel işlem (concurrent requests)
CONCURRENT_REQUESTS = 5

# ═══════════════════════════════════════════════════════════
# NOTIFICATION AYARLARI (Future)
# ═══════════════════════════════════════════════════════════

# Push notification (Pushover, Slack, vb)
ENABLE_NOTIFICATIONS = False
NOTIFICATION_SERVICE = "email"  # email, pushover, slack, telegram

# ═══════════════════════════════════════════════════════════
# BACKUP & STORAGE
# ═══════════════════════════════════════════════════════════

# Veritabanı dosyası
DATABASE_FILE = "performance.db"

# Veritabanını gözlemle
ENABLE_DATABASE = True

# ═══════════════════════════════════════════════════════════
# VERIFICATION
# ═══════════════════════════════════════════════════════════

# Başlangış kontrolleri yap
if not NEWS_API_KEY or NEWS_API_KEY == "YOUR_NEWS_API_KEY_HERE":
    print(f"{COLOR_WARNING}⚠️  NewsAPI anahtarı tanımlanmamış{COLOR_RESET}")

if not MAIL_PASSWORD or MAIL_PASSWORD == "YOUR_APP_PASSWORD_HERE":
    print(f"{COLOR_WARNING}⚠️  Email şifresi tanımlanmamış{COLOR_RESET}")

if not MAIL_SENDER or MAIL_SENDER == "your_email@gmail.com":
    print(f"{COLOR_WARNING}⚠️  Email gönderici adresi tanımlanmamış{COLOR_RESET}")

print(f"{COLOR_INFO}✅ Config yüklendi{COLOR_RESET}")
