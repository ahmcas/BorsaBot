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
# BIST 100 - TÜRKIYE BORSA HISSELERI (100 hisse)
# ═══════════════════════════════════════════════════════════

TURKISH_STOCKS = [
    # Bankalar & Finans (15)
    "AKBANK.IS",   # Akbank
    "GARAN.IS",    # Garanti BBVA
    "ISA.IS",      # İş Bankası
    "INDOG.IS",    # İnfo İnşaat Holding
    "YBANK.IS",    # Yapı ve Kredi Bank
    "SFIN.IS",     # Schnider Finans
    "TKFEN.IS",    # TkFen Gayrimenkul
    "TEBNK.IS",    # TEB Bank
    "HALKB.IS",    # Halkbank
    "KLVT.IS",     # Kültür Yatırım
    "KREDI.IS",    # Kredi Katılım
    "PBANK.IS",    # Pera Bank
    "ALBRK.IS",    # Albayrak Group
    "SAFAK.IS",    # Şafak Yatırım
    "AKTIF.IS",    # Aktif Finans
    
    # Sigorta (5)
    "DOAS.IS",     # Doğa Sigorta
    "ACSEL.IS",    # Açık Sigorta
    "AEGON.IS",    # Aegon Ödeme
    "XYAPI.IS",    # Xyapı Sigorta
    "RSGUP.IS",    # Resepsiyon
    
    # Telekomunikasyon (3)
    "TCELL.IS",    # Turkcell
    "TTKOM.IS",    # Türk Telekom
    "TRWF.IS",     # Turkcell Vodafone
    
    # Enerji & Petrol (8)
    "AKSA.IS",     # Aksa Enerji
    "TUPAS.IS",    # Türkiye Petrol
    "CCHOL.IS",    # Çelebi Holding
    "GENIL.IS",    # Genlik İnşaat
    "DKHOL.IS",    # Doğan Holding
    "ENKA.IS",     # Enka Holding
    "KRDMD.IS",    # Karadeniz
    "SODA.IS",     # Soda Sanayii
    
    # İnşaat & Gayrimenkul (12)
    "EKGYO.IS",    # Emlak Konut
    "BLDYR.IS",    # Bilder Gayrimenkul
    "TOASY.IS",    # Toasan Madencilik
    "ORMA.IS",     # Orma Holding
    "YAPI.IS",     # Yapı Holding
    "RSGYO.IS",    # Resorpia Gayrimenkul
    "AKMYA.IS",    # Akbulut Makine
    "TRLAT.IS",    # Turla Tekstil
    "MRSB.IS",     # Marsan Tekstil
    "HMROL.IS",    # Hamrolı
    "CEYS.IS",     # Çeyi Sakız
    "HRSGL.IS",    # Herosğil Tekstil
    
    # Üretim & Sanayi (20)
    "ASELS.IS",    # Aselsan
    "OTKAR.IS",    # Otokar
    "FROTO.IS",    # Ford Otomotiv
    "TOYO.IS",     # Toyokogyo
    "SISE.IS",     # Şişecam
    "ISKUR.IS",    # İskur
    "TCLER.IS",    # Tüm Cemaat Ler
    "CRYHO.IS",    # Crystalize
    "ARÇEL.IS",    # Arçelik
    "VESBE.IS",    # Vestel Beyaz
    "VESTEL.IS",   # Vestel Elektronik
    "AYGAZ.IS",    # Aygaz
    "PETKE.IS",    # Petkim Kimya
    "KORDS.IS",    # Kordindir Oyuncu
    "ULUSE.IS",    # Ulusal Tekstil
    "ANELE.IS",    # Anele Tekstil
    "KAYNK.IS",    # Kaynak Tekstil
    "LCDHO.IS",    # Leçar Holding
    "NTTUR.IS",    # Net Turizm
    "PNTAU.IS",    # Pantau
    
    # Turizm & Otel (8)
    "TURSH.IS",    # Turşu Turizm
    "TTSS.IS",     # Thessa Turizm
    "ALYAG.IS",    # Alyağ Turizm
    "BJKAS.IS",    # Bilmece Kas
    "DERIN.IS",    # Derin Turizm
    "GEOSH.IS",    # Geoşu Turizm
    "HERTT.IS",    # Hertz Turizm
    "TRTUR.IS",    # Turtur Turizm
    
    # Gıda & İçecek (8)
    "ULKER.IS",    # Ülker Bisküvi
    "HAPPF.IS",    # Happy Foods
    "PENGD.IS",    # Penguen Gıda
    "HATEK.IS",    # Hatek Gıda
    "MERKO.IS",    # Merkez Otel
    "PLAVT.IS",    # Plavan Gıda
    "SEFKR.IS",    # Sefakirin Gıda
    "TKFYE.IS",    # Takfiye Gıda
    
    # Perakende & Ticaret (8)
    "CARSI.IS",    # Çarşı Merkez
    "DIFSH.IS",    # Difesh Perakende
    "GRSEL.IS",    # Gürsel Perakende
    "MAKSM.IS",    # Maksima Perakende
    "MKTDR.IS",    # Market Dergisi
    "SEFIK.IS",    # Sefik Perakende
    "TOKNY.IS",    # Tokni Perakende
    "TRADE.IS",    # Trade Ticaret
    
    # Kimya & Plastik (6)
    "PETKM.IS",    # Petkim
    "BAYMR.IS",    # Bayram Kimya
    "CHMBK.IS",    # Cheminova
    "CHMPL.IS",    # Chempal Plastik
    "KLMPS.IS",    # Klimaplus
    "PSTKA.IS",    # Plastikart
    
    # Kağıt & Orman (3)
    "ARBOS.IS",    # Arbos Orman
    "KAĞIT.IS",    # Kağıt İşletmeleri
    "ORNUS.IS",    # Ornustech
]

# ═══════════════════════════════════════════════════════════
# GLOBAL TOP 50 HISSELER (S&P 500, NASDAQ, Avrupa)
# ═══════════════════════════════════════════════════════════

GLOBAL_STOCKS = [
    # Teknoloji (15)
    "AAPL",        # Apple
    "MSFT",        # Microsoft
    "GOOGL",       # Google/Alphabet
    "GOOG",        # Google (Class C)
    "AMZN",        # Amazon
    "NVIDIA",      # Nvidia (NVDA yerine)
    "META",        # Meta (Facebook)
    "TSLA",        # Tesla
    "AVGO",        # Broadcom
    "QCOM",        # Qualcomm
    "CRM",         # Salesforce
    "ADBE",        # Adobe
    "SNPS",        # Synopsys
    "ARM",         # Arm
    "VRTX",        # Vertex Pharmaceuticals
    
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
    "GILD",        # Gilead Sciences
    
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
print(f"   - Türkiye (BIST 100): {len(TURKISH_STOCKS)}")
print(f"   - Global (Top 50): {len(GLOBAL_STOCKS)}")

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
