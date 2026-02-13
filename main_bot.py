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

import os
from datetime import datetime
import yfinance as yf
from performance_tracker import PerformanceTracker
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib


# ==============================
# HİSSE LİSTESİ
# ==============================

STOCKS = [
    "TCELL.IS",
    "OTKAR.IS",
    "AKSA.IS",
    "ALARK.IS",
    "KOZAL.IS",
    "KOZAA.IS"
]


# ==============================
# BASİT SKOR HESABI
# ==============================

def analyze_stock(symbol):
    data = yf.download(symbol, period="3mo", progress=False)

    if data.empty:
        return None

    close = data["Close"]

    ma20 = close.rolling(20).mean().iloc[-1]
    ma50 = close.rolling(50).mean().iloc[-1]
    last_price = float(close.iloc[-1].item())

    score = 0

    if last_price > ma20:
        score += 40
    if last_price > ma50:
        score += 40
    if ma20 > ma50:
        score += 20

    return {
        "symbol": symbol,
        "price": last_price,
        "score": score
    }


# ==============================
# EMAIL GÖNDERME
# ==============================

def send_email(body, subject):
    sender = os.getenv("MAIL_SENDER")
    password = os.getenv("MAIL_PASSWORD")
    recipient = os.getenv("MAIL_RECIPIENT")

    msg = MIMEMultipart()
    msg["From"] = sender
    msg["To"] = recipient
    msg["Subject"] = subject

    msg.attach(MIMEText(body, "plain"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender, password)
        server.sendmail(sender, recipient, msg.as_string())


# ==============================
# ANA AKIŞ
# ==============================

def main():

    print("🚀 Borsa Bot Başladı")
    print("=" * 50)

    selected = []

    for symbol in STOCKS:
        result = analyze_stock(symbol)

        if result:
            print(f"{symbol} analiz edildi | Skor: {result['score']}")
            if result["score"] >= 60:
                selected.append(result)

    if not selected:
        print("Seçilen hisse yok.")
        return

    print("\n🏆 Seçilen Hisseler:")
    for s in selected:
        print(f"{s['symbol']} | Skor: {s['score']}")

    # ==============================
    # PERFORMANCE KAYIT
    # ==============================

    tracker = PerformanceTracker()

    for stock in selected:
        tracker.add_recommendation(
            symbol=stock["symbol"],
            entry_price=stock["price"],
            final_score=stock["score"]
        )

    tracker.update_prices()

    # ==============================
    # RAPOR OLUŞTUR
    # ==============================

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

    # ==============================
    # EMAIL İÇERİĞİ
    # ==============================

    email_body = "📊 BORSA ANALİZ RAPORU\n"
    email_body += f"Tarih: {datetime.now().strftime('%d %B %Y')}\n\n"

    email_body += "Seçilen Hisseler:\n"

    for s in selected:
        email_body += f"{s['symbol']} | Skor: {s['score']} | Fiyat: {round(s['price'],2)}\n"

    if report:
        email_body += "\n"
        email_body += f"📈 {period} Performans Özeti\n"
        email_body += f"Toplam İşlem: {report['total']}\n"
        email_body += f"Başarı Oranı: %{report['win_rate']}\n"
        email_body += f"Ortalama Getiri: %{report['avg_return']}\n\n"

        email_body += "Detay:\n"
        for symbol, change in report["history"]:
            email_body += f"{symbol} → %{change}\n"
    else:
        email_body += "\nHenüz ölçülebilir performans verisi yok.\n"

    send_email(
        email_body,
        subject=f"📊 Borsa Analiz Raporu - {datetime.now().strftime('%d %b %Y')}"
    )

    print("\n✅ Bot tamamlandı.")


if __name__ == "__main__":
    main()
