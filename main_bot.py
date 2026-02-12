# ============================================================
# main_bot.py — ANA BOT (Orchestrator)
# ============================================================

import sys
import os
import schedule
import time
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

    print("\n" + "=" * 65)
    print(f"  🚀 BORSA ANALİZ BOT BAŞLANGICI")
    print(f"  📅 {datetime.now().strftime('%d %B %Y, %H:%M:%S')}")
    print("=" * 65)

    # ─── STEP 1: HABER ANALİZİ ─────────────────────────────
    try:
        news_data = analyze_all_news()
        sector_scores = news_data.get("sector_scores", {})
    except Exception as e:
        print(f"❌ Haber analizi hatası: {e}")
        sector_scores = {}
        news_data = {"raw_news": []}

    # ─── STEP 2: TEKNİK ANALİZ ─────────────────────────────
    try:
        stock_analysis = analyze_all_stocks(config.ALL_STOCKS)
    except Exception as e:
        print(f"❌ Teknik analiz hatası: {e}")
        stock_analysis = []

    if not stock_analysis:
        print("⛔ Hiçbir hisse analiz edilemedi.")
        return False

    # ─── STEP 3: SEÇİM ──────────────────────────────────────
    try:
        selected = select_top_stocks(stock_analysis, sector_scores, max_count=3)
        recommendations = generate_recommendation_text(selected, sector_scores)
    except Exception as e:
        print(f"❌ Scoring hatası: {e}")
        selected = []
        recommendations = {"recommendations": [], "market_mood": "⚪ Belirsiz"}

    # ─── STEP 4: GRAFİK ─────────────────────────────────────
    chart_paths = []
    if selected:
        try:
            chart_paths = generate_all_charts(selected)
        except Exception as e:
            print(f"❌ Grafik üretim hatası: {e}")

    # ─── STEP 5: EMAIL ──────────────────────────────────────
    try:
        html_body = generate_html_body(recommendations, chart_paths)
        success = send_email(html_body, chart_paths)
    except Exception as e:
        print(f"❌ Email hatası: {e}")
        success = False

    # ─── STEP 6: PERFORMANS TAKİBİ (GÜÇLENDİRİLMİŞ) ─────────
    try:
        tracker = PerformanceTracker()

        for rec in selected:

            ticker = rec.get("ticker", "UNKNOWN")

            # entry_price güvenliği
            entry_price = rec.get("entry_price") or rec.get("price")

            if entry_price is None:
                print(f"⚠️ {ticker} için entry_price bulunamadı → kayıt atlanıyor.")
                continue

            # Tip güvenliği (string gelirse float'a çevir)
            try:
                entry_price = float(entry_price)
            except:
                print(f"⚠️ {ticker} entry_price float'a çevrilemedi → atlandı.")
                continue

            rec["entry_price"] = entry_price

            try:
                rec_id = tracker.save_recommendation(rec)
                print(f"💾 {ticker} kaydedildi (ID: {rec_id})")
            except Exception as db_error:
                print(f"❌ {ticker} DB kayıt hatası: {db_error}")

        # Geçmiş performans kontrol
        perf_results = tracker.check_performance([7, 14, 30])

        if perf_results and datetime.now().weekday() == 0:
            report = tracker.generate_report(30)
            history = tracker.get_detailed_history(20)

            perf_html = generate_performance_email(report, history)

            send_email(
                perf_html,
                subject=f"📊 Haftalık Performans Raporu - {datetime.now().strftime('%d %b %Y')}"
            )

    except Exception as e:
        print(f"❌ Performans takip genel hata: {e}")

    print("\n" + "=" * 65)
    print("📋 SÜREÇ TAMAMLANDI")
    print("=" * 65)

    return success


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
