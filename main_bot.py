# ============================================================
# main_bot.py — ANA BOT (Orchestrator)
# ============================================================
# Bu dosya tüm sistemi yönetir:
# 1) Haberleri çeker ve analiz eder
# 2) Tüm hisselerin teknik analizini yapır
# 3) Master scorer ile nihai skor hesaplar
# 4) En iyi 1-3 hisseyi seçer
# 5) Grafikleri üretir
# 6) Email'i formatlar ve gönderir
# 7) Her gün otomatik olarak çalıştırılır
# ============================================================

# ============================================================
# main_bot.py — GÜNCEL ANA BOT (Orchestrator)
# ============================================================

import sys
import os
from datetime import datetime

# Modül yollarını ayarla
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config
from news_analyzer import analyze_all_news
from technical_analyzer import analyze_all_stocks
from scorer import select_top_stocks, generate_recommendation_text
from chart_generator import generate_all_charts
from mail_sender import generate_html_body, send_email
from performance_tracker import PerformanceTracker, generate_performance_email

# --- SABİT METİNLER (Kullanıcı İstekleri) ---
PUAN_ACIKLAMASI = "Bu sistem, hisseleri teknik ve temel verilerine göre 0-100 arası puanlar; 100 en güçlü al sinyalini temsil eder."
BILGILENDIRME = "Şu anki güncel durum, hisseleri rastgele seçen 'Algoritmik Tarama' sistemidir ve hep bunun üzerine inşa edelim."

def run_full_analysis():
    print("\n" + "="*50)
    print(f"🚀 ANALİZ BAŞLADI: {datetime.now().strftime('%d.%m.%Y %H:%M')}")
    print("="*50)

    # 1. Haber ve Sektör Analizi
    try:
        news_data = analyze_all_news()
        sector_scores = news_data.get("sector_scores", {})
    except Exception as e:
        print(f"⚠️ Haber analizi hatası: {e}")
        sector_scores = {}

    # 2. Teknik Tarama
    try:
        stock_analysis = analyze_all_stocks(config.ALL_STOCKS)
    except Exception as e:
        print(f"❌ Teknik analiz hatası: {e}")
        stock_analysis = []

    if not stock_analysis:
        print("⛔ Analiz edilecek hisse bulunamadı.")
        return False

    # 3. Hisse Seçimi ve Puanlama
    selected = select_top_stocks(stock_analysis, sector_scores, max_count=3)
    recommendations = generate_recommendation_text(selected, sector_scores)
    
    # Mail formatına özel metinleri ekle
    recommendations['puan_aciklamasi_baslik'] = PUAN_ACIKLAMASI
    recommendations['algoritma_notu_alt'] = BILGILENDIRME

    # 4. Grafiklerin Hazırlanması
    chart_paths = generate_all_charts(selected) if selected else []

    # 5. Email Gönderimi (ahm.cagil@hotmail.com üzerinden)
    try:
        html_body = generate_html_body(recommendations, chart_paths)
        # Mail gönderim fonksiyonu içindeki MAIL_RECIPIENT ahm.cagil@gmail.com olarak ayarlı olmalı
        success = send_email(html_body, chart_paths)
        if success:
            print("✅ Email başarıyla gönderildi.")
    except Exception as e:
        print(f"❌ Mail hatası: {e}")
        success = False

    # 6. Performans Takibi ve Veritabanı Güncelleme
    try:
        tracker = PerformanceTracker()
        for rec in selected:
            tracker.save_recommendation(rec)
            print(f"💾 Veritabanına kaydedildi: {rec['ticker']}")
        
        # Geçmiş performansları güncelle
        tracker.check_performance([1, 7, 30])
        
        # Pazartesi günü ise performans raporu gönder
        if datetime.now().weekday() == 0:
            report = tracker.generate_report(30)
            history = tracker.get_detailed_history(10)
            perf_html = generate_performance_email(report, history)
            send_email(perf_html, subject="📊 Haftalık Performans Raporu")
            
    except Exception as e:
        print(f"⚠️ Performans takip hatası: {e}")

    print("="*50 + "\n✅ İŞLEM TAMAMLANDI\n" + "="*50)
    return success

if __name__ == "__main__":
    run_full_analysis()
