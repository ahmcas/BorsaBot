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

import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import config
from news_analyzer import analyze_all_news
from technical_analyzer import analyze_all_stocks
from scorer import select_top_stocks, generate_recommendation_text
from chart_generator import generate_all_charts
from mail_sender import generate_html_body, send_email
from performance_tracker import PerformanceTracker, generate_performance_email


def run_full_analysis():

    print("=" * 60)
    print("🚀 BORSA ANALİZ BOTU BAŞLADI")
    print(datetime.now())
    print("=" * 60)

    # HABER
    news_data = analyze_all_news()
    sector_scores = news_data.get("sector_scores", {})

    # TEKNİK
    stock_analysis = analyze_all_stocks(config.ALL_STOCKS)

    if not stock_analysis:
        print("Hiç hisse analiz edilemedi.")
        return

    # SEÇİM
    selected = select_top_stocks(stock_analysis, sector_scores, max_count=3)
    recommendations = generate_recommendation_text(selected, sector_scores)

    # GRAFİK
    chart_paths = []
    if selected:
        chart_paths = generate_all_charts(selected)

    # NORMAL ANALİZ MAİLİ
    html_body = generate_html_body(recommendations, chart_paths)
    send_email(html_body, chart_paths)

    # PERFORMANS
    tracker = PerformanceTracker()

    if selected:
        for rec in selected:
            tracker.save_recommendation(rec)

    tracker.check_performance([7, 14, 30])

    report = tracker.generate_report(30)
    history = tracker.get_detailed_history(20)

    if report["total"] > 0:
        perf_html = generate_performance_email(report, history)
        send_email(
            perf_html,
            subject=f"📊 Performans Raporu - {datetime.now().strftime('%d %b %Y')}"
        )
        print("📈 Performans raporu gönderildi.")
    else:
        print("Henüz performans verisi oluşmadı.")

    print("✅ Bot tamamlandı.")


if __name__ == "__main__":
    run_full_analysis()
