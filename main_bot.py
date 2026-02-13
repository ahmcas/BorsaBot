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

    # ANALİZ MAİLİ
    html_body = generate_html_body(recommendations, chart_paths)
    send_email(html_body, chart_paths)

    # PERFORMANS
    tracker = PerformanceTracker()

    if selected:
        for rec in selected:
            tracker.save_recommendation(rec)

    tracker.check_performance()

    report_7 = tracker.generate_report(7)
    report_14 = tracker.generate_report(14)
    report_30 = tracker.generate_report(30)

    report = None
    period = ""

    if report_30["total"] > 0:
        report = report_30
        period = "30 Gün"
    elif report_14["total"] > 0:
        report = report_14
        period = "14 Gün"
    elif report_7["total"] > 0:
        report = report_7
        period = "7 Gün"

    if report:
        history = tracker.get_detailed_history(20)
        perf_html = generate_performance_email(report, history, period)

        send_email(
            perf_html,
            subject=f"📊 {period} Performans Raporu - {datetime.now().strftime('%d %b %Y')}"
        )

        print(f"📈 {period} performans raporu gönderildi.")
    else:
        print("Henüz ölçülebilir performans verisi yok.")

    print("✅ Bot tamamlandı.")


if __name__ == "__main__":
    run_full_analysis()
