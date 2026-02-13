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
import yfinance as yf
from datetime import datetime, timedelta
import json
from typing import List, Dict
import pandas as pd

class PerformanceTracker:
“”“Her önerinin performansını takip eder.”””

```
def __init__(self, db_path: str = "performance.db"):
    self.db_path = db_path
    self.init_database()

def init_database(self):
    """Veritabanı tablolarını oluştur."""
    conn = sqlite3.connect(self.db_path)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS recommendations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            ticker TEXT NOT NULL,
            entry_price REAL,
            technical_score REAL,
            final_score REAL,
            rating TEXT,
            sector TEXT,
            support_price REAL,
            resistance_price REAL,
            risk_pct REAL,
            reward_pct REAL,
            rr_ratio REAL,
            signals TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS performance_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            recommendation_id INTEGER NOT NULL,
            check_date TEXT NOT NULL,
            days_held INTEGER NOT NULL,
            exit_price REAL,
            return_pct REAL,
            hit_resistance BOOLEAN,
            hit_support BOOLEAN,
            max_price REAL,
            min_price REAL,
            volatility REAL,
            outcome TEXT,
            FOREIGN KEY (recommendation_id) REFERENCES recommendations(id)
        )
    """)
    
    conn.commit()
    conn.close()

def save_recommendation(self, rec: Dict) -> int:
    """Bir öneriyi veritabanına kaydet."""
    conn = sqlite3.connect(self.db_path)
    cursor = conn.cursor()
    
    # Güvenli değer çıkarma
    entry_price = rec.get("price") or rec.get("current_price")
    if entry_price is None:
        conn.close()
        return 0
    
    # Float'a çevir
    try:
        entry_price = float(entry_price)
    except (ValueError, TypeError):
        conn.close()
        return 0
    
    # Güvenli float çevirme fonksiyonu
    def safe_float(value):
        if value is None:
            return None
        try:
            return float(value)
        except (ValueError, TypeError):
            return None
    
    cursor.execute("""
        INSERT INTO recommendations (
            date, ticker, entry_price, technical_score, final_score,
            rating, sector, support_price, resistance_price,
            risk_pct, reward_pct, rr_ratio, signals
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        datetime.now().strftime("%Y-%m-%d"),
        rec.get("ticker", "UNKNOWN"),
        entry_price,
        safe_float(rec.get("technical_score")),
        safe_float(rec.get("final_score") or rec.get("score")),
        rec.get("rating", "N/A"),
        rec.get("sector", "N/A"),
        safe_float(rec.get("support")),
        safe_float(rec.get("resistance")),
        safe_float(rec.get("risk_pct")),
        safe_float(rec.get("reward_pct")),
        safe_float(rec.get("risk_reward_ratio")),
        json.dumps(rec.get("signals", []))
    ))
    
    rec_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return rec_id

def check_performance(self, days_to_check: List[int] = [7, 14, 30]):
    """Geçmiş önerilerin performansını kontrol et."""
    conn = sqlite3.connect(self.db_path)
    cursor = conn.cursor()
    
    results = []
    
    for days in days_to_check:
        target_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        
        cursor.execute("""
            SELECT id, ticker, entry_price, support_price, resistance_price
            FROM recommendations
            WHERE date = ?
        """, (target_date,))
        
        recommendations = cursor.fetchall()
        
        for rec_id, ticker, entry_price, support, resistance in recommendations:
            if entry_price is None:
                continue
            
            cursor.execute("""
                SELECT id FROM performance_results
                WHERE recommendation_id = ? AND days_held = ?
            """, (rec_id, days))
            
            if cursor.fetchone():
                continue
            
            perf = self._calculate_actual_performance(
                ticker, entry_price, target_date, days, support, resistance
            )
            
            if perf:
                cursor.execute("""
                    INSERT INTO performance_results (
                        recommendation_id, check_date, days_held,
                        exit_price, return_pct, hit_resistance, hit_support,
                        max_price, min_price, volatility, outcome
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    rec_id,
                    datetime.now().strftime("%Y-%m-%d"),
                    days,
                    perf["exit_price"],
                    perf["return_pct"],
                    perf["hit_resistance"],
                    perf["hit_support"],
                    perf["max_price"],
                    perf["min_price"],
                    perf["volatility"],
                    perf["outcome"]
                ))
                
                results.append({
                    "ticker": ticker,
                    "days": days,
                    "return": perf["return_pct"],
                    "outcome": perf["outcome"]
                })
    
    conn.commit()
    conn.close()
    
    return results

def _calculate_actual_performance(self, ticker: str, entry_price: float,
                                 start_date: str, days: int,
                                 support: float = None, resistance: float = None) -> Dict:
    """Gerçek piyasa performansını hesapla."""
    try:
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = start + timedelta(days=days + 5)
        
        df = yf.download(ticker, start=start, end=end, progress=False)
        
        if df.empty or len(df) < 2:
            return None
        
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        
        exit_price = float(df["Close"].iloc[-1])
        max_price = float(df["High"].max())
        min_price = float(df["Low"].min())
        
        return_pct = ((exit_price - entry_price) / entry_price) * 100
        volatility = float(df["Close"].pct_change().std() * 100)
        
        # Güvenli karşılaştırma
        hit_resistance = False
        hit_support = False
        
        if resistance is not None:
            try:
                hit_resistance = max_price >= float(resistance)
            except (ValueError, TypeError):
                pass
        
        if support is not None:
            try:
                hit_support = min_price <= float(support)
            except (ValueError, TypeError):
                pass
        
        if return_pct >= 5:
            outcome = "SUCCESS"
        elif return_pct >= 0:
            outcome = "NEUTRAL"
        else:
            outcome = "LOSS"
        
        return {
            "exit_price": round(exit_price, 2),
            "return_pct": round(return_pct, 2),
            "hit_resistance": hit_resistance,
            "hit_support": hit_support,
            "max_price": round(max_price, 2),
            "min_price": round(min_price, 2),
            "volatility": round(volatility, 2),
            "outcome": outcome
        }
    
    except Exception as e:
        return None

def generate_report(self, days: int = 30) -> Dict:
    """Son N günün performans raporunu üret."""
    conn = sqlite3.connect(self.db_path)
    cursor = conn.cursor()
    
    start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    
    cursor.execute("""
        SELECT COUNT(*) FROM recommendations WHERE date >= ?
    """, (start_date,))
    total_recs = cursor.fetchone()[0]
    
    cursor.execute("""
        SELECT 
            pr.outcome,
            COUNT(*) as count
        FROM performance_results pr
        JOIN recommendations r ON pr.recommendation_id = r.id
        WHERE r.date >= ? AND pr.days_held = 7
        GROUP BY pr.outcome
    """, (start_date,))
    
    outcomes = cursor.fetchall()
    
    success_count = 0
    neutral_count = 0
    loss_count = 0
    
    for outcome, count in outcomes:
        if outcome == "SUCCESS":
            success_count = count
        elif outcome == "NEUTRAL":
            neutral_count = count
        elif outcome == "LOSS":
            loss_count = count
    
    total_checked = success_count + neutral_count + loss_count
    win_rate = (success_count / total_checked * 100) if total_checked > 0 else 0
    
    cursor.execute("""
        SELECT AVG(pr.return_pct)
        FROM performance_results pr
        JOIN recommendations r ON pr.recommendation_id = r.id
        WHERE r.date >= ? AND pr.days_held = 7
    """, (start_date,))
    
    avg_return = cursor.fetchone()[0] or 0
    
    cursor.execute("""
        SELECT 
            r.sector,
            AVG(pr.return_pct) as avg_return
        FROM performance_results pr
        JOIN recommendations r ON pr.recommendation_id = r.id
        WHERE r.date >= ? AND pr.days_held = 7 AND r.sector IS NOT NULL
        GROUP BY r.sector
        ORDER BY avg_return DESC
        LIMIT 1
    """, (start_date,))
    
    best_sector_row = cursor.fetchone()
    best_sector = best_sector_row[0] if best_sector_row else "N/A"
    
    cursor.execute("""
        SELECT 
            r.sector,
            AVG(pr.return_pct) as avg_return
        FROM performance_results pr
        JOIN recommendations r ON pr.recommendation_id = r.id
        WHERE r.date >= ? AND pr.days_held = 7 AND r.sector IS NOT NULL
        GROUP BY r.sector
        ORDER BY avg_return ASC
        LIMIT 1
    """, (start_date,))
    
    worst_sector_row = cursor.fetchone()
    worst_sector = worst_sector_row[0] if worst_sector_row else "N/A"
    
    conn.close()
    
    return {
        "period_days": days,
        "total_recommendations": total_recs,
        "total_checked": total_checked,
        "success_count": success_count,
        "neutral_count": neutral_count,
        "loss_count": loss_count,
        "win_rate": round(win_rate, 2),
        "avg_return_pct": round(avg_return, 2),
        "best_sector": best_sector,
        "worst_sector": worst_sector
    }

def get_detailed_history(self, limit: int = 20) -> List[Dict]:
    """Detaylı geçmiş önerileri getir."""
    conn = sqlite3.connect(self.db_path)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT 
            r.date,
            r.ticker,
            r.entry_price,
            r.rating,
            r.final_score,
            pr.days_held,
            pr.exit_price,
            pr.return_pct,
            pr.outcome
        FROM recommendations r
        LEFT JOIN performance_results pr ON r.id = pr.recommendation_id
        ORDER BY r.date DESC
        LIMIT ?
    """, (limit,))
    
    rows = cursor.fetchall()
    conn.close()
    
    history = []
    for row in rows:
        history.append({
            "date": row[0],
            "ticker": row[1],
            "entry_price": row[2],
            "rating": row[3],
            "score": row[4],
            "days_held": row[5],
            "exit_price": row[6],
            "return_pct": row[7],
            "outcome": row[8]
        })
    
    return history
```

