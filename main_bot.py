# ============================================================
# main_bot.py — Ana Orchestrator (QUICK MODE)
# ============================================================

import os
import sys
from datetime import datetime

# Config yükle
import config

# Tüm moduller
from technical_analyzer import analyze_all_stocks
from news_analyzer import analyze_news
from scorer import select_top_stocks, generate_recommendation_text
from mail_sender import generate_html_body, send_email
from chart_generator import generate_charts
from global_market_analyzer import run_global_analysis, run_advanced_global_analysis
from advanced_features import run_all_advanced_features

# QUICK TEST MODE
QUICK_MODE = True  # ← BUNU BURSAYA AYARLA
QUICK_STOCKS = ["AKBANK.IS", "AAPL", "MSFT", "GARAN.IS", "ISA.IS"]  # Sadece 5 hisse


def run_analysis(quick=False):
    """Ana analiz fonksiyonu"""
    
    print("\n" + "="*70)
    print("🚀 BORSA ANALİZİ BAŞLANIYOR")
    print("="*70)
    
    stocks_to_analyze = QUICK_STOCKS if quick else config.ALL_STOCKS
    
    print(f"\n📊 Analiz edilen hisseler: {len(stocks_to_analyze)}")
    
    # ADIM 1: Teknik Analiz (Hızlı)
    print("\n📊 ADIM 1: Teknik Analiz...")
    try:
        technical_results = analyze_all_stocks(stocks_to_analyze)
        print(f"✅ {len([r for r in technical_results if not r.get('skip')])} hisse analiz edildi")
    except Exception as e:
        print(f"❌ Teknik analiz hatası: {e}")
        technical_results = []
    
    # ADIM 2: Haber Analizi (Hızlı)
    print("\n📰 ADIM 2: Haber Analizi...")
    try:
        sector_scores = analyze_news(days_back=3)  # 7 günden 3 güne düşür
        print(f"✅ Haber analizi tamamlandı")
    except Exception as e:
        print(f"❌ Haber analizi hatası: {e}")
        sector_scores = {}
    
    # ADIM 3: Skor Hesaplama ve Seçim
    print("\n🎯 ADIM 3: Skor Hesaplama...")
    try:
        selected = select_top_stocks(technical_results, sector_scores, max_count=3)
        print(f"✅ {len(selected)} hisse seçildi")
    except Exception as e:
        print(f"❌ Skor hesaplama hatası: {e}")
        selected = []
    
    # ADIM 4: Recommendation Oluştur
    print("\n📋 ADIM 4: Öneriler Hazırlanıyor...")
    try:
        recommendations = generate_recommendation_text(selected, sector_scores)
        print(f"✅ Öneriler oluşturuldu")
    except Exception as e:
        print(f"❌ Öneri oluşturma hatası: {e}")
        recommendations = {"recommendations": [], "total_selected": 0}
    
    # ADIM 5: Email Oluştur ve Gönder
    print("\n📧 ADIM 5: Email Hazırlanıyor...")
    try:
        html_body = generate_html_body(recommendations)
        
        # Grafikler (opsiyonel, hızlı mode'da atla)
        chart_paths = []
        if not quick:
            print("   📈 Grafikler oluşturuluyor...")
            for stock in selected:
                try:
                    df = stock.get("dataframe")
                    if df is not None:
                        chart_path = generate_charts(stock.get("ticker"), df)
                        if chart_path:
                            chart_paths.append(chart_path)
                except:
                    pass
        
        # Email gönder
        print("   📤 Email gönderiliyor...")
        send_email(html_body, chart_paths)
        print("✅ Email gönderildi!")
        
    except Exception as e:
        print(f"❌ Email hatası: {e}")
    
    print("\n" + "="*70)
    print("✅ ANALİZ TAMAMLANDI")
    print("="*70)


def main():
    """Ana program"""
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "once":
            # Tek seferlik çalıştır
            if len(sys.argv) > 2 and sys.argv[2] == "--quick":
                print("⚡ QUICK MODE AÇIK (5 hisse)")
                run_analysis(quick=True)
            else:
                print("📊 NORMAL MODE (92 hisse)")
                run_analysis(quick=False)
        
        elif sys.argv[1] == "test":
            # Test mode
            print("🧪 TEST MODE (5 hisse)")
            run_analysis(quick=True)
        
        elif sys.argv[1] == "help":
            print("""
            Kullanım:
            
            python main_bot.py once          - Tüm hisse analiz et
            python main_bot.py once --quick  - Sadece 5 hisse analiz et (HIZLI)
            python main_bot.py test          - Test mode
            python main_bot.py               - Scheduler mode (her gün 09:30)
            """)
    
    else:
        # Scheduler mode
        print("🔄 SCHEDULER MODE BAŞLATILIYOR")
        print(f"📅 Her gün saat {config.DAILY_RUN_HOUR}:{config.DAILY_RUN_MINUTE:02d} çalışacak")
        
        import schedule
        import time
        
        def job():
            run_analysis(quick=False)
        
        schedule.every().day.at(f"{config.DAILY_RUN_HOUR}:{config.DAILY_RUN_MINUTE:02d}").do(job)
        
        print("✅ Scheduler başladı. Ctrl+C ile durdur.")
        
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)
        except KeyboardInterrupt:
            print("\n❌ Scheduler durduruldu")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Program durduruldu")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Hata: {e}")
        sys.exit(1)
