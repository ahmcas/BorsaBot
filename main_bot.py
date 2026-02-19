# ============================================================
# main_bot.py — Ana Orchestrator (HATASIZ)
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

# QUICK MODE - Hızlı test için
QUICK_STOCKS = ["GARAN.IS", "ISA.IS", "AAPL", "MSFT", "NVDA"]  # Sadece güvenilir hisseler


def run_analysis(quick=False):
    """Ana analiz fonksiyonu"""
    
    print("\n" + "="*70)
    print("🚀 BORSA ANALİZİ BAŞLANIYOR")
    print("="*70)
    
    stocks_to_analyze = QUICK_STOCKS if quick else config.ALL_STOCKS
    
    print(f"\n📊 Analiz edilen hisseler: {len(stocks_to_analyze)}")
    
    # ADIM 1: Teknik Analiz
    print("\n📊 ADIM 1: Teknik Analiz...")
    try:
        technical_results = analyze_all_stocks(stocks_to_analyze)
        successful = len([r for r in technical_results if not r.get('skip')])
        print(f"✅ {successful}/{len(stocks_to_analyze)} hisse analiz edildi")
    except Exception as e:
        print(f"❌ Teknik analiz hatası: {e}")
        technical_results = []
    
    # ADIM 2: Haber Analizi (Sınırlı)
    print("\n📰 ADIM 2: Haber Analizi...")
    try:
        sector_scores = analyze_news(days_back=1)  # 1 günlük haber (API limit)
        print(f"✅ Haber analizi tamamlandı")
    except Exception as e:
        print(f"⚠️  Haber analizi yapılamadı (API limit): {e}")
        sector_scores = {}
    
    # ADIM 3: Skor Hesaplama
    print("\n🎯 ADIM 3: Skor Hesaplama...")
    try:
        selected = select_top_stocks(technical_results, sector_scores, max_count=3)
        print(f"✅ {len(selected)} hisse seçildi")
    except Exception as e:
        print(f"❌ Skor hesaplama hatası: {e}")
        selected = []
    
    # ADIM 4: Email Hazırlama
    print("\n📧 ADIM 4: Email Hazırlanıyor...")
    try:
        recommendations = generate_recommendation_text(selected, sector_scores)
        html_body = generate_html_body(recommendations)
        
        # Email gönder
        send_email(html_body, [])
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
            if len(sys.argv) > 2 and sys.argv[2] == "--quick":
                print("⚡ QUICK MODE (5 hisse, 1 gün)")
                run_analysis(quick=True)
            else:
                print("📊 NORMAL MODE (tüm hisseler)")
                run_analysis(quick=False)
        
        elif sys.argv[1] == "test":
            print("🧪 TEST MODE")
            run_analysis(quick=True)
        
        elif sys.argv[1] == "help":
            print("""
            Kullanım:
            python main_bot.py once --quick  - Hızlı test (5 hisse)
            python main_bot.py once          - Tüm hisseler
            python main_bot.py test          - Test mode
            """)
    else:
        # Scheduler mode
        print("🔄 SCHEDULER MODE BAŞLATILIYOR")
        
        import schedule
        import time
        
        def job():
            run_analysis(quick=False)
        
        schedule.every().day.at("09:30").do(job)
        
        print("✅ Scheduler başladı")
        
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)
        except KeyboardInterrupt:
            print("\n❌ Durduruldu")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"❌ Hata: {e}")
        sys.exit(1)
