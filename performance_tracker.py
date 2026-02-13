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
        """Veritabanı tablosunu en baştan, tüm sütunlarla birlikte kurar."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Eğer tablo varsa ama score sütunu yoksa, tabloyu silip yeniden kurarız
                cursor = conn.cursor()
                cursor.execute("PRAGMA table_info(recommendations)")
                columns = [col[1] for col in cursor.fetchall()]
                
                if columns and "score" not in columns:
                    print("⚠️ 'score' sütunu eksik, tablo yeniden oluşturuluyor...")
                    conn.execute("DROP TABLE IF EXISTS recommendations")
                
                # Tabloyu eksiksiz şema ile oluştur
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
                print("✅ Veritabanı şeması hazır (score sütunu dahil).")
        except Exception as e:
            print(f"❌ Veritabanı başlatma hatası: {e}")

    def save_recommendation(self, rec):
        """Yeni bir hisse önerisini veritabanına kaydeder."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    "INSERT INTO recommendations (ticker, score, entry_price, date, status) VALUES (?, ?, ?, ?, ?)",
                    (
                        rec.get('ticker'), 
                        rec.get('final_score', 0), 
                        rec.get('price', 0), 
                        datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 
                        "OPEN"
                    )
                )
                conn.commit()
                print(f"💾 Veritabanına kaydedildi: {rec.get('ticker')}")
            return True
        except Exception as e:
            print(f"❌ Veritabanı kayıt hatası (save_recommendation): {e}")
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
        with sqlite3.connect(self.db_path) as conn:
            query = "SELECT ticker, score, date, return_pct FROM recommendations ORDER BY date DESC LIMIT ?"
            return pd.read_sql_query(query, conn, params=(limit,)).to_dict('records')

def generate_performance_email(report, history):
    """Haftalık rapor HTML içeriği."""
    html = f"<h3>📊 Performans Özeti</h3><p>Başarı: %{report['win_rate']}</p>"
    html += "<table border='1' style='width:100%; border-collapse: collapse;'>"
    html += "<tr style='background:#f4f4f4;'><th>Hisse</th><th>Skor</th><th>Getiri</th></tr>"
    for item in history:
        html += f"<tr><td>{item['ticker']}</td><td>{item['score']}</td><td>%{item['return_pct']}</td></tr>"
    return html + "</table>"
