# ============================================================
# mail_sender.py — Email Gönderim Sistemi (v6 - KOMPLE FINAL)
# ============================================================

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from datetime import datetime


def get_urgency_color(urgency: str) -> str:
    """Urgency rengini al"""
    if "ÖNEMLİ" in urgency:
        return "#e74c3c"
    elif "Orta" in urgency:
        return "#f39c12"
    else:
        return "#27ae60"


def generate_detailed_market_mood(market_mood: str, sector_scores: dict) -> dict:
    """Market mood'u detaylı analiz et"""
    
    sorted_sectors = sorted(sector_scores.items(), key=lambda x: x[1], reverse=True)
    
    emoji_map = {
        "finans": "🏦", "teknoloji": "💻", "enerji": "⚡", "sağlık": "💊",
        "perakende": "🛒", "gıda": "🍔", "telekom": "📱", "otomotiv": "🚗",
        "inşaat_gayrimenkul": "🏗️", "sigortalar": "🛡️", "turizm": "✈️",
        "savunma": "🎖️", "tekstil": "👕", "kimya": "🧪", "orman": "🌲", "medya": "📺",
        "genel": "📊"
    }
    
    best_3 = sorted_sectors[:3]
    worst_3 = sorted_sectors[-3:]
    
    avg_score = sum(sector_scores.values()) / len(sector_scores) if sector_scores else 0
    
    if avg_score >= 0.4:
        title = "🟢 ÇOK OLUMLU - Piyasalar Güçlü Yukarı Baskı Altında"
        description = f"Küresel ve yerel piyasalar keskin yükseliş trendinde. Haber akışı olumlu, yatırımcı duygusu pozitif. Riski yönetmek şartıyla agresif pozisyon alınabilir."
        recommendation = "Alım sinyalleri güçlü. Portföy pozisyonunu artırabilirsiniz. Stop-loss belirleyerek riski kontrol edin."
        color = "#27ae60"
    elif avg_score >= 0.2:
        title = "🟢 OLUMLU - Pozitif Sinyaller Hakimiyetinde"
        description = f"Piyasalar yavaş yavaş yukarı yönlü. Çoğu sektörde pozitif momentum. Risk düşük seviyelerde."
        recommendation = "Seçici alımlar yapabilirsiniz. Yüksek volatilite sektörlerinden kaçının."
        color = "#2ecc71"
    elif avg_score >= -0.2:
        title = "🟡 KARIŞIK - Belirsiz Piyasa Durumu"
        description = f"Piyasa yönü net değil. Bazı sektörler yukarı, bazıları aşağı. Dengeli durum gözleniyor."
        recommendation = "Pozisyon almadan önce daha net sinyal bekleyebilirsiniz."
        color = "#f39c12"
    elif avg_score >= -0.4:
        title = "🔴 OLUMSUZ - Aşağı Yönlü Basınç Var"
        description = f"Piyasalar zayıflık gösteriyor. Çoğu sektöre satış baskısı. Yatırımcı duygusu negatif."
        recommendation = "Yeni pozisyonlardan uzak durun. Riski azaltmayı düşünün."
        color = "#e74c3c"
    else:
        title = "🔴 ÇOK OLUMSUZ - Yüksek Risk Dönem"
        description = f"Piyasalar panik modunda. Keskin satışlar yaşanıyor. Ekonomik endişeler yüksek."
        recommendation = "Defansif sektörlere kaçın. Nakit pozisyonu güçlü tutun."
        color = "#c0392b"
    
    return {
        "title": title,
        "description": description,
        "recommendation": recommendation,
        "color": color,
        "avg_score": round(avg_score, 3),
        "best_3": best_3,
        "worst_3": worst_3
    }


