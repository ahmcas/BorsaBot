# ============================================================
# main_bot.py — Ana Orchestrator (v6 - KOMPLE FINAL)
# ============================================================
# Tüm modülleri koordine eden ana dosya
# Çalışma modları:
# - once: Tek seferlik çalıştır
# - once --quick: Hızlı test (5 hisse)
# - test: Test mode
# - (boş): Scheduler mode (her gün 09:30)
# ============================================================

import os
import sys
import logging
from datetime import datetime
import traceback

# Config yükle
import config

# Tüm moduller
from technical_analyzer import analyze_all_stocks
from news_analyzer import analyze_news
from scorer import select_top_stocks, generate_recommendation_text
from mail_sender import generate_html_body, send_email
from chart_generator import generate_charts
from commodity_analyzer import CommodityAnalyzer
from macro_analyzer import MacroAnalyzer

# QUICK MODE - Hızlı test için (GÜVENLİ HİSSELER)
QUICK_STOCKS = [
    "GARAN.IS",   # Garanti Bankası - TÜRKİYE
    "AAPL",       # Apple - USA
    "MSFT",       # Microsoft - USA
    "GOOGL",      # Google - USA
    "NVDA"        # Nvidia - USA
]


def setup_logging():
    """Python logging modülünü yapılandır"""
    os.makedirs(os.path.dirname(config.LOG_FILE), exist_ok=True)
    logging.basicConfig(
        level=getattr(logging, config.LOG_LEVEL, logging.INFO),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(config.LOG_FILE, encoding="utf-8"),
            logging.StreamHandler(),
        ],
    )


def print_header(title: str):
    """Başlık yazdır"""
    print("\n" + "="*70)
    print(f"🚀 {title}")
    print("="*70)


def print_section(title: str):
    """Bölüm başlığı yazdır"""
    print(f"\n📋 {title}...")


