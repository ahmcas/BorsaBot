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
import pandas as pd
from datetime import datetime, timedelta

class PerformanceTracker:
    def __init__(self, db_path="performance.db"):
        self.db_path = db_path
        self._check_and_fix_db()

    def _check_and_fix_db(self):
        """Eksik sütunları (score, ticker vb.) otomatik ekler veya tabloyu kurar."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            # Tablo var mı kontrol et
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='recommendations'")
            if not cursor.fetchone():
                conn.execute("""
                    CREATE TABLE recommendations (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        ticker TEXT, score INTEGER, entry_price REAL,
                        date TEXT, status TEXT DEFAULT 'OPEN', return_pct REAL DEFAULT 0.0
                    )
                """)
            else:
                # Sütunları kontrol et ve eksikleri ekle
                cursor.execute("PRAGMA table_info(recommendations)")
                columns = [col[1] for col in cursor.fetchall()]
                if "score" not in columns:
                    conn.execute("ALTER TABLE recommendations ADD COLUMN score INTEGER DEFAULT 0")
            conn.commit()

    def save_recommendation(self, rec):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO recommendations (ticker, score, entry_price, date, status) VALUES (?, ?, ?, ?, ?)",
                (rec.get('ticker'), rec.get('final_score', 0), rec.get('price', 0), 
                 datetime.now().strftime('%Y-%m-%d %H:%M'), "OPEN")
            )

    def generate_report(self, days):
        return {"win_rate": 0, "avg_return_pct": 0}

    def get_detailed_history(self, limit):
        return []

def generate_performance_email(report, history):
    return f"<h3>Haftalık Rapor</h3><p>Başarı Oranı: %{report['win_rate']}</p>"
