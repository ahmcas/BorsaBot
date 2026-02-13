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

    def _create_table(self):
        """Veritabanı ve tabloyu oluşturur."""
        with sqlite3.connect(self.db_path) as conn:
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
            return True
        except Exception as e:
            print(f"❌ Veritabanı kayıt hatası: {e}")
            return False

    def check_performance(self, days_list):
        """
        Geçmiş önerilerin performansını kontrol eder ve günceller.
        (Burada yfinance veya benzeri bir kütüphane ile güncel fiyat çekilebilir)
        """
        # Şimdilik mevcut kayıtları listeler, analiz mantığı buraya eklenebilir.
        with sqlite3.connect(self.db_path) as conn:
            query = "SELECT * FROM recommendations WHERE status = 'OPEN'"
            df = pd.read_sql_query(query, conn)
            return df.to_dict('records')

    def generate_report(self, days=30):
        """Belirli bir gün aralığı için özet rapor üretir."""
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
        """Son yapılan önerilerin listesini getirir."""
        with sqlite3.connect(self.db_path) as conn:
            query = "SELECT ticker, score, date, return_pct FROM recommendations ORDER BY date DESC LIMIT ?"
            df = pd.read_sql_query(query, conn, params=(limit,))
            return df.to_dict('records')

def generate_performance_email(report, history):
    """
    Görüntüdeki hatayı çözen fonksiyon. 
    Main botun beklediği HTML formatında performans özeti üretir.
    """
    html_template = f"""
    <div style="font-family: Arial, sans-serif; border: 1px solid #ddd; padding: 20px; border-radius: 10px;">
        <h2 style="color: #2c3e50;">📊 Performans Raporu</h2>
        <p><b>Son {report.get('total', 0)} Öneri Özeti:</b></p>
        <table style="width: 100%; border-collapse: collapse;">
            <tr style="background-color: #f8f9fa;">
                <th style="padding: 10px; border: 1px solid #ddd;">Başarı Oranı</th>
                <th style="padding: 10px; border: 1px solid #ddd;">Ort. Getiri</th>
            </tr>
            <tr>
                <td style="padding: 10px; border: 1px solid #ddd; text-align: center;">%{report['win_rate']}</td>
                <td style="padding: 10px; border: 1px solid #ddd; text-align: center;">%{report['avg_return_pct']}</td>
            </tr>
        </table>
        <h3 style="color: #2c3e50; margin-top: 20px;">🔍 Son İşlemler</h3>
        <ul style="list-style: none; padding: 0;">
    """
    
    for item in history:
        color = "green" if item['return_pct'] >= 0 else "red"
        html_template += f"""
            <li style="padding: 8px; border-bottom: 1px solid #eee;">
                <b>{item['ticker']}</b> - Skor: {item['score']} | 
                <span style="color: {color}; font-weight: bold;">%{item['return_pct']}</span> 
                ({item['date']})
            </li>
        """
    
    html_template += "</ul></div>"
    return html_template
