# ============================================================
# main_bot.py — Ana Orchestrator (v6 - KOMPLE FINAL)
# ============================================================
# Tüm modülleri koordine eden ana dosya
# Çalışma modları:
# - once: Tek seferlik çalıştır
# - once --quick: Hızlı test (5 hisse)
# - test: Test mode
# - (boş): Scheduler mode (her gün 09:30)
# ============================================================

import os
import sys
import logging
from datetime import datetime, timedelta
import traceback
import config
# (tüm importlar, fonksiyonlar aynen)

# Copilot: Tatil uyarılarını gösteren fonksiyon
def get_holiday_warnings(holidays):
    today = datetime.today()
    warnings = []
    for country, hlist in holidays.items():
        for h in hlist:
            start = datetime.strptime(h['start'], '%Y-%m-%d')
            days_left = (start - today).days
            if 0 < days_left <= 7:
                warnings.append(f"🇺🇸 {country} — {h['name']} [{h['start']}]: {days_left} gün kaldı! ({h.get('impact','')})")
            elif days_left > 7:
                warnings.append(f"🇺🇸 {country} — {h['name']} [{h['start']}]: {days_left} gün sonra (bilgilendirme)")
            elif days_left < 0 and days_left >= -7:
                warnings.append(f"🇺🇸 {country} — {h['name']} [{h['start']}]: Tatil sona erdi, piyasada normale dönüş bekleniyor.")
    return warnings

def run_analysis(quick: bool = False):
    try:
        # ... (başlangıç ve ADIM 1, ADIM 2 aynen)
        # ADIM 3 ve teknik analiz aşamaları aynen
        
        # ADIM 4: Skor Hesaplama ve Öneri Tamamlama
        selected = select_top_stocks(technical_results, sector_scores, max_count=config.MAX_RECOMMENDATIONS)
        for s in selected:
            s['source_pool'] = '🎯 Hedef Sektör'

        if len(selected) < config.MAX_RECOMMENDATIONS:
            already_tickers = [s['ticker'] for s in selected]
            remaining_stocks = [ticker for ticker in config.ALL_STOCKS if ticker not in stocks_to_analyze and ticker not in already_tickers]
            remaining_results = analyze_all_stocks(remaining_stocks)
            remaining_selected = select_top_stocks(remaining_results, sector_scores, max_count=config.MAX_RECOMMENDATIONS - len(selected))
            for s in remaining_selected:
                s['source_pool'] = '🌍 Genel Havuz'
            selected += remaining_selected
            technical_results += remaining_results
            print(f"⚠️  Hedef sektörden sadece {len(selected) - len(remaining_selected)} hisse seçildi, kalan havuzdan {len(remaining_selected)} eklendi!")

        for idx, stock in enumerate(selected, 1):
            print(f"   {idx}. {stock.get('ticker', '?'):10s} - Skor: {stock.get('score', 0):6.1f} | R/R: {stock.get('reward_risk_ratio', 0):.2f} | {stock.get('source_pool', '')}")

        # ... (mail hazırlama ve diğer adımlar aynı)
        # Copilot: Tatil uyarılarını göster
        holiday_warnings = get_holiday_warnings(config.MARKET_HOLIDAYS_2026)
        print("\n📅 Tatil ve Volatilite Uyarısı")
        for w in holiday_warnings:
            print(w)

        # ... (analiz özeti ve son kapanışlar aynı)
    except Exception as e:
        # ... (hata blokları aynı)

# ... (main fonksiyonu ve dosya sonu aynı)
