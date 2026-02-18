# ============================================================
# main_bot.py — Ana Orchestrator (v4 - KÜRESEL ANALİZ)
# ============================================================

import os
import sys
from datetime import datetime
import schedule
import time

# Local imports
import config
from technical_analyzer import analyze_all_stocks
from news_analyzer import analyze_news
from scorer import select_top_stocks, generate_recommendation_text
from mail_sender import generate_html_body, send_email
from chart_generator import generate_charts
from global_market_analyzer import (
    run_global_analysis,
    USDebtAnalyzer,
    CommodityAnalyzer,
    GeopoliticalAnalyzer,
    ExchangeHolidayTracker
)


def run_analysis():
    """Ana analiz fonksiyonu"""
    print("\n" + "="*70)
    print(f"🚀 BORSA ANALİZİ BAŞLANIYOR - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)
    
    # ADIM 0: Küresel Piyasa Analizi
    print("\n🌍 ADIM 0: Küresel Piyasa Analizi")
    print("-" * 70)
    global_analysis = run_global_analysis()
    
    # ADIM 1: Teknik Analiz
    print("\n📊 ADIM 1: Teknik Analiz")
    print("-" * 70)
    all_analysis = analyze_all_stocks(config.ALL_STOCKS)
    
    if not all_analysis:
        print("❌ Analiz başarısız!")
        return False
    
    valid_stocks = [s for s in all_analysis if not s.get("skip")]
    print(f"✅ {len(valid_stocks)} hisse analiz edildi")
    
    # ADIM 2: Haber Analizi
    print("\n📰 ADIM 2: Haber Analizi")
    print("-" * 70)
    sector_scores = analyze_news()
    
    if not sector_scores:
        print("⚠️  Haber analizi yapılamadı, varsay��lan değerler kullanılıyor")
        sector_scores = {"genel": 0.0}
    else:
        print(f"✅ {len(sector_scores)} sektör analiz edildi")
        for sector, score in sorted(sector_scores.items(), key=lambda x: x[1], reverse=True)[:5]:
            print(f"   {sector}: {score:+.3f}")
    
    # ADIM 3: Skor Hesaplama
    print("\n🎯 ADIM 3: Skor Hesaplama & Seçim")
    print("-" * 70)
    selected = select_top_stocks(all_analysis, sector_scores, max_count=3)
    
    if selected:
        print(f"✅ {len(selected)} hisse seçildi:")
        for i, stock in enumerate(selected, 1):
            print(f"   {i}. {stock.get('ticker')} - Skor: {stock.get('final_score', 0):.1f}")
    else:
        print("⚠️  Alım sinyali bulunamadı")
    
    # ADIM 4: Yükseliş Trendine Giren Hisseler (Support → Resistance)
    print("\n📈 ADIM 4: Trend Analizi (Support → Resistance Geçişleri)")
    print("-" * 70)
    trend_opportunities = analyze_trend_reversals(all_analysis)
    
    if trend_opportunities:
        print(f"✅ {len(trend_opportunities)} hisse yükseliş trendine girdi:")
        for opp in trend_opportunities[:5]:
            print(f"   {opp['ticker']} - Destek: {opp['support']}, Direnç: {opp['resistance']}")
    else:
        print("⚠️  Trend geçişi bulunamadı")
    
    # ADIM 5: Recommendation Oluştur
    print("\n📋 ADIM 5: Recommendation Oluştur")
    print("-" * 70)
    recommendations = generate_recommendation_text(selected, sector_scores)
    recommendations["global_analysis"] = global_analysis
    recommendations["trend_opportunities"] = trend_opportunities
    
    print(f"✅ {len(recommendations.get('recommendations', []))} hisse önerisi hazırlandı")
    
    # ADIM 6: Grafikler Oluştur
    print("\n📈 ADIM 6: Grafikler Oluştur")
    print("-" * 70)
    chart_paths = []
    
    for stock in selected:
        try:
            ticker = stock.get("ticker", "")
            df = stock.get("dataframe", None)
            
            if df is not None and not df.empty:
                chart_path = generate_charts(ticker, df)
                if chart_path and os.path.exists(chart_path):
                    chart_paths.append(chart_path)
                    print(f"✅ {ticker} grafiği oluşturuldu")
        except Exception as e:
            print(f"⚠️  {ticker} grafik hatası: {e}")
    
    # ADIM 7: HTML Email Oluştur
    print("\n📧 ADIM 7: HTML Email Oluştur")
    print("-" * 70)
    html_body = generate_html_body(recommendations, chart_paths)
    print(f"✅ HTML email oluşturuldu ({len(html_body)} karakter)")
    
    # ADIM 8: Email Gönder
    print("\n🚀 ADIM 8: Email Gönder")
    print("-" * 70)
    subject = f"📊 Borsa Analiz - {datetime.now().strftime('%d %b %Y')}"
    
    if send_email(html_body, chart_paths, subject):
        print("✅ Analiz tamamlandı ve email gönderildi!")
        return True
    else:
        print("❌ Email gönderme başarısız!")
        return False


def analyze_trend_reversals(all_analysis):
    """
    Yükseliş trendine giren ve destek seviyesini dirençe dönüştüren hisseleri bul
    """
    opportunities = []
    
    for stock in all_analysis:
        try:
            if stock.get("skip"):
                continue
            
            ticker = stock.get("ticker", "")
            df = stock.get("dataframe", None)
            
            if df is None or df.empty:
                continue
            
            close = df["Close"].squeeze()
            
            # Son 60 günün low'u (destek)
            support_level = float(close.tail(60).min())
            
            # Son 60 günün high'ı (direnç)
            resistance_level = float(close.tail(60).max())
            
            # Şu anki fiyat
            current_price = float(close.iloc[-1])
            
            # Destek seviyesini geçip yükselmişse
            if current_price > support_level * 1.02:  # Destek üzerinde
                
                # SMA 50 yukarıda mı?
                sma_50 = float(close.rolling(window=50).mean().iloc[-1])
                
                # Momentum pozitif mi?
                momentum = ((close.iloc[-1] - close.iloc[-10]) / close.iloc[-10] * 100)
                
                if current_price > sma_50 and momentum > 0:
                    opportunities.append({
                        "ticker": ticker,
                        "sector": stock.get("sector", "genel"),
                        "current_price": round(current_price, 2),
                        "support": round(support_level, 2),
                        "resistance": round(resistance_level, 2),
                        "momentum": round(momentum, 2),
                        "breakout_strength": round((current_price - support_level) / support_level * 100, 2),
                        "potential_upside": round((resistance_level - current_price) / current_price * 100, 2)
                    })
        
        except Exception as e:
            pass
    
    # En güçlü kırılışları seç
    opportunities.sort(key=lambda x: x["breakout_strength"], reverse=True)
    
    return opportunities[:10]  # Top 10


def schedule_bot():
    """Bot'u belirli saatlerde çalıştır"""
    
    # Pazartesi-Cuma 09:30'de çalıştır
    schedule.every().monday.at(f"{config.DAILY_RUN_HOUR:02d}:{config.DAILY_RUN_MINUTE:02d}").do(run_analysis)
    schedule.every().tuesday.at(f"{config.DAILY_RUN_HOUR:02d}:{config.DAILY_RUN_MINUTE:02d}").do(run_analysis)
    schedule.every().wednesday.at(f"{config.DAILY_RUN_HOUR:02d}:{config.DAILY_RUN_MINUTE:02d}").do(run_analysis)
    schedule.every().thursday.at(f"{config.DAILY_RUN_HOUR:02d}:{config.DAILY_RUN_MINUTE:02d}").do(run_analysis)
    schedule.every().friday.at(f"{config.DAILY_RUN_HOUR:02d}:{config.DAILY_RUN_MINUTE:02d}").do(run_analysis)
    
    print(f"✅ Bot çizelgesi ayarlandı: Her gün {config.DAILY_RUN_HOUR:02d}:{config.DAILY_RUN_MINUTE:02d}")
    
    # Scheduler'ı çalıştır
    while True:
        schedule.run_pending()
        time.sleep(60)


if __name__ == "__main__":
    
    if len(sys.argv) > 1 and sys.argv[1] == "once":
        # Tek seferlik çalıştır
        print("🎯 Tek seferlik analiz modu")
        run_analysis()
    
    else:
        # Scheduler modu
        print("📅 Scheduler modu (Ctrl+C ile durdur)")
        schedule_bot()
