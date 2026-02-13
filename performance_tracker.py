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
        self._ensure_correct_schema()

    def _ensure_correct_schema(self):
        """Tabloyu kontrol eder, 'score' yoksa silip yeniden oluşturur."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            try:
                cursor.execute("SELECT score FROM recommendations LIMIT 1")
            except sqlite3.OperationalError:
                print("⚠️ 'score' sütunu bulunamadı, tablo sıfırlanıyor...")
                conn.execute("DROP TABLE IF EXISTS recommendations")
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS recommendations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ticker TEXT NOT NULL,
                    score INTEGER,
                    entry_price REAL,
                    current_price REAL,
                    date TEXT,
                    status TEXT DEFAULT 'OPEN',
                    return_pct REAL DEFAULT 0.0
                )
            """)
            conn.commit()

    def save_recommendation(self, rec):
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    "INSERT INTO recommendations (ticker, score, entry_price, date, status) VALUES (?, ?, ?, ?, ?)",
                    (rec.get('ticker'), rec.get('final_score', 0), rec.get('price', 0), 
                     datetime.now().strftime('%Y-%m-%d %H:%M:%S'), "OPEN")
                )
                conn.commit()
            return True
        except Exception as e:
            print(f"❌ DB Kayıt Hatası: {e}")
            return False

    def check_performance(self, days_list):
        with sqlite3.connect(self.db_path) as conn:
            return pd.read_sql_query("SELECT * FROM recommendations WHERE status = 'OPEN'", conn).to_dict('records')

    def generate_report(self, days=30):
        with sqlite3.connect(self.db_path) as conn:
            query = "SELECT * FROM recommendations WHERE date >= ?"
            df = pd.read_sql_query(query, conn, params=((datetime.now() - timedelta(days=days)).isoformat(),))
            if df.empty: return {"win_rate": 0, "avg_return_pct": 0, "total": 0}
            return {"win_rate": round((df[df['return_pct'] > 0].shape[0] / df.shape[0]) * 100, 2), "avg_return_pct": round(df['return_pct'].mean(), 2), "total": df.shape[0]}

    def get_detailed_history(self, limit=10):
        with sqlite3.connect(self.db_path) as conn:
            return pd.read_sql_query("SELECT ticker, score, date, return_pct FROM recommendations ORDER BY date DESC LIMIT ?", conn, params=(limit,)).to_dict('records')

def generate_performance_email(report, history):
    html = f"<h3>📊 Performans Özeti</h3><p>Başarı: %{report['win_rate']}</p> <table border='1'><tr><th>Hisse</th><th>Skor</th></tr>"
    for item in history: html += f"<tr><td>{item['ticker']}</td><td>{item['score']}</td></tr>"
    return html + "</table>"
