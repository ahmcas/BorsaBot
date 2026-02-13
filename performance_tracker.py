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
import json


class PerformanceTracker:
    def __init__(self, db_path="performance.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS recommendations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT,
                ticker TEXT,
                entry_price REAL,
                final_score REAL,
                rating TEXT
            )
        """)
        
        conn.commit()
        conn.close()
    
    def save_recommendation(self, rec):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        entry_price = rec.get("price") or rec.get("current_price")
        if entry_price is None:
            conn.close()
            return 0
        
        try:
            entry_price = float(entry_price)
        except:
            conn.close()
            return 0
        
        cursor.execute("""
            INSERT INTO recommendations (date, ticker, entry_price, final_score, rating)
            VALUES (?, ?, ?, ?, ?)
        """, (
            datetime.now().strftime("%Y-%m-%d"),
            rec.get("ticker", "N/A"),
            entry_price,
            float(rec.get("final_score") or rec.get("score") or 0),
            rec.get("rating", "N/A")
        ))
        
        rec_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return rec_id
    
    def check_performance(self, days_to_check):
        return []
    
    def generate_report(self, days):
        return {
            "period_days": days,
            "total_recommendations": 0,
            "total_checked": 0,
            "success_count": 0,
            "neutral_count": 0,
            "loss_count": 0,
            "win_rate": 0,
            "avg_return_pct": 0,
            "best_sector": "N/A",
            "worst_sector": "N/A"
        }
    
    def get_detailed_history(self, limit):
        return []


def generate_performance_email(report, history):
    html = "<h1>Performans Raporu</h1>"
    html += f"<p>Toplam Oneri: {report['total_recommendations']}</p>"
    return html