def generate_html_body(recommendations, chart_paths=None):
    """Detaylı, profesyonel HTML email oluştur (KOMPLE VERSION)"""
    date_str = datetime.now().strftime("%d %B %Y, %H:%M")
    recs = recommendations.get("recommendations", [])
    sector_scores = recommendations.get("sector_scores", {})
    global_analysis = recommendations.get("global_analysis", {})
    advanced_analysis = recommendations.get("advanced_analysis", {})
    advanced_features = recommendations.get("advanced_features", {})
    trend_opportunities = recommendations.get("trend_opportunities", [])
    sector_recommendations = recommendations.get("sector_recommendations", {})
    geo_news = recommendations.get("geo_news", [])
    supply_chain = recommendations.get("supply_chain", {})
    vix_data = advanced_analysis.get("vix", {})
    correlations = recommendations.get("correlations", {})
    specific_triggers = recommendations.get("specific_triggers", [])
    
    mood_analysis = generate_detailed_market_mood("", sector_scores)
    
    html = f"""
    <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                * {{ margin: 0; padding: 0; box-sizing: border-box; }}
                body {{ 
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
                    background: #f5f7fa;
                    color: #2c3e50;
                    line-height: 1.6;
                }}
                .wrapper {{ max-width: 1200px; margin: 0 auto; background: white; }}
                
                .header {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    padding: 40px 30px;
                    color: white;
                    text-align: center;
                    border-bottom: 5px solid {mood_analysis['color']};
                }}
                .header h1 {{
                    font-size: 32px;
                    margin-bottom: 8px;
                    font-weight: 700;
                    letter-spacing: -0.5px;
                }}
                .header .date {{
                    font-size: 14px;
                    opacity: 0.9;
                }}
                
                .mood-section {{
                    background: linear-gradient(135deg, {mood_analysis['color']} 0%, rgba(0,0,0,0.05) 100%);
                    color: white;
                    padding: 30px;
                    text-align: center;
                    border-bottom: 3px solid {mood_analysis['color']};
                }}
                
                .mood-title {{
                    font-size: 24px;
                    font-weight: 700;
                    margin-bottom: 15px;
                    letter-spacing: 0.5px;
                }}
                
                .mood-description {{
                    font-size: 15px;
                    line-height: 1.8;
                    margin-bottom: 15px;
                    opacity: 0.95;
                }}
                
                .mood-stats {{
                    display: grid;
                    grid-template-columns: repeat(3, 1fr);
                    gap: 15px;
                    margin: 20px 0;
                    background: rgba(255,255,255,0.1);
                    padding: 15px;
                    border-radius: 8px;
                }}
                
                .mood-stat {{
                    text-align: center;
                }}
                
                .mood-stat-label {{
                    font-size: 12px;
                    opacity: 0.8;
                    text-transform: uppercase;
                    letter-spacing: 0.5px;
                    font-weight: 600;
                }}
                
                .mood-stat-value {{
                    font-size: 20px;
                    font-weight: 700;
                    margin-top: 5px;
                }}
                
                .mood-sectors {{
                    display: grid;
                    grid-template-columns: 1fr 1fr;
                    gap: 15px;
                    margin-top: 20px;
                }}
                
                .best-worst-box {{
                    background: rgba(255,255,255,0.1);
                    border-radius: 6px;
                    padding: 12px;
                    font-size: 13px;
                }}
                
                .best-worst-title {{
                    font-weight: 700;
                    margin-bottom: 8px;
                    font-size: 12px;
                    text-transform: uppercase;
                    opacity: 0.9;
                }}
                
                .sector-item {{
                    padding: 6px 0;
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    border-bottom: 1px solid rgba(255,255,255,0.1);
                    font-size: 13px;
                }}
                
                .sector-item:last-child {{ border-bottom: none; }}
                
                .sector-name {{
                    display: flex;
                    align-items: center;
                    gap: 8px;
                }}
                
                .sector-score {{
                    font-weight: 700;
                    padding: 2px 8px;
                    background: rgba(255,255,255,0.2);
                    border-radius: 4px;
                    font-size: 12px;
                }}
                
                .mood-recommendation {{
                    background: rgba(255,255,255,0.15);
                    border-left: 4px solid white;
                    padding: 15px;
                    margin-top: 15px;
                    border-radius: 4px;
                    font-size: 14px;
                    font-weight: 500;
                    line-height: 1.7;
                }}
                
                .mood-recommendation strong {{
                    display: block;
                    margin-bottom: 8px;
                    font-size: 13px;
                    text-transform: uppercase;
                    letter-spacing: 0.5px;
                    opacity: 0.9;
                }}
                
                .content {{
                    padding: 40px 30px;
                }}
                
                .section-title {{
                    font-size: 24px;
                    font-weight: 700;
                    color: #2c3e50;
                    margin: 30px 0 25px 0;
                    padding-bottom: 12px;
                    border-bottom: 3px solid #667eea;
                    display: flex;
                    align-items: center;
                }}
                .section-title::before {{
                    content: '●';
                    margin-right: 12px;
                    font-size: 24px;
                    color: #667eea;
                }}
                
                .global-section {{
                    display: grid;
                    grid-template-columns: 1fr 1fr;
                    gap: 20px;
                    margin: 30px 0;
                }}
                
                .global-box {{
                    background: #f8f9fa;
                    border-radius: 8px;
                    padding: 20px;
                    border-left: 5px solid #667eea;
                }}
                
                .global-box.us-debt {{ border-left-color: #e74c3c; }}
                .global-box.commodities {{ border-left-color: #f39c12; }}
                .global-box.geopolitical {{ border-left-color: #e67e22; }}
                .global-box.holidays {{ border-left-color: #3498db; }}
                
                .global-box h3 {{
                    font-size: 16px;
                    font-weight: 700;
                    color: #2c3e50;
                    margin-bottom: 12px;
                }}
                
                .global-stat {{
                    display: flex;
                    justify-content: space-between;
                    padding: 8px 0;
                    border-bottom: 1px solid #ecf0f1;
                    font-size: 13px;
                }}
                
                .global-stat:last-child {{ border-bottom: none; }}
                
                .global-label {{ color: #7f8c8d; font-weight: 500; }}
                .global-value {{ color: #2c3e50; font-weight: 700; }}
                
                .commodity-grid {{
                    display: grid;
                    grid-template-columns: repeat(2, 1fr);
                    gap: 10px;
                    margin: 15px 0;
                }}
                
                .commodity-item {{
                    background: white;
                    padding: 10px;
                    border-radius: 6px;
                    border: 1px solid #ecf0f1;
                    text-align: center;
                    font-size: 12px;
                }}
                
                .commodity-name {{
                    font-weight: 600;
                    color: #2c3e50;
                    margin-bottom: 5px;
                }}
                
                .commodity-price {{
                    font-size: 16px;
                    font-weight: 700;
                    color: #667eea;
                }}
                
                .commodity-change {{
                    font-size: 11px;
                    margin-top: 3px;
                }}
                
                .commodity-change.up {{ color: #27ae60; }}
                .commodity-change.down {{ color: #e74c3c; }}
                
                .event-item {{
                    background: white;
                    padding: 12px;
                    margin: 8px 0;
                    border-left: 4px solid #e67e22;
                    border-radius: 4px;
                    font-size: 12px;
                }}
                
                .event-title {{
                    font-weight: 600;
                    color: #2c3e50;
                    margin-bottom: 4px;
                }}
                
                .event-impact {{
                    color: #7f8c8d;
                    font-size: 11px;
                }}
                
                .trend-box {{
                    background: #f0f7ff;
                    border-left: 4px solid #3498db;
                    padding: 15px;
                    margin: 15px 0;
                    border-radius: 4px;
                }}
                
                .trend-box h4 {{
                    color: #3498db;
                    font-size: 14px;
                    font-weight: 600;
                    margin-bottom: 10px;
                }}
                
                .trend-item {{
                    background: white;
                    padding: 10px;
                    margin: 8px 0;
                    border-radius: 4px;
                    font-size: 12px;
                    border-left: 3px solid #3498db;
                }}
                
                .trend-ticker {{
                    font-weight: 700;
                    color: #2c3e50;
                }}
                
                .trend-stat {{
                    font-size: 11px;
                    color: #7f8c8d;
                }}
                
                .stock-card {{
                    background: #f8f9fa;
                    border-left: 5px solid #667eea;
                    border-radius: 8px;
                    padding: 25px;
                    margin-bottom: 25px;
                    box-shadow: 0 2px 8px rgba(0,0,0,0.05);
                }}
                .stock-card.rank1 {{ border-left-color: #f39c12; background: #fffbf5; }}
                .stock-card.rank2 {{ border-left-color: #27ae60; background: #f5fef8; }}
                .stock-card.rank3 {{ border-left-color: #3498db; background: #f5fbff; }}
                
                .stock-header {{
                    display: flex;
                    justify-content: space-between;
                    align-items: flex-start;
                    margin-bottom: 20px;
                    padding-bottom: 15px;
                    border-bottom: 2px solid rgba(0,0,0,0.08);
                }}
                .stock-header-left h2 {{
                    font-size: 28px;
                    font-weight: 700;
                    color: #2c3e50;
                    margin-bottom: 5px;
                }}
                .stock-header-left .sector {{
                    font-size: 12px;
                    color: #7f8c8d;
                    text-transform: uppercase;
                    letter-spacing: 1px;
                    font-weight: 600;
                }}
                .rating-badge {{
                    display: inline-block;
                    padding: 10px 20px;
                    background: #27ae60;
                    color: white;
                    border-radius: 25px;
                    font-weight: 700;
                    font-size: 14px;
                    box-shadow: 0 4px 12px rgba(39, 174, 96, 0.3);
                    text-align: center;
                }}
                
                .metrics-grid {{
                    display: grid;
                    grid-template-columns: repeat(3, 1fr);
                    gap: 15px;
                    margin: 20px 0;
                }}
                .metric-box {{
                    background: white;
                    border: 2px solid #ecf0f1;
                    border-radius: 6px;
                    padding: 15px;
                    text-align: center;
                }}
                .metric-label {{
                    font-size: 11px;
                    color: #95a5a6;
                    text-transform: uppercase;
                    letter-spacing: 0.5px;
                    font-weight: 600;
                    margin-bottom: 8px;
                }}
                .metric-value {{
                    font-size: 24px;
                    font-weight: 700;
                    color: #667eea;
                }}
                .metric-sub {{
                    font-size: 12px;
                    color: #7f8c8d;
                    margin-top: 5px;
                }}
                
                .indicators-section {{
                    background: white;
                    border: 1px solid #ecf0f1;
                    border-radius: 6px;
                    padding: 15px;
                    margin: 15px 0;
                    font-size: 13px;
                }}
                .indicators-section h4 {{
                    color: #2c3e50;
                    font-size: 14px;
                    font-weight: 600;
                    margin-bottom: 12px;
                    border-bottom: 2px solid #ecf0f1;
                    padding-bottom: 8px;
                }}
                .indicator-row {{
                    display: flex;
                    justify-content: space-between;
                    padding: 8px 0;
                    border-bottom: 1px solid #ecf0f1;
                }}
                .indicator-row:last-child {{ border-bottom: none; }}
                .indicator-label {{
                    color: #7f8c8d;
                    font-weight: 500;
                }}
                .indicator-value {{
                    color: #2c3e50;
                    font-weight: 700;
                }}
                .indicator-value.positive {{ color: #27ae60; }}
                .indicator-value.negative {{ color: #e74c3c; }}
                
                .risk-potential-grid {{
                    display: grid;
                    grid-template-columns: 1fr 1fr;
                    gap: 15px;
                    margin: 15px 0;
                }}
                .risk-box {{
                    background: rgba(231, 76, 60, 0.08);
                    border-left: 4px solid #e74c3c;
                    padding: 15px;
                    border-radius: 4px;
                }}
                .risk-box h4 {{
                    color: #e74c3c;
                    font-size: 12px;
                    font-weight: 700;
                    text-transform: uppercase;
                    margin-bottom: 8px;
                    letter-spacing: 0.5px;
                }}
                .risk-box .value {{
                    font-size: 20px;
                    color: #e74c3c;
                    font-weight: 700;
                }}
                .risk-box .detail {{
                    font-size: 11px;
                    color: #7f8c8d;
                    margin-top: 5px;
                }}
                
                .potential-box {{
                    background: rgba(39, 174, 96, 0.08);
                    border-left: 4px solid #27ae60;
                    padding: 15px;
                    border-radius: 4px;
                }}
                .potential-box h4 {{
                    color: #27ae60;
                    font-size: 12px;
                    font-weight: 700;
                    text-transform: uppercase;
                    margin-bottom: 8px;
                    letter-spacing: 0.5px;
                }}
                .potential-box .value {{
                    font-size: 20px;
                    color: #27ae60;
                    font-weight: 700;
                }}
                .potential-box .detail {{
                    font-size: 11px;
                    color: #7f8c8d;
                    margin-top: 5px;
                }}
                
                .fibonacci-section {{
                    background: white;
                    border: 1px solid #ecf0f1;
                    border-radius: 6px;
                    padding: 15px;
                    margin: 15px 0;
                    font-size: 12px;
                }}
                .fibonacci-section h4 {{
                    color: #2c3e50;
                    font-size: 13px;
                    font-weight: 600;
                    margin-bottom: 10px;
                    border-bottom: 2px solid #ecf0f1;
                    padding-bottom: 8px;
                }}
                .fib-row {{
                    display: flex;
                    justify-content: space-between;
                    padding: 8px 0;
                    border-bottom: 1px solid #f5f5f5;
                }}
                .fib-row:last-child {{ border-bottom: none; }}
                .fib-label {{ color: #7f8c8d; font-weight: 500; }}
                .fib-value {{ color: #667eea; font-weight: 700; }}
                
                .signals-box {{
                    background: #f0f7ff;
                    border-left: 4px solid #3498db;
                    padding: 15px;
                    margin: 15px 0;
                    border-radius: 4px;
                    font-size: 13px;
                }}
                .signals-box h4 {{
                    color: #3498db;
                    font-size: 13px;
                    font-weight: 600;
                    margin-bottom: 10px;
                }}
                .signal-item {{
                    padding: 6px 0;
                    color: #2c3e50;
                    border-bottom: 1px solid rgba(52, 152, 219, 0.1);
                }}
                .signal-item:last-child {{ border-bottom: none; }}
                .signal-item::before {{
                    content: '▸ ';
                    color: #3498db;
                    font-weight: 700;
                }}
                
                .charts-section {{
                    margin-top: 40px;
                    text-align: center;
                }}
                .charts-section h2 {{
                    font-size: 24px;
                    font-weight: 700;
                    color: #2c3e50;
                    margin-bottom: 25px;
                    padding-bottom: 12px;
                    border-bottom: 3px solid #667eea;
                    display: inline-block;
                }}
                .chart-img {{
                    max-width: 100%;
                    height: auto;
                    border-radius: 8px;
                    margin: 20px 0;
                    border: 1px solid #ecf0f1;
                    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
                }}
                
                .disclaimer {{
                    background: #fffbf5;
                    border-left: 4px solid #f39c12;
                    padding: 20px;
                    margin: 30px 0;
                    border-radius: 4px;
                    font-size: 12px;
                    color: #d68910;
                    line-height: 1.8;
                }}
                .disclaimer strong {{ color: #bf6e1a; }}
                
                .no-recommendation {{
                    background: #fef5f5;
                    border-left: 4px solid #e74c3c;
                    padding: 20px;
                    border-radius: 4px;
                    text-align: center;
                    color: #e74c3c;
                    font-weight: 600;
                    font-size: 16px;
                }}
                
                .footer {{
                    background: #2c3e50;
                    color: white;
                    padding: 30px;
                    text-align: center;
                    font-size: 12px;
                    border-top: 1px solid #ecf0f1;
                }}
                .footer p {{
                    margin: 8px 0;
                    opacity: 0.9;
                }}
                .footer .footer-brand {{
                    font-size: 14px;
                    font-weight: 600;
                    margin-bottom: 10px;
                }}
                
                .rank-label {{
                    display: inline-block;
                    width: 35px;
                    height: 35px;
                    background: #667eea;
                    color: white;
                    border-radius: 50%;
                    font-size: 16px;
                    font-weight: 700;
                    line-height: 35px;
                    text-align: center;
                    margin-right: 12px;
                    float: left;
                }}
                .stock-card.rank1 .rank-label {{ background: #f39c12; }}
                .stock-card.rank2 .rank-label {{ background: #27ae60; }}
                .stock-card.rank3 .rank-label {{ background: #3498db; }}

                .trigger-box {{
                    background: #fff8dc;
                    border-left: 4px solid #ff8c00;
                    padding: 15px;
                    border-radius: 6px;
                    margin: 15px 0;
                    font-size: 12px;
                }}

                .trigger-header {{
                    font-weight: 700;
                    color: #2c3e50;
                    margin-bottom: 10px;
                    font-size: 13px;
                }}

                .trigger-grid {{
                    display: grid;
                    grid-template-columns: 1fr 1fr;
                    gap: 10px;
                }}

                .trigger-positive {{
                    background: #e8f5e9;
                    padding: 10px;
                    border-radius: 4px;
                    font-size: 11px;
                    border-left: 3px solid #27ae60;
                }}

                .trigger-negative {{
                    background: #ffebee;
                    padding: 10px;
                    border-radius: 4px;
                    font-size: 11px;
                    border-left: 3px solid #e74c3c;
                }}

                .crypto-box {{
                    background: #f3e5f5;
                    border-left: 4px solid #9c27b0;
                    padding: 15px;
                    border-radius: 6px;
                    margin: 20px 0;
                }}

                .crypto-grid {{
                    display: grid;
                    grid-template-columns: 1fr 1fr;
                    gap: 15px;
                    margin-bottom: 15px;
                }}

                .crypto-item {{
                    text-align: center;
                    background: white;
                    padding: 12px;
                    border-radius: 4px;
                    font-size: 12px;
                }}

                .crypto-name {{
                    font-weight: 600;
                    color: #5e35b1;
                    margin-bottom: 5px;
                }}

                .crypto-price {{
                    font-size: 20px;
                    font-weight: 700;
                    color: #2c3e50;
                }}

                .currency-box {{
                    background: #ecf0f1;
                    border-left: 4px solid #34495e;
                    padding: 12px;
                    border-radius: 4px;
                    margin: 8px 0;
                    font-size: 11px;
                    text-align: center;
                }}

                .buyback-box {{
                    background: #e3f2fd;
                    border-left: 4px solid #2196f3;
                    padding: 15px;
                    border-radius: 6px;
                    margin: 20px 0;
                    font-size: 12px;
                }}

                .earnings-box {{
                    background: #fff9c4;
                    border-left: 4px solid #fbc02d;
                    padding: 15px;
                    border-radius: 6px;
                    margin: 20px 0;
                    font-size: 12px;
                }}

                .breadth-box {{
                    background: #f0f7ff;
                    border-left: 4px solid #3498db;
                    padding: 15px;
                    border-radius: 6px;
                    margin: 20px 0;
                }}

                .breadth-grid {{
                    display: grid;
                    grid-template-columns: repeat(3, 1fr);
                    gap: 10px;
                    margin-bottom: 12px;
                }}

                .breadth-item {{
                    text-align: center;
                    background: white;
                    padding: 10px;
                    border-radius: 4px;
                    font-size: 11px;
                }}
            </style>
        </head>
        <body>
            <div class="wrapper">
                <div class="header">
                    <h1>📊 Borsa Analiz Raporu</h1>
                    <div class="date">{date_str} | Günlük Analiz</div>
                </div>
                
                <!-- MARKET MOOD -->
                <div class="mood-section">
                    <div class="mood-title">{mood_analysis['title']}</div>
                    <div class="mood-description">{mood_analysis['description']}</div>
                    
                    <div class="mood-stats">
                        <div class="mood-stat">
                            <div class="mood-stat-label">Pazar Skoru</div>
                            <div class="mood-stat-value">{mood_analysis['avg_score']:.2f}</div>
                        </div>
                        <div class="mood-stat">
                            <div class="mood-stat-label">Analiz Edilen</div>
                            <div class="mood-stat-value">{len(sector_scores)}</div>
                        </div>
                        <div class="mood-stat">
                            <div class="mood-stat-label">Tarih</div>
                            <div class="mood-stat-value">{datetime.now().strftime('%d.%m.%Y')}</div>
                        </div>
                    </div>
                    
                    <div class="mood-sectors">
                        <div class="best-worst-box">
                            <div class="best-worst-title">🏆 En Güçlü Sektörler</div>
    """
    
    emoji_map = {
        "finans": "🏦", "teknoloji": "💻", "enerji": "⚡", "sağlık": "💊",
        "perakende": "🛒", "gıda": "🍔", "telekom": "📱", "otomotiv": "🚗",
        "inşaat_gayrimenkul": "🏗️", "sigortalar": "🛡️", "turizm": "✈️",
        "savunma": "🎖️", "tekstil": "👕", "kimya": "🧪", "orman": "🌲", "medya": "📺"
    }
    
    for sector, score in mood_analysis['best_3']:
        html += f"""
                            <div class="sector-item">
                                <span class="sector-name">
                                    {emoji_map.get(sector, '📊')} {sector.replace('_', ' ').title()}
                                </span>
                                <span class="sector-score">{score:+.3f}</span>
                            </div>
        """
    
    html += """
                        </div>
                        
                        <div class="best-worst-box">
                            <div class="best-worst-title">⚠️ En Zayıf Sektörler</div>
    """
    
    for sector, score in mood_analysis['worst_3']:
        html += f"""
                            <div class="sector-item">
                                <span class="sector-name">
                                    {emoji_map.get(sector, '📊')} {sector.replace('_', ' ').title()}
                                </span>
                                <span class="sector-score">{score:+.3f}</span>
                            </div>
        """
    
    html += f"""
                        </div>
                    </div>
                    
                    <div class="mood-recommendation">
                        <strong>💡 Tavsia:</strong>
                        {mood_analysis['recommendation']}
                    </div>
                </div>
                
                <div class="content">
    """
    
    # ========== KÜRESEL ANALİZ ==========
    html += """
                    <div class="section-title">🌍 Küresel Piyasa Analizi</div>
                    <div class="global-section">
    """
    
    # ABD Borcu
    if global_analysis.get("us_debt"):
        us_debt = global_analysis["us_debt"]
        html += f"""
                        <div class="global-box us-debt">
                            <h3>📊 ABD Dış Borcu</h3>
                            <div class="global-stat">
                                <span class="global-label">Durum</span>
                                <span class="global-value">{us_debt.get('level', 'N/A')}</span>
                            </div>
                            <div class="global-stat">
                                <span class="global-label">Güncel Borç</span>
                                <span class="global-value">${us_debt.get('current_debt_billion', 'N/A')} Trilyon</span>
                            </div>
                            <div class="global-stat">
                                <span class="global-label">Risk Seviyesi</span>
                                <span class="global-value">{us_debt.get('risk', 'N/A')}</span>
                            </div>
                            <div class="global-stat">
                                <span class="global-label">Trend</span>
                                <span class="global-value">{us_debt.get('trend', 'N/A')}</span>
                            </div>
                        </div>
        """
    
    # Emtialar
    if global_analysis.get("commodities"):
        commodities = global_analysis["commodities"]
        html += """
                        <div class="global-box commodities">
                            <h3>🏭 Emtia Fiyatları</h3>
                            <div class="commodity-grid">
        """
        
        commodity_names = {
            "gold": "Altın",
            "silver": "Gümüş",
            "copper": "Bakır",
            "oil": "Petrol",
            "natural_gas": "Doğalgaz"
        }
        
        for key, commodity in commodities.items():
            trend = "📈" if commodity['change'] >= 0 else "📉"
            html += f"""
                                <div class="commodity-item">
                                    <div class="commodity-name">{commodity_names.get(key, key.title())}</div>
                                    <div class="commodity-price">${commodity['current']}</div>
                                    <div class="commodity-change {'up' if commodity['change'] >= 0 else 'down'}">{trend} {commodity['change']:+.2f}%</div>
                                </div>
            """
        
        html += """
                            </div>
                        </div>
        """
    
    html += """
                    </div>
    """
    
    # ========== EMTİA REKORLARI ==========
    if global_analysis.get("commodity_records"):
        records = global_analysis["commodity_records"]
        html += """
                    <div class="section-title">📈 Emtia Rekor Analizi</div>
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin: 20px 0;">
        """
        
        for key, record in records.items():
            record_status = "🔥 REKOR YAKINI!" if record['is_record'] else f"↑ {record['distance_to_high']:.1f}% uzakta"
            
            html += f"""
                        <div class="global-box">
                            <h3>{record['name'].title()}</h3>
                            <div class="global-stat">
                                <span class="global-label">��u Anki</span>
                                <span class="global-value">${record['current']}</span>
                            </div>
                            <div class="global-stat">
                                <span class="global-label">All-Time High</span>
                                <span class="global-value">${record['all_time_high']}</span>
                            </div>
                            <div class="global-stat">
                                <span class="global-label">Durum</span>
                                <span class="global-value">{record_status}</span>
                            </div>
            """
            
            # Geçmiş olaylar
            if record.get('events'):
                html += """
                            <div style="margin-top: 10px; padding-top: 10px; border-top: 1px solid #ecf0f1;">
                                <div style="font-size: 11px; font-weight: 600; color: #2c3e50; margin-bottom: 8px;">📌 Geçmiş Olaylar:</div>
                """
                
                for event in record['events'][:2]:
                    html += f"""
                                <div style="font-size: 11px; color: #7f8c8d; padding: 4px 0;">
                                    • {event['date']}: {event['event']} ({event['impact']})
                                </div>
                    """
                
                html += """
                            </div>
                """
            
            html += """
                        </div>
            """
        
        html += """
                    </div>
        """
    
    # ========== JEOPOLİTİK OLAYLAR ==========
    if global_analysis.get("geopolitical"):
        geopolitical = global_analysis["geopolitical"]
        
        if geopolitical.get("events"):
            html += """
                    <div class="section-title">🗺️ Jeopolitik Olaylar ve Piyasa Etkileri</div>
                    <div style="background: #fff3cd; border-left: 4px solid #ff9800; padding: 15px; border-radius: 4px; margin: 20px 0;">
                        <strong>⚠️ Dikkat:</strong> Aşağıdaki olaylar küresel piyasalarda volatilite yaratabilir.
                    </div>
            """
            
            for event in geopolitical["events"]:
                html += f"""
                    <div class="event-item">
                        <div class="event-title">📍 {event['event']}</div>
                        <div style="font-size: 11px; color: #95a5a6; margin: 4px 0;">
                            Tarih: {event['date']} | Durum: {event['status']} | Süresi: {event['duration']}
                        </div>
                        <div class="event-impact">
                            Piyasa Etkileri: {', '.join(event['impact'])}
                        </div>
                    </div>
                """
            
            html += """
                    <div style="background: #e8f5e9; border-left: 4px solid #4caf50; padding: 15px; border-radius: 4px; margin: 20px 0;">
                        <strong>Genel Piyasa Ortamı:</strong> Yüksek Volatilite
                    </div>
            """
    
    # ========== BORSA TATİLLERİ ==========
    if global_analysis.get("exchange_holidays"):
        holidays = global_analysis["exchange_holidays"]
        
        if holidays.get("upcoming_holidays"):
            html += """
                    <div class="section-title">📅 Yakın Borsa Tatilleri</div>
                    <div style="background: #e3f2fd; border-left: 4px solid #2196f3; padding: 15px; border-radius: 4px; margin: 20px 0;">
                        <strong>ℹ️ Bilgi:</strong> Tatil günlerinde volatilite artabilir.
                    </div>
            """
            
            for holiday in holidays["upcoming_holidays"]:
                html += f"""
                    <div style="background: white; border: 1px solid #ecf0f1; padding: 12px; margin: 10px 0; border-radius: 4px;">
                        <div style="display: flex; justify-content: space-between; font-size: 13px; font-weight: 600; color: #2c3e50; margin-bottom: 5px;">
                            <span>{holiday['exchange']} - {holiday['region']}</span>
                            <span style="color: #e74c3c;">{holiday['days_until']} gün sonra</span>
                        </div>
                        <div style="font-size: 12px; color: #7f8c8d;">
                            {holiday['date']}: {holiday['event']}
                        </div>
                    </div>
                """
    
    # ========== MAKRO EKONOMIK TAKVIM ==========
    if advanced_analysis.get("macro_events"):
        macro = advanced_analysis["macro_events"]
        
        if macro.get("upcoming_events"):
            html += """
                    <div class="section-title">📅 Makro Ekonomik Takvim</div>
                    <div style="background: #fff3cd; border-left: 4px solid #ff9800; padding: 15px; border-radius: 4px; margin: 20px 0;">
                        <strong>⚠️ Makro Olaylar Başında</strong>
                    </div>
            """
            
            for event in macro.get("upcoming_events", [])[:3]:
                html += f"""
                    <div style="background: white; border: 1px solid #ecf0f1; padding: 15px; margin: 15px 0; border-radius: 6px;">
                        <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 10px;">
                            <div style="flex: 1;">
                                <div style="font-size: 14px; font-weight: 700; color: #2c3e50;">{event['event']}</div>
                                <div style="font-size: 12px; color: #7f8c8d; margin-top: 4px;">
                                    {event['date']} {event.get('time', '')} | Impact: {event.get('impact', 'N/A')}
                                </div>
                            </div>
                            <div style="background: {get_urgency_color(event.get('urgency', ''))}; color: white; padding: 6px 12px; border-radius: 4px; font-size: 11px; font-weight: 600;">
                                {event.get('urgency', 'Normal')}
                            </div>
                        </div>
                        <div style="background: #f8f9fa; padding: 10px; border-radius: 4px; font-size: 12px; color: #2c3e50; line-height: 1.6;">
                            <strong>Beklenen:</strong> {event.get('expected', 'N/A')}<br>
                            <strong>Etkilenen Sektörler:</strong> {', '.join(event.get('sector_impact', []))}<br>
                            <strong>Varlık Etkileri:</strong> {', '.join([f"{k.upper()}: {v}" for k, v in event.get('asset_impact', {}).items()])}
                        </div>
                    </div>
                """
    
    # ========== VIX ANALİZİ ==========
    if vix_data:
        vix_color = "#27ae60" if vix_data.get("current", 20) < 15 else "#f39c12" if vix_data.get("current", 20) < 20 else "#e74c3c"
        
        html += f"""
                    <div class="section-title">📊 Volatilite İndeksi (VIX)</div>
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin: 20px 0;">
                        <div style="background: {vix_color}15; border-left: 4px solid {vix_color}; padding: 20px; border-radius: 6px;">
                            <div style="font-size: 12px; color: #7f8c8d; text-transform: uppercase; margin-bottom: 10px; font-weight: 600;">Güncel VIX</div>
                            <div style="font-size: 32px; font-weight: 700; color: {vix_color}; margin-bottom: 10px;">{vix_data.get('current', 'N/A')}</div>
                            <div style="font-size: 13px; color: #2c3e50; font-weight: 500;">{vix_data.get('level', 'N/A')}</div>
                        </div>
                        
                        <div style="background: #e3f2fd; border-left: 4px solid #2196f3; padding: 20px; border-radius: 6px;">
                            <div style="font-size: 12px; color: #1565c0; text-transform: uppercase; margin-bottom: 10px; font-weight: 600;">Pazar Tavsiyesi</div>
                            <div style="font-size: 13px; color: #2c3e50; line-height: 1.7;">
                                <strong>{vix_data.get('status', 'N/A')}</strong><br>
                                <div style="margin-top: 8px; font-size: 12px; color: #7f8c8d;">
                                    {vix_data.get('recommendation', 'N/A')}
                                </div>
                            </div>
                        </div>
                    </div>
        """
    
    # ========== SEKTÖR TAVSİYESİ ==========
    if sector_recommendations:
        sector_rec = sector_recommendations
        
        html += """
                    <div class="section-title">📈 Makro-Temelli Sektör Tavsiyesi</div>
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin: 20px 0;">
                        <div style="background: #e8f5e9; border-left: 4px solid #4caf50; padding: 20px; border-radius: 6px;">
                            <div style="font-size: 12px; color: #2e7d32; text-transform: uppercase; margin-bottom: 10px; font-weight: 600;">🟢 EN İYİ 3 SEKTÖR</div>
        """
        
        for sector in sector_rec.get('top_3_buy', []):
            html += f'<div style="padding: 6px 0; font-size: 13px; color: #2c3e50; border-bottom: 1px solid rgba(0,0,0,0.1);">💹 {sector}</div>'
        
        html += """
                        </div>
                        
                        <div style="background: #ffebee; border-left: 4px solid #f44336; padding: 20px; border-radius: 6px;">
                            <div style="font-size: 12px; color: #c62828; text-transform: uppercase; margin-bottom: 10px; font-weight: 600;">🔴 KAÇINILACAK SEKTÖRLER</div>
        """
        
        for sector in sector_rec.get('top_3_avoid', []):
            html += f'<div style="padding: 6px 0; font-size: 13px; color: #2c3e50; border-bottom: 1px solid rgba(0,0,0,0.1);">⚠️ {sector}</div>'
        
        html += """
                        </div>
                    </div>
        """
    
    # ========== YÜKSELIŞ TRENDLERI ==========
    if trend_opportunities:
        html += """
                    <div class="section-title">📈 Trend Analizi - Destek → Direnç Geçişleri</div>
                    <div class="trend-box">
                        <h4>🚀 Yükseliş Trendine Giren Hisseler (Support Breakout)</h4>
        """
        
        for opp in trend_opportunities[:5]:
            html += f"""
                        <div class="trend-item">
                            <div class="trend-ticker">{opp['ticker']}</div>
                            <div class="trend-stat">
                                Destek: {opp['support']} | Direnç: {opp['resistance']} | 
                                Kıyaslanma Gücü: {opp['breakout_strength']:.1f}% | 
                                Potansiyel: {opp['potential_upside']:.1f}%
                            </div>
                        </div>
            """
        
        html += """
                    </div>
        """
    
    # ========== SPESIFIK TETIKLEYICILER ==========
    if specific_triggers:
        html += """
                    <div class="section-title">🎯 Spesifik Sektör Tetikleyicileri</div>
        """
        
        for trigger in specific_triggers[:3]:
            html += f"""
                    <div class="trigger-box">
                        <div class="trigger-header">⚡ {trigger['name']}</div>
                        <div style="font-size: 11px; color: #7f8c8d; margin-bottom: 10px;">
                            Etki: {trigger['impact']} | Süre: {trigger['duration']}<br>
                            <strong>Geçmiş:</strong> {trigger.get('historical_reference', 'N/A')}
                        </div>
                        <div class="trigger-grid">
                            <div class="trigger-positive">
                                <strong style="color: #27ae60;">🟢 LONG (AL)</strong><br>
            """
            
            for stock in trigger.get("affected_stocks", {}).get("positive", [])[:2]:
                html += f"""
                                <div style="margin: 5px 0;">{stock['ticker']}: +{stock['impact']}</div>
                """
            
            html += """
                            </div>
                            <div class="trigger-negative">
                                <strong style="color: #e74c3c;">🔴 SHORT (SAT)</strong><br>
            """
            
            for stock in trigger.get("affected_stocks", {}).get("negative", [])[:2]:
                html += f"""
                                <div style="margin: 5px 0;">{stock['ticker']}: {stock['impact']}</div>
                """
            
            html += """
                            </div>
                        </div>
                    </div>
            """
    
    # ========== KRİPTO ETKİSİ ==========
    if advanced_features.get("crypto_impact"):
        crypto = advanced_features["crypto_impact"]
        
        html += """
                    <div class="section-title">🪙 Kripto Piyasası Etkisi</div>
                    <div class="crypto-box">
                        <div class="crypto-grid">
        """
        
        if crypto.get('crypto_data'):
            crypto_data = crypto['crypto_data']
            html += f"""
                            <div class="crypto-item">
                                <div class="crypto-name">₿ Bitcoin</div>
                                <div class="crypto-price">${crypto_data['bitcoin']['price']:,.0f}</div>
                                <div style="font-size: 13px; color: {'#27ae60' if crypto_data['bitcoin']['change'] > 0 else '#e74c3c'};">
                                    {crypto_data['bitcoin']['trend']} {crypto_data['bitcoin']['change']:+.2f}%
                                </div>
                            </div>
                            <div class="crypto-item">
                                <div class="crypto-name">Ξ Ethereum</div>
                                <div class="crypto-price">${crypto_data['ethereum']['price']:,.0f}</div>
                                <div style="font-size: 13px; color: {'#27ae60' if crypto_data['ethereum']['change'] > 0 else '#e74c3c'};">
                                    {crypto_data['ethereum']['trend']} {crypto_data['ethereum']['change']:+.2f}%
                                </div>
                            </div>
            """
        
        html += f"""
                        </div>
                        <div style="background: white; padding: 10px; border-radius: 4px; font-size: 12px; color: #2c3e50;">
                            <strong>Piyasa Durumu:</strong> {crypto.get('status', 'N/A')}<br>
                            <strong>Etki:</strong> {crypto.get('impact', 'N/A')}<br>
                            <strong>Etkilenen Sektörler:</strong> {', '.join(crypto.get('affected_sectors', [])) if crypto.get('affected_sectors') else 'Nötr'}
                        </div>
                    </div>
        """
    
    # ========== DÖVIZ KURLAR ==========
    if advanced_features.get("currency_impact"):
        currency = advanced_features["currency_impact"]
        
        if currency.get("rates"):
            html += """
                    <div class="section-title">💱 Döviz Kurları</div>
                    <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; margin: 20px 0;">
            """
            
            for pair, data in list(currency["rates"].items())[:4]:
                html += f"""
                        <div class="currency-box">
                            <strong>{pair}</strong><br>
                            <div style="font-size: 16px; font-weight: 700; color: #667eea; margin: 5px 0;">{data['rate']}</div>
                            <div style="color: {'#27ae60' if data['change'] > 0 else '#e74c3c'};">
                                {data['trend']} {data['change']:+.2f}%
                            </div>
                        </div>
                """
            
            html += """
                    </div>
            """
    
    # ========== BUYBACK PROGRAMLARI ==========
    if advanced_features.get("buyback"):
        buyback = advanced_features["buyback"]
        
        if buyback.get("programs"):
            html += f"""
                    <div class="section-title">📊 Kurumsal Geri Satın Alma (Buyback)</div>
                    <div class="buyback-box">
                        <div style="font-size: 13px; color: #1565c0; margin-bottom: 12px;">
                            <strong>{buyback.get('status', 'N/A')}</strong><br>
                            Toplam: {buyback.get('total_amount', 'N/A')}
                        </div>
            """
            
            for program in buyback.get("programs", [])[:3]:
                html += f"""
                        <div style="background: white; padding: 10px; border-radius: 4px; margin-bottom: 8px; font-size: 11px; border-left: 3px solid #2196f3;">
                            <strong>{program['company']} ({program['ticker']})</strong><br>
                            Tutar: {program['amount']} | Durum: {program['status']}<br>
                            <span style="color: #7f8c8d;">Etki: {program['impact']}</span>
                        </div>
                """
            
            html += """
                    </div>
            """
    
    # ========== KAZANÇ TAKVİMİ ==========
    if advanced_features.get("earnings"):
        earnings = advanced_features["earnings"]
        
        if earnings.get("upcoming_earnings"):
            html += f"""
                    <div class="section-title">📈 Yaklaşan Kazanç Raporları</div>
                    <div class="earnings-box">
                        <div style="font-size: 13px; color: #f57f17; font-weight: 600; margin-bottom: 12px;">
                            ⚠️ {earnings.get('status', 'N/A')}
                        </div>
            """
            
            for earning in earnings.get("upcoming_earnings", [])[:3]:
                eps_beat = float(earning.get("expected_eps", 0)) > float(earning.get("previous_eps", 0))
                html += f"""
                        <div style="background: white; padding: 10px; border-radius: 4px; margin-bottom: 8px; font-size: 11px; border-left: 3px solid #fbc02d;">
                            <strong>{earning['company']} ({earning['ticker']})</strong><br>
                            {earning['date']} | {earning['quarter']}<br>
                            Beklenen: {earning['expected_eps']} | Önceki: {earning['previous_eps']} {'📈' if eps_beat else '📉'}<br>
                            <span style="color: #7f8c8d;">{earning['urgency']}</span>
                        </div>
                """
            
            html += """
                    </div>
            """
    
    # ========== PIYASA GENİŞLİĞİ ==========
    if advanced_features.get("market_breadth"):
        breadth = advanced_features["market_breadth"]
        
        html += f"""
                    <div class="
