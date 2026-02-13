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
from datetime import datetime, timedelta
import yfinance as yf

DB_NAME = "performance.db"


class PerformanceTracker:

    def __init__(self):
        self.conn = sqlite3.connect(DB_NAME)
        self.cursor = self.conn.cursor()
        self._create_table()

    def _create_table(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS performance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticker TEXT,
                recommendation_date TEXT,
                price_at_rec REAL,
                price_7d REAL,
                price_14d REAL,
                price_30d REAL
            )
        """)
        self.conn.commit()

    def _get_price(self, ticker):
        try:
            data = yf.download(ticker, period="1d", progress=False)
            if data.empty:
                return None
            return float(data["Close"].iloc[-1])
        except:
            return None

    def save_recommendation(self, rec):
        ticker = rec["ticker"]
        today = datetime.now().strftime("%Y-%m-%d")
        price = self._get_price(ticker)

        self.cursor.execute("""
            INSERT INTO performance (ticker, recommendation_date, price_at_rec)
            VALUES (?, ?, ?)
        """, (ticker, today, price))

        self.conn.commit()
        return self.cursor.lastrowid

    def check_performance(self, days_list):

        self.cursor.execute("SELECT * FROM performance")
        rows = self.cursor.fetchall()
        updated = []

        for row in rows:
            id, ticker, rec_date, p_rec, p7, p14, p30 = row
            rec_date_dt = datetime.strptime(rec_date, "%Y-%m-%d")

            for d in days_list:
                target_date = rec_date_dt + timedelta(days=d)

                if datetime.now() >= target_date:

                    column_name = f"price_{d}d"
                    existing_value = row[3 + days_list.index(d)]

                    if existing_value is None:
                        price = self._get_price(ticker)

                        self.cursor.execute(
                            f"UPDATE performance SET {column_name}=? WHERE id=?",
                            (price, id)
                        )
                        updated.append(ticker)

        self.conn.commit()
        return updated

    def generate_report(self, days=30):

        col = f"price_{days}d"

        self.cursor.execute(f"""
            SELECT price_at_rec, {col}
            FROM performance
            WHERE {col} IS NOT NULL
        """)

        rows = self.cursor.fetchall()

        total = len(rows)
        wins = 0
        returns = []

        for rec, future in rows:
            if rec and future:
                pct = ((future - rec) / rec) * 100
                returns.append(pct)
                if pct > 0:
                    wins += 1

        win_rate = round((wins / total) * 100, 2) if total > 0 else 0
        avg_return = round(sum(returns) / len(returns), 2) if returns else 0

        return {
            "total": total,
            "win_rate": win_rate,
            "avg_return_pct": avg_return
        }

    def get_detailed_history(self, limit=20):
        self.cursor.execute("""
            SELECT ticker, recommendation_date, price_at_rec, price_30d
            FROM performance
            ORDER BY id DESC
            LIMIT ?
        """, (limit,))
        return self.cursor.fetchall()


def generate_performance_email(report, history):

    html = f"""
    <h2>📊 Performans Raporu</h2>
    <p><b>Toplam İşlem:</b> {report['total']}</p>
    <p><b>Başarı Oranı:</b> %{report['win_rate']}</p>
    <p><b>Ortalama Getiri:</b> %{report['avg_return_pct']}</p>
    <hr>
    <h3>Son İşlemler</h3>
    """

    for h in history:
        html += f"<p>{h[0]} | {h[1]}</p>"

    return html
