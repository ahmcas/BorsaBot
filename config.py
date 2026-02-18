# ============================================================
# config.py — Tüm ayarlar burada
# ============================================================

import os

# --- API ANAHTARLARI ---
NEWS_API_KEY = os.environ.get("NEWS_API_KEY", "YOUR_NEWS_API_KEY_HERE")
ALPHA_VANTAGE_KEY = os.environ.get("ALPHA_VANTAGE_KEY", "YOUR_ALPHA_VANTAGE_KEY_HERE")

# --- MAIL AYARLARI (Gmail) ---
MAIL_SENDER = os.environ.get("MAIL_SENDER", "senin_gmail_adresin@gmail.com")
MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD", "APP_PASSWORD_BURAYA")
MAIL_RECIPIENT = os.environ.get("MAIL_RECIPIENT", "alici_adres@gmail.com")

# ═══════════════════════════════════════════════════════════
# BIST 100 - TÜRKIYE BORSA HISSELERI (100 HISSE)
# ═══════════════════════════════════════════════════════════

TURKISH_STOCKS = [
    # 1-10: Bankalar
    "AKBANK.IS",   # Akbank
    "GARAN.IS",    # Garanti BBVA
    "ISA.IS",      # İş Bankası
    "YBANK.IS",    # Yapı ve Kredi Bank
    "TEBNK.IS",    # TEB Bank
    "HALKB.IS",    # Halkbank
    "PBANK.IS",    # Pera Bank
    "KLVT.IS",     # Kültür Yatırım
    "FICOH.IS",    # Ficohsa
    "BNTAS.IS",    # Bürokrat
    
    # 11-20: Finans & Holding
    "TLMAN.IS",    # Turk Limanları
    "DYHOL.IS",    # Doğan Holding
    "KORDSA.IS",   # Kordsa
    "INDAG.IS",    # İnda
    "DOHOL.IS",    # Doğan Holding Enerji
    "ALBRK.IS",    # Albayrak
    "YKBNK.IS",    # YK Bankası
    "BANVT.IS",    # Banvit
    "BUCIM.IS",    # Buçim
    "ORTAK.IS",    # Ortak
    
    # 21-30: Sigorta
    "DOAS.IS",     # Doğa Sigorta
    "ACSEL.IS",    # Açık Sigorta
    "ANELE.IS",    # Anele
    "TRWF.IS",     # Turkcell Vodafone
    "OZKGY.IS",    # Özak Gayrimenkul
    "ARENA.IS",    # Arena Medya
    "BAGFS.IS",    # Bagfas
    "ATATP.IS",    # Ataturk
    "ADHA.IS",     # Adha
    "ALTIN.IS",    # Altın Yönetim
    
    # 31-40: Telekomunikasyon
    "TCELL.IS",    # Turkcell
    "TTKOM.IS",    # Türk Telekom
    "TAVHL.IS",    # Turk Vataş
    "TKFEN.IS",    # TkFen
    "TICLK.IS",    # Tiçelli
    "TMSFT.IS",    # Turkiye Microsoft
    "TUREX.IS",    # Turex
    "TUTEM.IS",    # Tutem
    "TURNA.IS",    # Turna
    "TUSUQ.IS",    # Tusque
    
    # 41-50: Enerji
    "AKSA.IS",     # Aksa Enerji
    "TUPAS.IS",    # Türkiye Petrol
    "ENKA.IS",     # Enka
    "KRDMD.IS",    # Karadeniz
    "SODA.IS",     # Soda Sanayii
    "CCHOL.IS",    # Çelebi
    "KPGRP.IS",    # Kapıkap
    "EGEEN.IS",    # Egeen Enerji
    "ENJSA.IS",    # Enerjisa
    "GEMIN.IS",    # Gemin
    
    # 51-60: İnşaat & Gayrimenkul
    "EKGYO.IS",    # Emlak Konut
    "BLDYR.IS",    # Bilder
    "ORMA.IS",     # Orma
    "TOASY.IS",    # Toasan
    "YAPI.IS",     # Yapı
    "RSGYO.IS",    # Resorpia
    "YAPRK.IS",    # Yapıkredi Konut
    "INSGYO.IS",   # İnş Gayrimenkul
    "ARSAN.IS",    # Arsan
    "ARYAP.IS",    # Ar Yapı
    
    # 61-70: Üretim & Sanayi
    "ASELS.IS",    # Aselsan
    "OTKAR.IS",    # Otokar
    "FROTO.IS",    # Ford Otomotiv
    "SISE.IS",     # Şişecam
    "ARÇEL.IS",    # Arçelik
    "VESTEL.IS",   # Vestel
    "AYGAZ.IS",    # Aygaz
    "PETKE.IS",    # Petkim
    "ULUSE.IS",    # Ulusal
    "KAYNK.IS",    # Kaynak
    
    # 71-80: Üretim & Sanayi (devamı)
    "LCDHO.IS",    # Leçar
    "GOLTS.IS",    # Goldaş
    "HMROL.IS",    # Hamrolı
    "MRSB.IS",     # Marsan
    "KRGYO.IS",    # Karma
    "SRVGY.IS",    # Seren
    "HEYLL.IS",    # Heyll
    "HRSGL.IS",    # Herosğil
    "KORDS.IS",    # Kordindir
    "IPEKE.IS",    # İpek Enerji
    
    # 81-90: Turizm, Gıda & Perakende
    "TRST.IS",     # Türsab
    "BJKAS.IS",    # Bilmece
    "KOTON.IS",    # Koton
    "NTHOL.IS",    # Net Turizm
    "ULKER.IS",    # Ülker
    "PENGD.IS",    # Penguen
    "CARSI.IS",    # Çarşı
    "HATEK.IS",    # Hatek
    "MERKO.IS",    # Merkoz
    "PSTKA.IS",    # Plastikart
    
    # 91-100: Çeşitli
    "ARBOS.IS",    # Arbos
    "EGLET.IS",    # Egeli
    "NTTUR.IS",    # Turtur
    "MARTI.IS",    # Martı
    "ASMK.IS",     # Asım
    "KNC.IS",      # Konç
    "KSTUR.IS",    # Ksu
    "PETKM.IS",    # Petkim
    "TAVHL.IS",    # Tavahlı
    "GEOSH.IS",    # Geoşu
]

