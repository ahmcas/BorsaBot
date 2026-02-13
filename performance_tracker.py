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
from datetime import datetime
import yfinance as yf

DB_NAME = "performance.db"


class PerformanceTracker:

    def __init__(self):
        self.conn = sqlite3.connect(DB_NAME)
        self.create_table()

    def create_table(self):
        cursor = self.conn.cursor()

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS recommendations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT,
            recommendation_date TEXT,
            entry_price REAL,
            final_score REAL,
            price_7d REAL,
            price_14d REAL,
            price_30d REAL
        )
        """)

        # Migration kontrolü
        cursor.execute("PRAGMA table_info(recommendations)")
        columns = [col[1] for col in cursor.fetchall()]

        if "final_score" not in columns:
            cursor.execute("ALTER TABLE recommendations ADD COLUMN final_score REAL")

        self.conn.commit()

    def add_recommendation(self, symbol, entry_price, final_score):
        cursor = self.conn.cursor()
        cursor.execute("""
        INSERT INTO recommendations (symbol, recommendation_date, entry_price, final_score)
        VALUES (?, ?, ?, ?)
        """, (symbol, datetime.now().strftime("%Y-%m-%d"), entry_price, final_score))
        self.conn.commit()

    def update_prices(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, symbol, recommendation_date FROM recommendations")
        rows = cursor.fetchall()

        for row in rows:
            rec_id, symbol, rec_date = row
            rec_date_dt = datetime.strptime(rec_date, "%Y-%m-%d")
            days_passed = (datetime.now() - rec_date_dt).days

            data = yf.download(symbol, period="35d", progress=False)
            if data.empty:
                continue

            last_price = float(data["Close"].iloc[-1].item())

            if days_passed >= 7:
                cursor.execute("UPDATE recommendations SET price_7d=? WHERE id=?", (last_price, rec_id))
            if days_passed >= 14:
                cursor.execute("UPDATE recommendations SET price_14d=? WHERE id=?", (last_price, rec_id))
            if days_passed >= 30:
                cursor.execute("UPDATE recommendations SET price_30d=? WHERE id=?", (last_price, rec_id))

        self.conn.commit()

    def generate_report(self, days):
        cursor = self.conn.cursor()

        column = f"price_{days}d"

        cursor.execute(f"""
        SELECT symbol, entry_price, {column}
        FROM recommendations
        WHERE {column} IS NOT NULL
        """)

        rows = cursor.fetchall()

        if not rows:
            return {"total": 0}

        total = len(rows)
        wins = 0
        total_return = 0

        history = []

        for symbol, entry, exit_price in rows:
            change = ((exit_price - entry) / entry) * 100
            total_return += change
            if change > 0:
                wins += 1

            history.append((symbol, round(change, 2)))

        return {
            "total": total,
            "win_rate": round((wins / total) * 100, 2),
            "avg_return": round(total_return / total, 2),
            "history": history
        }
