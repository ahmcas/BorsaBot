# ============================================================
# config.py — Tüm Ayarlar (v4 - KOMPLE FINAL)
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

TURKISH_STOCKS = [
    # Bankalar
    "AKBANK.IS",   # Akbank
    "GARAN.IS",    # Garanti BBVA
    "ISA.IS",      # İş Bankası
    "YBANK.IS",    # Yapı ve Kredi
    "TEBNK.IS",    # TEB Bankası
    "HALKB.IS",    # Halkbank
    "PBANK.IS",    # Pera Bank
    
    # Sigorta
    "DOAS.IS",     # Doğa Sigorta
    "ACSEL.IS",    # Açık Sigorta
    
    # Telekom
    "TCELL.IS",    # Turkcell
    "TTKOM.IS",    # Türk Telekom
    
    # Enerji
    "TUPAS.IS",    # Türkiye Petrol Rafinerileri
    "AKSA.IS",     # Aksa Enerji
    "ENKA.IS",     # Enka
    "AYGAZ.IS",    # Aygaz
    "SODA.IS",     # Soda Sanayii
    "CCHOL.IS",    # Çelebi
    "KRDMD.IS",    # Karadeniz Holding
    
    # Üretim ve Teknoloji
    "ASELS.IS",    # Aselsan
    "SISE.IS",     # Şişecam
    "VESTEL.IS",   # Vestel
    "ARÇEL.IS",    # Arçelik
    "OTKAR.IS",    # Otokar
    "FROTO.IS",    # Ford Otomotiv
    "KORDSA.IS",   # Kordsa
    
    # Gıda ve Perakende
    "ULKER.IS",    # Ülker Bisküvi
    "PENGD.IS",    # Penguen
    "ULUSE.IS",    # Ulusal
    "KOTON.IS",    # Koton
    
    # Gayrimenkul ve İnşaat
    "EKGYO.IS",    # Emlak Konut
    "BLDYR.IS",    # Bilder
    "SRVGY.IS",    # Seren Gayrimenkul
    "RSGYO.IS",    # Resorpia
    "TKFEN.IS",    # TkFen
    "ORMA.IS",     # Orma
    "ARSAN.IS",    # Arsan
    
    # Turizm
    "TRST.IS",     # Türsab
    "NTHOL.IS",    # Net Turizm
    "CARSI.IS",    # Çarşı
    
    # Diğer
    "DYHOL.IS",    # Doğan Holding
    "TLMAN.IS",    # Turk Limanları
    "MERKO.IS",    # Merkez
    "ASMK.IS",     # Asım
    "HATEK.IS",    # Hatek
    "PETKM.IS",    # Petkim
    "KLVT.IS",     # Kültür Yatırım
    "YKBNK.IS",    # YK Bankası
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

# ═══════════════════════════════════════════════════════════
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
# NOTIFICATION AYARLARI
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

# ═══════���═══════════════════════════════════════════════════
# KÜRESEL ANALİZ AYARLARI
# ═══════════════════════════════════════════════════════════

# ABD Dış Borcu
TRACK_US_DEBT = True

# Emtia Fiyatları
TRACK_COMMODITIES = True
TRACK_GOLD = True
TRACK_SILVER = True
TRACK_COPPER = True
TRACK_OIL = True
TRACK_NATURAL_GAS = True

# Emtia Rekorları
TRACK_COMMODITY_RECORDS = True

# Jeopolitik Olaylar
TRACK_GEOPOLITICS = True

# Borsa Tatilleri
TRACK_EXCHANGE_HOLIDAYS = True

# ═══════════════════════════════════════════════════════════
# İLERİ KÜRESEL ANALİZ AYARLARI
# ═══════════════════════════════════════════════════════════

# Makro Ekonomik Takvim
TRACK_MACRO_CALENDAR = True
TRACK_FED_MEETINGS = True
TRACK_ECB_MEETINGS = True
TRACK_BOJ_MEETINGS = True

# VIX Volatilite İndeksi
TRACK_VIX = True

# Sektör Tavsiyesi (Makro + VIX temelli)
ENABLE_SECTOR_RECOMMENDATIONS = True

# ��══════════════════════════════════════════════════════════
# İLERİ ÖZELLİKLER AYARLARI
# ═══════════════════════════════════════════════════════════

# Spesifik Tetikleyici İzleme
ENABLE_SPECIFIC_TRIGGERS = True
TRACK_AI_BOOM = True
TRACK_ENERGY_CRISIS = True
TRACK_GEOPOLITICS_SPECIFIC = True
TRACK_RECESSION = True
TRACK_WAR_PREPARATION = True
TRACK_INTEREST_RATES = True

# Kripto Piyasası İzleme
ENABLE_CRYPTO_ANALYSIS = True
TRACK_BITCOIN = True
TRACK_ETHEREUM = True

# Döviz ve Para Politikası
ENABLE_CURRENCY_ANALYSIS = True
TRACK_USD_STRENGTH = True
TRACK_EUR_USD = True
TRACK_GBP_USD = True
TRACK_JPY_USD = True

# Kurumsal Hareketler
ENABLE_BUYBACK_TRACKING = True
ENABLE_EARNINGS_CALENDAR = True

# Piyasa Genişliği
ENABLE_BREADTH_ANALYSIS = True
TRACK_SP500 = True
TRACK_NASDAQ = True

# ═══════════════════════════════════════════════════════════
# EMAIL TASARIM AYARLARI
# ═══════════════════════════════════════════════════════════

# Email maksimum boyutu (KB)
MAX_EMAIL_SIZE = 50

# Gösterilecek Email bölümleri (True/False)
SHOW_MARKET_MOOD = True
SHOW_GLOBAL_ANALYSIS = True
SHOW_MACRO_CALENDAR = True
SHOW_VIX = True
SHOW_COMMODITIES = True
SHOW_COMMODITY_RECORDS = True
SHOW_GEOPOLITICS = True
SHOW_HOLIDAYS = True
SHOW_TRENDS = True
SHOW_CORRELATIONS = True
SHOW_SPECIFIC_TRIGGERS = True
SHOW_CRYPTO = True
SHOW_CURRENCIES = True
SHOW_BUYBACKS = True
SHOW_EARNINGS = True
SHOW_BREADTH = True
SHOW_RECOMMENDATIONS = True
SHOW_TECHNICAL_INDICATORS = True
SHOW_FIBONACCI = True
SHOW_CHARTS = True
SHOW_SUPPLY_CHAIN = True
SHOW_DISCLAIMER = True

# Bölüm sırası (önem sırasına göre)
SECTION_ORDER = [
    "header",
    "market_mood",
    "global_analysis",
    "macro_events",
    "vix",
    "commodities",
    "commodity_records",
    "geopolitics",
    "holidays",
    "trends",
    "specific_triggers",
    "crypto",
    "currencies",
    "buybacks",
    "earnings",
    "breadth",
    "recommendations",
    "technical_indicators",
    "fibonacci",
    "correlations",
    "supply_chain",
    "charts",
    "disclaimer",
    "footer"
]

# ═══════════════════════════════════════════════════════════
# TEDARIK ZİNCİRİ AYARLARI
# ═══════════════════════════════════════════════════════════

# RAM Kıtlığı Tracking
TRACK_RAM_SHORTAGE = True
RAM_SHORTAGE_STATUS = "normal"  # normal, shortage, excess

# Çip Kıtlığı Tracking
TRACK_CHIP_SHORTAGE = True
CHIP_SHORTAGE_STATUS = "normal"

# Gemi Gecikmesi Tracking
TRACK_SHIPPING_DELAYS = True
SHIPPING_DELAY_STATUS = "normal"

# Enerji Krizi Tracking
TRACK_ENERGY_CRISIS = True
ENERGY_CRISIS_STATUS = "normal"

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

# ═══════════════════════════════════════════════════════════
# HATA KONTROL
# ═══════════════════════════════════════════════════════════

try:
    assert DAILY_RUN_HOUR >= 0 and DAILY_RUN_HOUR <= 23, "Saat 0-23 arasında olmalı"
    assert DAILY_RUN_MINUTE >= 0 and DAILY_RUN_MINUTE <= 59, "Dakika 0-59 arasında olmalı"
    assert LOOKBACK_DAYS > 0, "Günler pozitif olmalı"
    assert FIBONACCI_LOOKBACK > 0, "Fibonacci lookback pozitif olmalı"
    assert MAX_SAME_SECTOR > 0, "Max sektör sayısı pozitif olmalı"
    assert MIN_SCORE_THRESHOLD >= 0 and MIN_SCORE_THRESHOLD <= 100, "Threshold 0-100 arasında olmalı"
except AssertionError as e:
    print(f"{COLOR_ERROR}❌ Config hatası: {e}{COLOR_RESET}")
    exit(1)

# ════════════════════════════════════════════════════��══════
# BAŞARILI BAŞLANGAÇ
# ═══════════════════════════════════════════════════════════

print(f"{COLOR_SUCCESS}✅ Config yüklendi başarıyla{COLOR_RESET}")
print(f"{COLOR_INFO}📊 Analiz edilen hisseler: {len(ALL_STOCKS)}{COLOR_RESET}")
print(f"{COLOR_INFO}⏰ Günlük çalışma saati: {DAILY_RUN_HOUR:02d}:{DAILY_RUN_MINUTE:02d}{COLOR_RESET}")
print(f"{COLOR_INFO}📧 Email gönderici: {MAIL_SENDER}{COLOR_RESET}")

# ═══════════════════════════════════════════════════════════
# AÇIKLAMALAR VE NOTLAR
# ═════════════════════════════════════════════════���═════════

"""
KURULUM TALIMLARI:

1. API Anahtarlarını Al:
   - NewsAPI: https://newsapi.org/register (Ücretsiz)
   - Alpha Vantage: https://www.alphavantage.co (Ücretsiz, 5 çağrı/dk)
   - Polygon.io: https://polygon.io (Ücretsiz)

2. Gmail Kurulumu:
   - 2FA etkinleştir: https://myaccount.google.com/security
   - Uygulama Şifresi oluştur: https://myaccount.google.com/apppasswords
   - MAIL_SENDER ve MAIL_PASSWORD ortam değişkenlerine ekle

3. Ortam Değişkenleri Ayarla (.env dosyası):
   NEWS_API_KEY=xxxxx
   ALPHA_VANTAGE_KEY=xxxxx
   MAIL_SENDER=your_email@gmail.com
   MAIL_PASSWORD=your_app_password
   MAIL_RECIPIENT=recipient@gmail.com

4. Çalıştır:
   python main_bot.py once      # Tek seferlik test
   python main_bot.py            # Scheduler modu

ÖZELLİKLER:

Teknik Analiz:
✅ RSI, MACD, Bollinger Bands, SMA, Fibonacci, Momentum

Temel Analiz:
✅ Haber Sentiment, Sektor Analizi, Makro Olaylar

Küresel Analiz:
✅ ABD Borcu, Emtia, Jeopolitik, Borsa Tatilleri
✅ Makro Ekonomik Takvim, VIX, Sektör Tavsiyesi

İleri Özellikler:
✅ Spesifik Tetikleyiciler (AI, Savunma, Enerji)
✅ Kripto Analizi, Döviz Kurları, Buyback Programları
✅ Kazanç Takvimi, Piyasa Genişliği

Email:
✅ Profesyonel HTML tasarım
✅ Responsive grid layout
✅ Detaylı analiz ve göstergeler
✅ Grafik entegrasyonu

Veritabanı:
✅ Performans takibi
✅ Tarihsel veri depolama
✅ Kazanç raporu

AYARLAMALAR:

Hisse Ekleme/Çıkarma:
- TURKISH_STOCKS ve GLOBAL_STOCKS listelerini düzenle

Analiz Sıklığı:
- DAILY_RUN_HOUR ve DAILY_RUN_MINUTE değiştir

Email Bölümleri:
- SHOW_* ayarlarını True/False yap

Teknik Göstergeler:
- RSI_PERIOD, MACD_*, BOLLINGER_*, SMA_* değerleri değiştir

Skor Ağırlıkları:
- WEIGHT_* değerlerini güncelle (toplam 100 olmalı)

Veritabanı:
- DATABASE_FILE ve ENABLE_DATABASE ayarla

Log Ayarları:
- LOG_FILE ve LOG_LEVEL düzenle

SORUN GİDERME:

Email göndermiyor?
→ MAIL_SENDER, MAIL_PASSWORD, MAIL_RECIPIENT kontrol et
→ Gmail'de 2FA aktif mı?
→ Uygulama şifresi doğru mu?

Veri çekmiyor?
→ API anahtarları doğru mu?
→ İnternet bağlantısı var mı?
→ Rate limits'e ulaştın mı?

Analiz çalışmıyor?
→ Config.py hataları kontrol et
→ Log dosyasını oku
→ VERBOSE = True yap, debug mod etkinleştir

GÜVENLİK NOTU:

- API anahtarlarını .env dosyasına koy
- GitHub'a commit etme!
- MAIL_PASSWORD hassas bilgidir
- Ortam değişkenlerini kullan: os.environ.get()

LİSANS:

Bu bot yatırım tavsiyesi DEĞİLDİR.
Tüm kararlarınızı profesyonel danışmanlık ile alın.
"""
