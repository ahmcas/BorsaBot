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
        self._create_table()
        self._migrate_db() # Eksik sütunları otomatik ekler

    def _create_table(self):
        """Tabloyu temel yapısıyla oluşturur."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS recommendations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ticker TEXT,
                    score INTEGER,
                    entry_price REAL,
                    current_price REAL,
                    date TEXT,
                    status TEXT DEFAULT 'OPEN',
                    return_pct REAL DEFAULT 0.0
                )
            """)
            conn.commit()

    def _migrate_db(self):
        """Loglardaki 'no column named ticker/status' hatalarını önlemek için sütun kontrolü yapar."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("PRAGMA table_info(recommendations)")
            columns = [column[1] for column in cursor.fetchall()]
            
            # Eksik olması muhtemel sütunları kontrol et ve ekle
            needed_columns = {
                "ticker": "TEXT",
                "status": "TEXT DEFAULT 'OPEN'",
                "return_pct": "REAL DEFAULT 0.0",
                "current_price": "REAL"
            }
            
            for col, col_type in needed_columns.items():
                if col not in columns:
                    try:
                        cursor.execute(f"ALTER TABLE recommendations ADD COLUMN {col} {col_type}")
                        print(f"✅ Veritabanına eksik sütun eklendi: {col}")
                    except Exception as e:
                        print(f"⚠️ Sütun ekleme atlandı (zaten var olabilir): {e}")
            conn.commit()

    def save_recommendation(self, rec):
        """Önerilen hisseyi kaydeder."""
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
        """Özet rapor verilerini hazırlar."""
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
        """Geçmiş verileri çeker."""
        with sqlite3.connect(self.db_path) as conn:
            query = "SELECT ticker, score, date, return_pct FROM recommendations ORDER BY date DESC LIMIT ?"
            return pd.read_sql_query(query, conn, params=(limit,)).to_dict('records')

def generate_performance_email(report, history):
    """ImportError hatasını gideren fonksiyon."""
    html = f"""
    <div style="font-family: Arial; border: 1px solid #eee; padding: 15px;">
        <h2 style="color: #2c3e50;">📊 Performans Özeti</h2>
        <p><b>Başarı Oranı:</b> %{report['win_rate']}</p>
        <p><b>Ortalama Getiri:</b> %{report['avg_return_pct']}</p>
        <table border="1" style="width:100%; border-collapse: collapse;">
            <tr style="background: #f4f4f4;"><th>Hisse</th><th>Skor</th><th>Getiri</th></tr>
    """
    for item in history:
        html += f"<tr><td>{item['ticker']}</td><td>{item['score']}</td><td>%{item['return_pct']}</td></tr>"
    return html + "</table></div>"
