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
# main_bot.py — ANA BOT (Orchestrator)
# ============================================================

import sys
import os
import schedule
import time
from datetime import datetime

# Module imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config
from news_analyzer import analyze_all_news
from technical_analyzer import analyze_all_stocks
from scorer import select_top_stocks, generate_recommendation_text
from chart_generator import generate_all_charts
from mail_sender import generate_html_body, send_email
from performance_tracker import PerformanceTracker, generate_performance_email

# ✅ YENİ EKLENDİ
from portfolio_engine import PortfolioEngine


def run_full_analysis():

    print("\n" + "=" * 65)
    print(f"  🚀 BORSA ANALİZ BOT BAŞLANGICI")
    print(f"  📅 {datetime.now().strftime('%d %B %Y, %H:%M:%S')}")
    print("=" * 65)

    # ─── STEP 1: HABER ANALİZİ ─────────────────────────────
    try:
        news_data = analyze_all_news()
        sector_scores = news_data.get("sector_scores", {})
        top_sectors = news_data.get("top_sectors", [])
        risk_sectors = news_data.get("risk_sectors", [])
    except:
        sector_scores = {}
        news_data = {"raw_news": []}

    # ─── STEP 2: TEKNİK ANALİZ ─────────────────────────────
    try:
        stock_analysis = analyze_all_stocks(config.ALL_STOCKS)
    except:
        stock_analysis = []

    if not stock_analysis:
        print("⛔ Hiçbir hisse analiz edilemedi.")
        return False

    # ─── STEP 3: SCORING ───────────────────────────────────
    try:
        selected = select_top_stocks(stock_analysis, sector_scores, max_count=3)
        recommendations = generate_recommendation_text(selected, sector_scores)
    except:
        selected = []
        recommendations = {"recommendations": [], "market_mood": "Belirsiz"}

    # ─── STEP 4: GRAFİK ────────────────────────────────────
    chart_paths = []
    if selected:
        try:
            chart_paths = generate_all_charts(selected)
        except:
            pass

    # ─── STEP 5: EMAIL ─────────────────────────────────────
    try:
        html_body = generate_html_body(recommendations, chart_paths)
        success = send_email(html_body, chart_paths)
    except:
        success = False

    # ─── STEP 6: PERFORMANS + PORTFÖY ENGINE ──────────────
    print("\n📊 ADIM 6: Performans & Portföy Yönetimi...")

    try:
        tracker = PerformanceTracker()

        # Günlük önerileri kaydet
        for rec in selected:
            tracker.save_recommendation(rec)

        tracker.check_performance([7, 14, 30])

        # 30 günlük performans raporu
        report = tracker.generate_report(30)

        # ===============================
        # ✅ PORTFOLIO ENGINE ENTEGRASYON
        # ===============================

        engine = PortfolioEngine(total_capital=100000)

        # Basit market regime mantığı (isteğe göre evre sistemine bağlanır)
        if report["win_rate"] >= 65:
            regime = "BULL"
        elif report["win_rate"] >= 50:
            regime = "NEUTRAL"
        else:
            regime = "BEAR"

        portfolio = engine.allocate_portfolio(selected, regime)
        system_metrics = engine.calculate_system_strength(report)

        # ===============================
        # Haftalık Profesyonel Rapor (Pazartesi)
        # ===============================
        if datetime.now().weekday() == 0:

            history = tracker.get_detailed_history(20)

            perf_html = generate_performance_email(report, history)

            portfolio_html = f"""
            <h2>📊 Portföy Dağılımı</h2>
            <p><b>Nakit:</b> %{portfolio['cash_ratio_pct']} 
            ({portfolio['cash_amount']} ₺)</p>
            """

            for pos in portfolio["positions"]:
                portfolio_html += f"""
                <p>
                <b>{pos['ticker']}</b><br>
                Ağırlık: %{pos['weight_pct']}<br>
                Lot: {pos['shares']}<br>
                Stop: {pos['stop_price']}<br>
                Confidence: {pos['confidence']}
                </p>
                """

            system_html = f"""
            <h2>🧠 Sistem Gücü</h2>
            <p>Skor: {system_metrics['system_strength_score']} / 100</p>
            <p>Risk Seviyesi: {system_metrics['risk_level']}</p>
            """

            final_report = perf_html + portfolio_html + system_html

            send_email(
                final_report,
                subject=f"📊 Haftalık Profesyonel Portföy Raporu - {datetime.now().strftime('%d %b %Y')}"
            )

    except Exception as e:
        print("Performans/Portföy hatası:", e)

    print("\n✅ ANALİZ TAMAMLANDI")
    return success


# ─── SCHEDULER ─────────────────────────────────────────────

def start_scheduler():

    schedule.every().day.at(
        f"{config.DAILY_RUN_HOUR}:{config.DAILY_RUN_MINUTE:02d}"
    ).do(run_full_analysis)

    run_full_analysis()

    while True:
        schedule.run_pending()
        time.sleep(60)


if __name__ == "__main__":

    import argparse

    parser = argparse.ArgumentParser(description="Borsa Analiz Botu")
    parser.add_argument("--mode", choices=["run", "schedule", "test"],
                       default="run")
    args = parser.parse_args()

    if args.mode == "test":
        config.ALL_STOCKS = ["THYAO.IS", "AAPL"]
        run_full_analysis()

    elif args.mode == "schedule":
        start_scheduler()

    else:
        run_full_analysis()
