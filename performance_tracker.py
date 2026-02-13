# ============================================================
# performance_tracker.py — Performans Takip Sistemi
# ============================================================
# Bu modül:
# 1) Her gün yapılan önerileri SQLite DB'ye kaydeder
# 2) 7, 14, 30 gün sonra gerçek sonuçları kontrol eder
# 3) Başarı oranını hesaplar ve raporlar
# 4) Hangi sinyallerin daha başarılı olduğunu analiz eder
# ============================================================

import sqlite3
import yfinance as yf
from datetime import datetime, timedelta

DB_NAME = "performance.db"

def get_price(symbol, date):
    try:
        data = yf.download(symbol, start=date, end=date + timedelta(days=5), progress=False)
        if data.empty:
            return None
        return float(data["Close"].iloc[0])
    except:
        return None


def update_performance():

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS performance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT,
            recommendation_date TEXT,
            price_at_recommendation REAL,
            price_7d REAL,
            price_14d REAL,
            price_30d REAL,
            checked_7d INTEGER DEFAULT 0,
            checked_14d INTEGER DEFAULT 0,
            checked_30d INTEGER DEFAULT 0
        )
    """)

    conn.commit()

    cursor.execute("SELECT * FROM performance")
    rows = cursor.fetchall()

    today = datetime.now().date()

    for row in rows:
        id, symbol, rec_date, rec_price, p7, p14, p30, c7, c14, c30 = row

        rec_date = datetime.strptime(rec_date, "%Y-%m-%d").date()

        if not c7 and (today - rec_date).days >= 7:
            price = get_price(symbol, rec_date + timedelta(days=7))
            if price:
                cursor.execute("UPDATE performance SET price_7d=?, checked_7d=1 WHERE id=?", (price, id))

        if not c14 and (today - rec_date).days >= 14:
            price = get_price(symbol, rec_date + timedelta(days=14))
            if price:
                cursor.execute("UPDATE performance SET price_14d=?, checked_14d=1 WHERE id=?", (price, id))

        if not c30 and (today - rec_date).days >= 30:
            price = get_price(symbol, rec_date + timedelta(days=30))
            if price:
                cursor.execute("UPDATE performance SET price_30d=?, checked_30d=1 WHERE id=?", (price, id))

    conn.commit()
    conn.close()


def generate_summary():

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM performance WHERE checked_30d=1")
    rows = cursor.fetchall()

    total = len(rows)
    success = 0
    best_stock = None
    best_return = -999

    for row in rows:
        _, symbol, _, rec_price, _, _, p30, *_ = row

        if p30 and rec_price:
            change = ((p30 - rec_price) / rec_price) * 100

            if change > 0:
                success += 1

            if change > best_return:
                best_return = change
                best_stock = symbol

    conn.close()

    success_rate = (success / total * 100) if total > 0 else 0

    summary = f"""
PERFORMANS RAPORU
------------------------
Toplam Ölçülen: {total}
Başarılı: {success}
Başarı Oranı: %{round(success_rate,2)}
En İyi Hisse (30g): {best_stock} %{round(best_return,2)}
"""

    return summary