# ═══════════════════════════════════════════════════════════
# GLOBAL TOP 50 HISSELER
# ═══════════════════════════════════════════════════════════

GLOBAL_STOCKS = [
    # Teknoloji Mega Cap (10)
    "AAPL",        # Apple
    "MSFT",        # Microsoft
    "GOOGL",       # Google
    "GOOG",        # Google Class C
    "AMZN",        # Amazon
    "META",        # Meta
    "NVDA",        # Nvidia
    "TSLA",        # Tesla
    "NFLX",        # Netflix
    "ADBE",        # Adobe
    
    # Finans (10)
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
    
    # Tüketim (7)
    "WMT",         # Walmart
    "KO",          # Coca-Cola
    "PEP",         # PepsiCo
    "MCD",         # McDonald's
    "NKE",         # Nike
    "COST",        # Costco
    "HD",          # Home Depot
]

# Tüm hisseler
ALL_STOCKS = TURKISH_STOCKS + GLOBAL_STOCKS

print(f"✅ Toplam hisse sayısı: {len(ALL_STOCKS)}")
print(f"   - BIST 100: {len(TURKISH_STOCKS)}")
print(f"   - Global Top 50: {len(GLOBAL_STOCKS)}")

# --- ANALIZ PARAMETRELERI ---
FIBONACCI_LEVELS = [0.236, 0.382, 0.500, 0.618, 0.786]

RSI_PERIOD = 14
MACD_FAST = 12
MACD_SLOW = 26
MACD_SIGNAL = 9
BOLLINGER_PERIOD = 20
SMA_SHORT = 20
SMA_LONG = 50

WEIGHT_TECHNICAL = 40
WEIGHT_FUNDAMENTAL = 30
WEIGHT_NEWS_SENTIMENT = 20
WEIGHT_MOMENTUM = 10

# --- ZAMANLAMA ---
DAILY_RUN_HOUR = 9
DAILY_RUN_MINUTE = 30