def generate_performance_email(report: Dict, history: List[Dict]) -> str:
“”“Performans raporu için HTML email üretir.”””

```
win_rate_color = "#10b981" if report["win_rate"] >= 60 else "#f59e0b" if report["win_rate"] >= 45 else "#ef4444"
avg_return_color = "#10b981" if report["avg_return_pct"] > 0 else "#ef4444"

html = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; background: #f0f4f8; padding: 20px; }}
        .container {{ max-width: 700px; margin: 0 auto; background: #fff; border-radius: 12px; }}
        .header {{ background: linear-gradient(135deg, #6366f1, #8b5cf6); padding: 30px; text-align: center; color: white; }}
        .stats {{ display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 15px; padding: 25px; }}
        .stat-box {{ background: #f8fafc; border: 2px solid #e2e8f0; border-radius: 10px; padding: 15px; text-align: center; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Performans Raporu</h1>
            <p>Son {report['period_days']} Gun</p>
        </div>
        
        <div class="stats">
            <div class="stat-box">
                <div>Toplam Oneri</div>
                <div style="font-size:28px; font-weight:800">{report['total_recommendations']}</div>
            </div>
            <div class="stat-box">
                <div>Basari Orani</div>
                <div style="font-size:28px; font-weight:800; color:{win_rate_color}">{report['win_rate']}%</div>
            </div>
            <div class="stat-box">
                <div>Ort. Getiri</div>
                <div style="font-size:28px; font-weight:800; color:{avg_return_color}">{report['avg_return_pct']:+.2f}%</div>
            </div>
        </div>
        
        <div style="padding: 25px;">
            <p><strong>En Iyi Sektor:</strong> {report['best_sector']}</p>
            <p><strong>En Kotu Sektor:</strong> {report['worst_sector']}</p>
        </div>
    </div>
</body>
</html>
"""

return html
```
