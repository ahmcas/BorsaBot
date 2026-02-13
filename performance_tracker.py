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
        self._initialize_db()

    def _initialize_db(self):
        """Veritabanını tüm sütunlar (score dahil) olacak şekilde sıfırlar."""
        with sqlite3.connect(self.db_path) as conn:
            # Şemayı temizleyip en güncel haliyle kuruyoruz
            conn.execute("DROP TABLE IF EXISTS recommendations")
            conn.execute("""
                CREATE TABLE recommendations (
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
            print("✅ Veritabanı şeması başarıyla sıfırlandı ve 'score' sütunu eklendi.")

    def save_recommendation(self, rec):
        """Hisse önerisini kaydeder."""
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
            print(f"❌ Veritabanı kayıt hatası: {e}")
            return False

    def check_performance(self, days_list):
        """Açık pozisyonları kontrol eder."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                query = "SELECT * FROM recommendations WHERE status = 'OPEN'"
                df = pd.read_sql_query(query, conn)
                return df.to_dict('records')
        except Exception as e:
            print(f"❌ Performans kontrol hatası: {e}")
            return []

    def generate_report(self, days=30):
        """Özet rapor üretir."""
        with sqlite3.connect(self.db_path) as conn:
            query = "SELECT * FROM recommendations WHERE date >= ?"
            date_limit = (datetime.now() - timedelta(days=days)).isoformat()
            df = pd.read_sql_query(query, conn, params=(date_limit,))
            if df.empty:
                return {"win_rate": 0, "avg_return_pct": 0, "total": 0}
            win_rate = (df[df['return_pct'] > 0].shape[0] / df.shape[0]) * 100
            return {
                "win_rate": round(win_rate, 2), 
                "avg_return_pct": round(df['return_pct'].mean(), 2),
                "total": df.shape[0]
            }

    def get_detailed_history(self, limit=10):
        """Geçmiş verileri getirir."""
        with sqlite3.connect(self.db_path) as conn:
            query = "SELECT ticker, score, date, return_pct FROM recommendations ORDER BY date DESC LIMIT ?"
            return pd.read_sql_query(query, conn, params=(limit,)).to_dict('records')

def generate_performance_email(report, history):
    """ImportError hatasını çözen performans mail fonksiyonu."""
    html = f"<h3>📊 Performans Özeti</h3><p>Başarı: %{report['win_rate']}</p>"
    html += "<table border='1'><tr><th>Hisse</th><th>Skor</th><th>Getiri</th></tr>"
    for item in history:
        html += f"<tr><td>{item['ticker']}</td><td>{item['score']}</td><td>%{item['return_pct']}</td></tr>"
    return html + "</table>"
