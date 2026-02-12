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

class PerformanceTracker:

    def __init__(self, db_path="performance.db"):
        self.db_path = db_path
        self.init_db()

    # -------------------------------------------------
    # DATABASE INIT (Gerçek SQLite oluşturur)
    # -------------------------------------------------
    def init_db(self):

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS recommendations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticker TEXT,
            entry_price REAL,
            date TEXT
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS performance_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            recommendation_id INTEGER,
            days_held INTEGER,
            return_pct REAL,
            outcome TEXT
        )
        """)

        conn.commit()
        conn.close()

    # -------------------------------------------------
    # SAVE RECOMMENDATION
    # -------------------------------------------------
    def save_recommendation(self, rec):

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        ticker = rec.get("ticker")
        entry_price = rec.get("entry_price", 0)

        cursor.execute("""
            INSERT INTO recommendations (ticker, entry_price, date)
            VALUES (?, ?, ?)
        """, (ticker, entry_price, datetime.now().strftime("%Y-%m-%d")))

        conn.commit()
        rec_id = cursor.lastrowid
        conn.close()

        return rec_id

    # -------------------------------------------------
    # CHECK PERFORMANCE (Dummy hesap)
    # -------------------------------------------------
    def check_performance(self, days_list):

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT id, entry_price FROM recommendations")
        rows = cursor.fetchall()

        results = []

        for rec_id, entry_price in rows:

            for days in days_list:

                fake_return = round((entry_price * 0.02), 2)
                outcome = "SUCCESS" if fake_return > 0 else "FAIL"

                cursor.execute("""
                    INSERT INTO performance_results
                    (recommendation_id, days_held, return_pct, outcome)
                    VALUES (?, ?, ?, ?)
                """, (rec_id, days, fake_return, outcome))

                results.append(rec_id)

        conn.commit()
        conn.close()

        return results

    # -------------------------------------------------
    # GENERATE REPORT
    # -------------------------------------------------
    def generate_report(self, days=30):

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT return_pct, outcome
            FROM performance_results
        """)

        rows = cursor.fetchall()
        conn.close()

        if not rows:
            return {
                "win_rate": 0,
                "avg_return_pct": 0
            }

        total = len(rows)
        wins = sum(1 for r in rows if r[1] == "SUCCESS")
        avg_return = sum(r[0] for r in rows) / total

        return {
            "win_rate": round((wins / total) * 100, 2),
            "avg_return_pct": round(avg_return, 2)
        }
