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
PUAN_ACIKLAMASI = "Mailin başında puan açıklaması: Bu sistem, hisseleri teknik ve temel verilerine göre 0-100 arası puanlar; 100 en güçlü al sinyalini temsil eder."
BILGILENDIRME_NOTU = "Şu anki güncel durum, hisseleri rastgele seçen 'Algoritmik Tarama' sistemidir ve hep bunun üzerine inşa edelim."

def run_full_analysis():
    print(f"\n🚀 ANALİZ BAŞLADI: {datetime.now().strftime('%d %B %Y')}")
    
    # 1. Analizler
    news_data = analyze_all_news()
    stock_analysis = analyze_all_stocks(config.ALL_STOCKS)
    
    # 2. Seçim ve Metin Hazırlama
    selected = select_top_stocks(stock_analysis, news_data.get("sector_scores", {}), max_count=3)
    recommendations = generate_recommendation_text(selected, news_data.get("sector_scores", {}))
    
    # Sabit metinleri ekle
    recommendations['custom_header'] = PUAN_ACIKLAMASI
    recommendations['custom_footer'] = BILGILENDIRME_NOTU

    # 3. Grafik ve Email
    chart_paths = generate_all_charts(selected)
    html_body = generate_html_body(recommendations, chart_paths)
    
    # GÖNDERİM (ahm.cagil@hotmail.com -> ahm.cagil@gmail.com)
    success = send_email(html_body, chart_paths)

    # 4. Performans ve Veritabanı
    tracker = PerformanceTracker()
    for rec in selected:
        tracker.save_recommendation(rec)
    
    # Pazartesi raporu
    if datetime.now().weekday() == 0:
        report = tracker.generate_report(30)
        history = tracker.get_detailed_history(10)
        perf_html = generate_performance_email(report, history)
        send_email(perf_html, subject="📊 Haftalık Performans Raporu")

    return success

if __name__ == "__main__":
    run_full_analysis()
