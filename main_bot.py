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

# --- SABİT BİLGİLENDİRME METİNLERİ (Kullanıcı İsteği) ---
PUAN_ACIKLAMASI = "Bu sistem, hisseleri teknik ve temel verilerine göre 0-100 arası puanlar; 100 en güçlü al sinyalini temsil eder."
ALGORITMA_BILGISI = "Şu anki güncel durum, hisseleri rastgele seçen 'Algoritmik Tarama' sistemidir ve tüm analizler bu temel üzerine inşa edilmiştir."

def run_full_analysis():
    """
    Tam analiz pipeline'ı çalıştırır ve performance.db'yi günceller.
    """
    print("\n" + "=" * 65)
    print(f"  🚀 BORSA ANALİZ BOT BAŞLANGICI")
    print(f"  📅 {datetime.now().strftime('%d %B %Y, %H:%M:%S')}")
    print("=" * 65)

    # ─── STEP 1: HABER ANALİZİ (NEWS API ENTEGRASYONU) ────
    print("\n📰 ADIM 1: Haber analizi başlıyor...")
    try:
        # News API key'i config üzerinden veya environment'tan alınır
        news_data = analyze_all_news() 
        sector_scores = news_data.get("sector_scores", {})
        print(f"  ✅ Haber analizi tamamlandı. Sektör skorları hesaplandı.")
    except Exception as e:
        print(f"  ❌ Haber analizi hatası: {e}")
        sector_scores = {}
        news_data = {"raw_news": []}

    # ─── STEP 2: TEKNİK ANALİZ ─────────────────────────────
    print("\n📈 ADIM 2: Teknik analiz başlıyor...")
    try:
        stock_analysis = analyze_all_stocks(config.ALL_STOCKS)
        print(f"  ✅ {len(stock_analysis)} hisse teknik olarak tarandı.")
    except Exception as e:
        print(f"  ❌ Teknik analiz hatası: {e}")
        stock_analysis = []

    if not stock_analysis:
        print("\n⛔ Analiz edilecek veri bulunamadı. Bot durduruluyor.")
        return False

    # ─── STEP 3: MASTER SCORING & SEÇIM ────────────────────
    print("\n🎯 ADIM 3: Hisse seçimi ve skor hesabı...")
    try:
        # Puanlama sistemine göre en iyi 3 hisse
        selected = select_top_stocks(stock_analysis, sector_scores, max_count=3)
        recommendations = generate_recommendation_text(selected, sector_scores)
        
        # Mail başına eklenecek puan açıklamasını recommendations objesine enjekte ediyoruz
        recommendations['puan_aciklamasi'] = PUAN_ACIKLAMASI
        recommendations['algoritma_notu'] = ALGORITMA_BILGISI
    except Exception as e:
        print(f"  ❌ Scoring hatası: {e}")
        selected = []

    # ─── STEP 4: GRAFİK ÜRETIM ─────────────────────────────
    print("\n📊 ADIM 4: Grafik üretimi...")
    chart_paths = []
    if selected:
        try:
            chart_paths = generate_all_charts(selected)
        except Exception as e:
            print(f"  ❌ Grafik üretim hatası: {e}")

    # ─── STEP 5: EMAIL GÖNDERİM (SENDGRID & ÖZEL FORMAT) ───
    print("\n📧 ADIM 5: Email hazırlanıyor (SendGrid)...")
    try:
        # Mail içeriğine sabit açıklamaları ekleyen HTML üretimi
        html_body = generate_html_body(recommendations, chart_paths)
        
        # Mail gönderimi (ahm.cagil@hotmail.com üzerinden ahm.cagil@gmail.com'a)
        success = send_email(html_body, chart_paths)
        if success: print("  🎉 Email başarıyla iletildi.")
    except Exception as e:
        print(f"  ❌ Email hatası: {e}")
        success = False

    # ─── STEP 6: PERFORMANS TAKİBİ & DB GÜNCELLEME ────────
    print("\n📊 ADIM 6: Performance.db güncelleniyor...")
    try:
        tracker = PerformanceTracker()
        
        # Yeni önerileri kaydet (Test için DB'ye yazar)
        for rec in selected:
            tracker.save_recommendation(rec)
        
        # Geçmiş performansları kontrol et ve DB'yi güncelle
        perf_results = tracker.check_performance([1, 7, 30])
        print(f"  💾 DB Güncellendi. Kontrol edilen kayıt: {len(perf_results)}")
        
        # Haftalık Rapor (Pazartesi)
        if datetime.now().weekday() == 0:
            report = tracker.generate_report(30)
            history = tracker.get_detailed_history(10)
            perf_html = generate_performance_email(report, history)
            send_email(perf_html, subject=f"📊 Haftalık Performans - {datetime.now().strftime('%d.%m.%Y')}")

    except Exception as e:
        print(f"  ❌ Performans DB hatası: {e}")

    print("\n" + "=" * 65 + "\n  ✅ SÜREÇ TAMAMLANDI\n" + "=" * 65)
    return success

if __name__ == "__main__":
    # GitHub Actions veya manuel tetikleme için 'run' modu
    run_full_analysis()
