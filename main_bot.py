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

# --- İSTEK: SABİT BİLGİLENDİRME METİNLERİ ---
PUAN_ACIKLAMASI = "Bu sistem, hisseleri teknik ve temel verilerine göre 0-100 arası puanlar; 100 en güçlü al sinyalini temsil eder."
BILGILENDIRME_NOTU = "Şu anki güncel durum, hisseleri rastgele seçen 'Algoritmik Tarama' sistemidir ve hep bunun üzerine inşa edelim."

def run_full_analysis():
    print("\n" + "=" * 65)
    print(f"  🚀 BORSA ANALİZ BOT BAŞLANGICI")
    print(f"  📅 {datetime.now().strftime('%d %B %Y, %H:%M:%S')}")
    print("=" * 65)

    # 1. Haber Analizi
    try:
        news_data = analyze_all_news()
        sector_scores = news_data.get("sector_scores", {})
        print("  ✅ Haber analizi tamamlandı.")
    except Exception as e:
        print(f"  ❌ Haber hatası: {e}")
        sector_scores = {}

    # 2. Teknik Analiz
    try:
        stock_analysis = analyze_all_stocks(config.ALL_STOCKS)
        print(f"  ✅ {len(stock_analysis)} hisse analiz edildi.")
    except Exception as e:
        print(f"  ❌ Teknik hata: {e}")
        stock_analysis = []

    if not stock_analysis:
        print("\n⛔ Analiz edilemedi. Bot durduruluyor.")
        return False

    # 3. Seçim ve Puanlama
    try:
        selected = select_top_stocks(stock_analysis, sector_scores, max_count=3)
        recommendations = generate_recommendation_text(selected, sector_scores)
        
        # Mail içeriğine özel notları ekle
        recommendations['puan_aciklamasi'] = PUAN_ACIKLAMASI
        recommendations['bilgilendirme_notu'] = BILGILENDIRME_NOTU
    except Exception as e:
        print(f"  ❌ Puanlama/Seçim hatası: {e}")
        selected = []

    # 4. Grafik Üretimi
    chart_paths = generate_all_charts(selected) if selected else []

    # 5. Email Gönderimi (ahm.cagil@hotmail.com üzerinden)
    try:
        html_body = generate_html_body(recommendations, chart_paths)
        success = send_email(html_body, chart_paths)
        if success:
            print("  🎉 Email başarıyla iletildi.")
        else:
            print("  ❌ Email gönderimi başarısız (Logları kontrol edin).")
    except Exception as e:
        print(f"  ❌ Email hazırlama hatası: {e}")
        success = False

    # 6. Performans DB Güncelleme
    try:
        tracker = PerformanceTracker()
        for rec in selected:
            tracker.save_recommendation(rec)
        
        # Haftalık Rapor (Pazartesi)
        if datetime.now().weekday() == 0:
            report = tracker.generate_report(30)
            history = tracker.get_detailed_history(20)
            perf_html = generate_performance_email(report, history)
            send_email(perf_html, subject="📊 Haftalık Performans Raporu")
            
    except Exception as e:
        print(f"  ❌ Performans sistemi hatası: {e}")

    print("\n" + "=" * 65 + "\n  ✅ İŞLEM TAMAMLANDI\n" + "=" * 65)
    return success

if __name__ == "__main__":
    run_full_analysis()