def run_analysis(quick: bool = False):
    """Ana analiz fonksiyonu"""
    
    try:
        print_header("BORSA ANALİZİ BAŞLANIYOR")
        
        start_time = datetime.now()
        
        # Analiz edilecek hisseler
        stocks_to_analyze = QUICK_STOCKS if quick else config.ALL_STOCKS
        
        mode = f"⚡ QUICK MODE ({len(QUICK_STOCKS)} hisse)" if quick else f"📊 NORMAL MODE ({len(config.ALL_STOCKS)} hisse)"
        print(f"\n{mode}")
        print(f"Başlangıç: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # ═══════════════════════════════════════════════════════════
        # ADIM 1: Teknik Analiz
        # ═══════════════════════════════════════════════════════════
        print_section("ADIM 1: Teknik Analiz")
        
        try:
            technical_results = analyze_all_stocks(stocks_to_analyze)
            successful_tech = len([r for r in technical_results if not r.get('skip')])
            
            if successful_tech == 0:
                print(f"⚠️  Hiçbir hisse analiz edilmedi, fallback aktive ediliyor...")
            else:
                print(f"✅ {successful_tech}/{len(stocks_to_analyze)} hisse analiz edildi")
        
        except Exception as e:
            print(f"❌ Teknik analiz hatası: {e}")
            technical_results = []
            successful_tech = 0
        
        # ═══════════════════════════════════════════════════════════
        # ADIM 2: Haber Analizi
        # ═══════════════════════════════════════════════════════════
        print_section("ADIM 2: Haber Analizi")
        
        try:
            sector_scores = analyze_news(days_back=1)
            print(f"✅ Haber analizi tamamlandı")
        except Exception as e:
            print(f"⚠️  Haber analizi yapılamadı: {e}")
            sector_scores = {}
        
        # ═══════════════════════════════════════════════════════════
        # ADIM 3: Skor Hesaplama ve Seçim
        # ═══════════════════════════════════════════════════════════
        print_section("ADIM 3: Skor Hesaplama")
        
        try:
            selected = select_top_stocks(technical_results, sector_scores, max_count=config.MAX_RECOMMENDATIONS)
            
            if len(selected) == 0:
                print(f"⚠️  Hiçbir hisse seçilmedi!")
                print(f"   Fallback: İlk 1-2 hisse manuel olarak seçiliyor...")
                
                # Fallback: En azından birini seç
                if technical_results:
                    valid = [r for r in technical_results if not r.get('skip')]
                    if valid:
                        selected = valid[:1]
                        print(f"   ✅ Fallback seçim: {selected[0].get('ticker')}")
            else:
                print(f"✅ {len(selected)} hisse seçildi")
                for i, stock in enumerate(selected, 1):
                    print(f"   {i}. {stock.get('ticker', '?'):10s} - Skor: {stock.get('score', 0):6.1f}")
        
        except Exception as e:
            print(f"❌ Skor hesaplama hatası: {e}")
            traceback.print_exc()
            selected = []
        
        # ═══════════════════════════════════════════════════════════
        # ADIM 4: Öneriler Üretme
        # ═══════════════════════════════════════════════════════════
        print_section("ADIM 4: Öneriler Üretiliyor")
        
        try:
            recommendations = generate_recommendation_text(selected, sector_scores, candidates=selected)
            rec_count = len(recommendations.get("recommendations", []))
            print(f"✅ {rec_count} öneri oluşturuldu")
        except Exception as e:
            print(f"❌ Öneri oluşturma hatası: {e}")
            traceback.print_exc()
            recommendations = {"recommendations": [], "total_selected": 0}
        
        # ═══════════════════════════════════════════════════════════
        # ADIM 4.5: Emtia & Makro Analiz
        # ═══════════════════════════════════════════════════════════
        print_section("ADIM 4.5: Emtia & Makro Analiz")
        
        commodity_data = None
        macro_data = None
        holiday_alerts = []
        
        try:
            commodity_data = CommodityAnalyzer.analyze_all_commodities()
            print(f"✅ Emtia analizi tamamlandı")
        except Exception as e:
            print(f"⚠️  Emtia analizi yapılamadı: {e}")
        
        try:
            dxy_result = MacroAnalyzer.analyze_dxy()
            debt_result = MacroAnalyzer.get_us_debt_analysis()
            geo_risk = sector_scores.get("geopolitical_risk", {})
            supply_demand = sector_scores.get("supply_demand_trends", [])
            macro_data = {
                "us_debt": debt_result,
                "dxy": dxy_result,
                "geopolitical_risk": geo_risk,
                "supply_demand_trends": supply_demand,
            }
            holiday_alerts = MacroAnalyzer.check_upcoming_holidays(days_ahead=14)
            print(f"✅ Makro analiz tamamlandı")
        except Exception as e:
            print(f"⚠️  Makro analiz yapılamadı: {e}")
        
        # ═══════════════════════════════════════════════════════════
        # ADIM 5: Email Hazırlama ve Gönderme
        # ═══════════════════════════════════════════════════════════
        print_section("ADIM 5: Email Hazırlanıyor")
        
        try:
            # HTML body oluştur
            html_body = generate_html_body(
                recommendations=recommendations,
                commodity_data=commodity_data,
                macro_data=macro_data,
                sector_scores=sector_scores,
                holiday_alerts=holiday_alerts,
            )
            print("✅ Email HTML oluşturuldu")
            
            # Grafikler (opsiyonel)
            chart_paths = []
            if not quick and selected:
                print("   📈 Grafikler oluşturuluyor...")
                for stock in selected[:3]:  # Max 3 grafik
                    try:
                        ticker = stock.get("ticker")
                        df = stock.get("dataframe")
                        
                        if ticker and df is not None:
                            chart_path = generate_charts(ticker, df)
                            if chart_path and os.path.exists(chart_path):
                                chart_paths.append(chart_path)
                                print(f"      ✅ {ticker} grafik oluşturuldu")
                    except Exception as e:
                        continue
            
            # Email gönder
            print("   📤 Email gönderiliyor...")
            email_sent = send_email(html_body, chart_paths, recommendations.get("total_selected", 0))
            
            if email_sent:
                print("✅ Email başarıyla gönderildi!")
            else:
                print("⚠️  Email gönderme başarısız")
        
        except Exception as e:
            print(f"❌ Email hatası: {e}")
            traceback.print_exc()
        
        # ═══════════════════════════════════════════════════════════
        # SONUÇ
        # ═══════════════════════════════════════════════════════════
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        print_header("ANALİZ TAMAMLANDI")
        print(f"\n📊 Özet:")
        print(f"   ✅ Teknik analiz: {successful_tech} hisse")
        print(f"   ✅ Seçilen hisseler: {len(selected)}")
        print(f"   ✅ Öneriler: {len(recommendations.get('recommendations', []))}")
        print(f"   ✅ Süre: {duration:.1f} saniye")
        print(f"   ✅ Bitiş: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
    except Exception as e:
        print_header("HATA OLUŞTU")
        print(f"❌ {e}")
        traceback.print_exc()


def main():
    """Ana program"""
    
    setup_logging()
    
    try:
        # Komut satırı argümanları
        if len(sys.argv) > 1:
            
            if sys.argv[1] == "once":
                # Tek seferlik çalıştır
                if len(sys.argv) > 2 and sys.argv[2] == "--quick":
                    print("⚡ QUICK MODE: Hızlı test (5 hisse, 1 gün haber)")
                    run_analysis(quick=True)
                else:
                    print(f"📊 NORMAL MODE: Tüm hisseler ({len(config.ALL_STOCKS)} hisse)")
                    run_analysis(quick=False)
            
            elif sys.argv[1] == "test":
                # Test mode
                print("🧪 TEST MODE: Hızlı test")
                run_analysis(quick=True)
            
            elif sys.argv[1] == "help":
                # Yardım
                print("""
╔════════════════════════════════════════════════════════════════════╗
║              BORSA BOT - KOMUT SATIRI KULLANIMI                    ║
╚════════════════════════════════════════════════════════════════════╝

Komutlar:

  python main_bot.py once --quick
      → Hızlı test mode (5 hisse, ~10-20 saniye)
      → Önerilir: İlk kez test etmek için

  python main_bot.py once
      → Normal mod (92 hisse, ~2-3 dakika)
      → Tüm hisseleri analiz et

  python main_bot.py test
      → Test mode (5 hisse)

  python main_bot.py
      → Scheduler mode (her gün 09:30'da çalışır)
      → Ctrl+C ile durdur

  python main_bot.py help
      → Bu yardımı göster

╔════════════════════════════════════════════════════════════════════╗
║                     ÖNERİMLER                                      ║
╚════════════════════════════════════════════════════════════════════╝

Hata oluşması durumunda:
  1. config.py'de API anahtarlarını kontrol et
  2. Internet bağlantısını kontrol et
  3. requirements.txt paketlerinin kurulu olduğunu kontrol et
  4. .env dosyasının varolduğunu kontrol et

API Limitleri:
  - NewsAPI: 100 istek/24 saat (ücretsiz)
  - Yahoo Finance: Sınırsız (rate limit yoktur)

Sonuçlar:
  - Email: Belirtilen alıcı adresine gönderilir
  - Grafikleri: charts/ klasöründe kaydedilir
  - Loglar: logs/ klasöründe kaydedilir
  - Cache: cache/ klasöründe kaydedilir

Troubleshooting:
  - Hiçbir hisse seçilmiyorsa: QUICK_STOCKS listesini kontrol et
  - Email gelmiyorsa: .env MAIL_* ayarlarını kontrol et
  - API hata veriyorsa: NewsAPI anahtarını kontrol et
                """)
            
            else:
                print(f"Bilinmeyen komut: {sys.argv[1]}")
                print("Yardım için: python main_bot.py help")
        
        else:
            # Scheduler mode
            print_header("SCHEDULER MODE BAŞLATILIYOR")
            print(f"📅 Her gün saat {config.DAILY_RUN_HOUR}:{config.DAILY_RUN_MINUTE:02d} çalışacak")
            print("Ctrl+C ile durdur\n")
            
            import schedule
            import time
            
            def scheduled_job():
                """Scheduled job"""
                print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Zamanlanmış analiz başlıyor...")
                run_analysis(quick=False)
                print(f"[{datetime.now().strftime('%H:%M:%S')}] Zamanlanmış analiz tamamlandı")
            
            # Zamanla
            schedule.every().day.at(f"{config.DAILY_RUN_HOUR}:{config.DAILY_RUN_MINUTE:02d}").do(scheduled_job)
            
            print("✅ Scheduler başladı")
            print(f"⏰ Sonraki çalışma: {datetime.now().strftime('%Y-%m-%d')} {config.DAILY_RUN_HOUR}:{config.DAILY_RUN_MINUTE:02d}\n")
            
            try:
                while True:
                    schedule.run_pending()
                    time.sleep(60)
            
            except KeyboardInterrupt:
                print("\n\n❌ Scheduler durduruldu")
                sys.exit(0)

    except KeyboardInterrupt:
        print("\n\n❌ Program durduruldu")
        sys.exit(0)
    
    except Exception as e:
        print(f"\n❌ Hata: {e}")
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
