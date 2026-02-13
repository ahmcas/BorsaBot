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
import smtplib
import yfinance as yf
import matplotlib.pyplot as plt

from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from performance_tracker import PerformanceTracker


# ==============================
# HİSSE LİSTESİ (KOZAL / KOZAA ÇIKARILDI)
# ==============================

STOCKS = [
    "TCELL.IS",
    "OTKAR.IS",
    "AKSA.IS",
    "ALARK.IS"
]


# ==============================
# ANALİZ
# ==============================

def analyze_stock(symbol):
    try:
        data = yf.download(symbol, period="3mo", progress=False)

        if data.empty or len(data) < 60:
            return None

        close = data["Close"]

        ma20 = close.rolling(20).mean().iloc[-1]
        ma50 = close.rolling(50).mean().iloc[-1]
        last_price = close.iloc[-1]

        # Scalar dönüşüm
        ma20 = float(ma20.item())
        ma50 = float(ma50.item())
        last_price = float(last_price.item())

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
            "score": score,
            "data": data
        }

    except Exception as e:
        print(f"{symbol} analiz hatası: {e}")
        return None


# ==============================
# GRAFİK ÜRETİM
# ==============================

def generate_chart(symbol, data):
    os.makedirs("charts", exist_ok=True)

    plt.figure()
    plt.plot(data["Close"])
    plt.title(symbol)
    plt.xlabel("Tarih")
    plt.ylabel("Fiyat")

    filename = f"charts/{symbol.replace('.', '_')}.png"
    plt.savefig(filename)
    plt.close()

    return filename


# ==============================
# EMAIL
# ==============================

def send_email(subject, body, image_paths):

    sender = os.getenv("MAIL_SENDER")
    password = os.getenv("MAIL_PASSWORD")
    recipient = os.getenv("MAIL_RECIPIENT")

    msg = MIMEMultipart()
    msg["From"] = sender
    msg["To"] = recipient
    msg["Subject"] = subject

    msg.attach(MIMEText(body, "html"))

    for path in image_paths:
        with open(path, "rb") as f:
            img = MIMEImage(f.read())
            img.add_header("Content-Disposition", "attachment", filename=os.path.basename(path))
            msg.attach(img)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender, password)
        server.sendmail(sender, recipient, msg.as_string())

    print("Email gönderildi.")


# ==============================
# ANA AKIŞ
# ==============================

def main():

    print("🚀 Borsa Bot Başladı")

    selected = []
    image_paths = []

    # ANALİZ
    for symbol in STOCKS:
        result = analyze_stock(symbol)

        if result:
            print(f"{symbol} analiz edildi | Skor: {result['score']}")

            if result["score"] >= 60:
                selected.append(result)

    if not selected:
        print("Seçilen hisse yok.")
        return

    # GRAFİK ÜRET
    for stock in selected:
        path = generate_chart(stock["symbol"], stock["data"])
        image_paths.append(path)

    # PERFORMANCE
    tracker = PerformanceTracker()

    for stock in selected:
        tracker.add_recommendation(
            symbol=stock["symbol"],
            entry_price=stock["price"],
            final_score=stock["score"]
        )

    tracker.update_prices()

    report_7 = tracker.generate_report(7)
    report_14 = tracker.generate_report(14)
    report_30 = tracker.generate_report(30)

    report = None
    period = ""

    if report_30.get("total", 0) > 0:
        report = report_30
        period = "30 Gün"
    elif report_14.get("total", 0) > 0:
        report = report_14
        period = "14 Gün"
    elif report_7.get("total", 0) > 0:
        report = report_7
        period = "7 Gün"

    # EMAIL BODY (HTML)
    body = f"""
    <h2>📊 Borsa Analiz Raporu</h2>
    <p>Tarih: {datetime.now().strftime('%d %B %Y')}</p>
    <h3>Seçilen Hisseler</h3>
    """

    for s in selected:
        body += f"<p><b>{s['symbol']}</b> | Skor: {s['score']} | Fiyat: {round(s['price'],2)}</p>"

    if report:
        body += f"""
        <h3>📈 {period} Performans</h3>
        <p>Toplam: {report['total']}</p>
        <p>Başarı Oranı: %{report['win_rate']}</p>
        <p>Ortalama Getiri: %{report['avg_return']}</p>
        """

    send_email(
        subject=f"📊 Borsa Analiz Raporu - {datetime.now().strftime('%d %b %Y')}",
        body=body,
        image_paths=image_paths
    )

    print("✅ Bot tamamlandı.")


if __name__ == "__main__":
    main()
