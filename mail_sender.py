# ============================================================
# mail_sender.py — Email Gönderim Sistemi (v4 - FINAL + GLOBAL)
# ============================================================

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from datetime import datetime


def generate_detailed_market_mood(market_mood: str, sector_scores: dict) -> dict:
    """
    Market mood'u detaylı analiz et.
    Hangi sektörler yukarı/aşağı gidiyor göster.
    """
    
    # Sektörleri skora göre sırala
    sorted_sectors = sorted(sector_scores.items(), key=lambda x: x[1], reverse=True)
    
    # Emoji'ler
    emoji_map = {
        "finans": "🏦",
        "teknoloji": "💻",
        "enerji": "⚡",
        "sağlık": "💊",
        "perakende": "🛒",
        "gida": "🍔",
        "telekom": "📱",
        "otomotiv": "🚗",
        "inşaat_gayrimenkul": "🏗️",
        "sigortalar": "🛡️",
        "turizm": "✈️",
        "savunma": "🎖️",
        "tekstil": "👕",
        "kimya": "🧪",
        "orman": "🌲",
        "medya": "📺",
        "genel": "📊"
    }
    
    # En iyi 3 sektör
    best_3 = sorted_sectors[:3]
    worst_3 = sorted_sectors[-3:]
    
    # Ortalama skor
    avg_score = sum(sector_scores.values()) / len(sector_scores) if sector_scores else 0
    
    # Detaylı açıklama
    if avg_score >= 0.4:
        title = "🟢 ÇOK OLUMLU - Piyasalar Güçlü Yukarı Baskı Altında"
        description = f"Küresel ve yerel piyasalar keskin yükseliş trendinde. Haber akışı olumlu, yatırımcı duygusu pozitif. Riski yönetmek şartıyla agresif pozisyon alınabilir."
        recommendation = "Alım sinyalleri güçlü. Portföy pozisyonunu artırabilirsiniz. Stop-loss belirleyerek riski kontrol edin."
        color = "#27ae60"
    
    elif avg_score >= 0.2:
        title = "🟢 OLUMLU - Pozitif Sinyaller Hakimiyetinde"
        description = f"Piyasalar yavaş yavaş yukarı yönlü. Çoğu sektörde pozitif momentum. Risk düşük seviyelerde. Temkinli bir yükseliş bekleniyor."
        recommendation = "Seçici alımlar yapabilirsiniz. Yüksek volatilite sektörlerinden kaçının. Pozisyon büyüklüğünü kontrol edin."
        color = "#2ecc71"
    
    elif avg_score >= -0.2:
        title = "🟡 KARIŞIK - Belirsiz Piyasa Durumu"
        description = f"Piyasa yönü net değil. Bazı sektörler yukarı, bazıları aşağı. Dengeli durum gözleniyor. Volatilite orta seviyelerde."
        recommendation = "Pozisyon almadan önce daha net sinyal bekleyebilirsiniz. Mevcut pozisyonları değerlendir. Risk yönetimini sıkı tutun."
        color = "#f39c12"
    
    elif avg_score >= -0.4:
        title = "🔴 OLUMSUZ - Aşağı Yönlü Basınç Var"
        description = f"Piyasalar zayıflık gösteriyor. Çoğu sektöre satış baskısı. Yatırımcı duygusu negatif. Koruma pozisyonları alınmalı."
        recommendation = "Yeni pozisyonlardan uzak durun. Riski azaltmayı düşünün. Put opsiyon veya stop-loss kullanın."
        color = "#e74c3c"
    
    else:
        title = "🔴 ÇOK OLUMSUZ - Yüksek Risk Dönem"
        description = f"Piyasalar panik modunda. Keskin satışlar yaşanıyor. Ekonomik endişeler y��ksek. Acil koruma gerekli."
        recommendation = "Defansif sektörlere kaçın. Nakit pozisyonu güçlü tutun. Yüksek risk pozisyonlarını kapatın."
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
    """Detaylı, profesyonel HTML email oluştur (Küresel Analiz ile)"""
    date_str = datetime.now().strftime("%d %B %Y, %H:%M")
    recs = recommendations.get("recommendations", [])
    sector_scores = recommendations.get("sector_scores", {})
    global_analysis = recommendations.get("global_analysis", {})
    trend_opportunities = recommendations.get("trend_opportunities", [])
    
    # Detaylı market mood analiz yap
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
                
                /* KÜRESEL ANALİZ SEKSİYONU */
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
            </style>
        </head>
        <body>
            <div class="wrapper">
                <div class="header">
                    <h1>📊 Borsa Analiz Raporu</h1>
                    <div class="date">{date_str} | Günlük Analiz</div>
                </div>
                
                <!-- DETAYLI MARKET MOOD BÖLÜMÜ -->
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
    
    # Emoji mapping
    emoji_map = {
        "finans": "🏦", "teknoloji": "💻", "enerji": "⚡", "sağlık": "💊",
        "perakende": "🛒", "gida": "🍔", "telekom": "📱", "otomotiv": "🚗",
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
    
    # ========== KÜRESEL ANALİZ BÖLÜMÜ ==========
    html += f"""
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
                                <span class="global-label">Piyasa Etkisi</span>
                                <span class="global-value" style="font-size: 11px;">{us_debt.get('impact', 'N/A')[:50]}...</span>
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
        html += f"""
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
    
    # Emtia Rekorları
    if global_analysis.get("commodity_records"):
        records = global_analysis["commodity_records"]
        html += f"""
                    <div class="section-title">📈 Emtia Rekor Analizi</div>
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin: 20px 0;">
        """
        
        for key, record in records.items():
            record_status = "🔥 REKOR YAKINI!" if record['is_record'] else f"↑ {record['distance_to_high']:.1f}% uzakta"
            
            html += f"""
                        <div class="global-box">
                            <h3>{record['name'].title()}</h3>
                            <div class="global-stat">
                                <span class="global-label">Şu Anki</span>
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
                
                for event in record['events'][:2]:  # Son 2 olay
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
    
    # Jeopolitik Olaylar
    if global_analysis.get("geopolitical"):
        geopolitical = global_analysis["geopolitical"]
        
        if geopolitical.get("events"):
            html += f"""
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
            
            html += f"""
                    <div style="background: #e8f5e9; border-left: 4px solid #4caf50; padding: 15px; border-radius: 4px; margin: 20px 0;">
                        <strong>Genel Piyasa Ortamı:</strong> {geopolitical.get('overall_sentiment', 'Bilinmiyor')}
                    </div>
            """
    
    # Borsa Tatilleri
    if global_analysis.get("exchange_holidays"):
        holidays = global_analysis["exchange_holidays"]
        
        if holidays.get("upcoming_holidays"):
            html += f"""
                    <div class="section-title">📅 Yakın Borsa Tatilleri</div>
                    <div style="background: #e3f2fd; border-left: 4px solid #2196f3; padding: 15px; border-radius: 4px; margin: 20px 0;">
                        <strong>ℹ️ Bilgi:</strong> {holidays.get('recommendation', 'Tatil günlerinde volatilite artabilir.')}
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
    
    # Yükseliş Trendine Giren Hisseler
    if trend_opportunities:
        html += f"""
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
    
    # Önerilen Hisseler
    if recs:
        html += f'<div class="section-title">🎯 Bugün Önerilen Hisseler ({len(recs)} adet)</div>'
        
        for idx, rec in enumerate(recs, 1):
            ticker = rec.get("ticker", "N/A")
            sector = rec.get("sector", "Sektör")
            rating = rec.get("rating", "N/A")
            score = rec.get("score", 0)
            price = rec.get("price", "N/A")
            confidence = rec.get("confidence", "Orta")
            
            signals = rec.get("signals", [])
            support = rec.get("support", 0)
            resistance = rec.get("resistance", 0)
            risk = rec.get("risk_pct", 0)
            reward = rec.get("reward_pct", 0)
            
            rank_class = f"rank{idx}"
            
            html += f"""
                <div class="stock-card {rank_class}">
                    <div class="rank-label">#{idx}</div>
                    
                    <div class="stock-header">
                        <div class="stock-header-left">
                            <h2>{ticker}</h2>
                            <div class="sector">{sector}</div>
                        </div>
                        <div class="rating-badge">{rating}</div>
                    </div>
                    
                    <div class="metrics-grid">
                        <div class="metric-box">
                            <div class="metric-label">Fiyat</div>
                            <div class="metric-value">{price}</div>
                            <div class="metric-sub">Cari</div>
                        </div>
                        <div class="metric-box">
                            <div class="metric-label">Skor</div>
                            <div class="metric-value">{score:.1f}</div>
                            <div class="metric-sub">/100</div>
                        </div>
                        <div class="metric-box">
                            <div class="metric-label">Güven</div>
                            <div class="metric-value">{'🟢' if score >= 70 else '🟡' if score >= 50 else '🔴'}</div>
                            <div class="metric-sub">{confidence}</div>
                        </div>
                    </div>
                    
                    <div class="indicators-section">
                        <h4>📈 Teknik Göstergeler</h4>
                        <div class="indicator-row">
                            <span class="indicator-label">RSI (14)</span>
                            <span class="indicator-value">{rec.get('rsi', 'N/A')}</span>
                        </div>
                        <div class="indicator-row">
                            <span class="indicator-label">MACD Histogram</span>
                            <span class="indicator-value {'positive' if rec.get('macd_histogram', 0) >= 0 else 'negative'}">{rec.get('macd_histogram', 'N/A')}</span>
                        </div>
                        <div class="indicator-row">
                            <span class="indicator-label">Bollinger Bands</span>
                            <span class="indicator-value">{rec.get('bollinger_position', 'N/A').title()}</span>
                        </div>
                        <div class="indicator-row">
                            <span class="indicator-label">SMA 20</span>
                            <span class="indicator-value">{rec.get('sma_short', 'N/A')}</span>
                        </div>
                        <div class="indicator-row">
                            <span class="indicator-label">SMA 50</span>
                            <span class="indicator-value">{rec.get('sma_long', 'N/A')}</span>
                        </div>
                        <div class="indicator-row">
                            <span class="indicator-label">Momentum (10D)</span>
                            <span class="indicator-value {'positive' if rec.get('momentum_pct', 0) >= 0 else 'negative'}">{rec.get('momentum_pct', 'N/A')}</span>
                        </div>
                    </div>
                    
                    <div class="risk-potential-grid">
                        <div class="risk-box">
                            <h4>⚠️ Destek (Risk)</h4>
                            <div class="value">{risk}%</div>
                            <div class="detail">Fib 0.382: {support}</div>
                        </div>
                        <div class="potential-box">
                            <h4>💰 Direnç (Potansiyel)</h4>
                            <div class="value">{reward}%</div>
                            <div class="detail">Fib 0.618: {resistance}</div>
                        </div>
                    </div>
                    
                    <div class="fibonacci-section">
                        <h4>🎯 Fibonacci Seviyeleri</h4>
            """
            
            fib = rec.get("fibonacci", {})
            fib_levels = [
                ("0.236", fib.get("fib_0.236", "N/A")),
                ("0.382", fib.get("fib_0.382", "N/A")),
                ("0.500", fib.get("fib_0.500", "N/A")),
                ("0.618", fib.get("fib_0.618", "N/A")),
                ("0.786", fib.get("fib_0.786", "N/A")),
            ]
            
            for level_name, level_value in fib_levels:
                html += f"""
                        <div class="fib-row">
                            <span class="fib-label">Fib {level_name}</span>
                            <span class="fib-value">{level_value}</span>
                        </div>
                """
            
            html += """
                    </div>
            """
            
            if signals:
                html += """
                    <div class="signals-box">
                        <h4>📊 Teknik Sinyaller</h4>
                """
                for signal in signals[:5]:
                    html += f'<div class="signal-item">{signal}</div>'
                
                html += """
                    </div>
                """
            
            html += """
                </div>
            """
    else:
        html += '<div class="no-recommendation">⚠️ Bugün alım sinyali bulunamadı. Pazarı gözlemlemeye devam ediyoruz.</div>'
    
    if chart_paths:
        html += """
                <div class="charts-section">
                    <h2>📊 Teknik Analiz Grafikleri</h2>
        """
        for i, path in enumerate(chart_paths, 1):
            if os.path.exists(path):
                html += f'<img src="cid:chart_{i}" class="chart-img" alt="Grafik {i}">'
        
        html += """
                </div>
        """
    
    html += f"""
                <div class="disclaimer">
                    <strong>⚠️ Önemli Uyarı:</strong> Bu analiz tamamen otomatik olarak üretilmiştir ve <strong>yatırım tavsiyesi DEĞİLDİR</strong>. 
                    Tüm yatırım kararlarınızı kendi araştırmanız, risk analizi ve profesyonel danışmanlığa dayandırınız. 
                    Geçmiş performans gelecekteki sonuçların garantisi değildir. Borsa işlemleri ciddi finansal riskleri taşır.
                </div>
                
                <div class="section-title">ℹ️ Analiz Detayları</div>
                <div style="background: #f8f9fa; padding: 20px; border-radius: 6px; font-size: 13px; line-height: 1.8; color: #2c3e50;">
                    <strong>Kullanılan Teknik Göstergeler:</strong><br>
                    • RSI (Relative Strength Index) - Momentum ve aşırı alım/satım seviyeleri<br>
                    • MACD (Moving Average Convergence Divergence) - Trend ve momentum<br>
                    • Bollinger Bands - Volatilite ve fiyat oynaklığı<br>
                    • SMA (Simple Moving Average) - Kısa (20) ve uzun (50) dönem trendleri<br>
                    • Fibonacci Retracements - Destek ve direnç seviyeleri<br>
                    • Momentum Analizi - 10 günlük fiyat değişimi<br>
                    <br>
                    <strong>Küresel Analiz Komponenti:</strong><br>
                    • ABD Dış Borcu Takibi - Para politikası ve dolar etkisi<br>
                    • Emtia Fiyat Analizi - Altın, Gümüş, Bakır, Petrol, Doğalgaz<br>
                    • Emtia Rekor Detektasyonu - All-time high yaklaşımları ve geçmiş olaylar<br>
                    • Jeopolitik Olay Takibi - Küresel volatilite tetikleyicileri<br>
                    • Borsa Tatil Takvimi - Likidite ve volatilite beklentileri<br>
                    • Trend Reversal Analizi - Support breakout fırsatları (Destek → Direnç geçişleri)<br>
                    <br>
                    <strong>Skor Ağırlıkları:</strong><br>
                    Teknik Analiz: %40 | Temel Analiz: %30 | Haber Sentiment: %20 | Momentum: %10<br>
                    <br>
                    <strong>Veri Kaynakları:</strong> Yahoo Finance, Alpha Vantage, IEX Cloud, NewsAPI, Dünya Bankası, İstatistik Kuruluşları<br>
                    <strong>Analiz Türü:</strong> Günlük (1D) + Küresel Makro | Veriler son 200 güne dayanır<br>
                    <br>
                    <strong>Yenilikler v2.0:</strong><br>
                    ✓ ABD Dış Borcu izlemesi ve piyasa etkisi analizi<br>
                    ✓ 5 emtianın gerçek zamanlı fiyat takibi<br>
                    ✓ Emtia rekor seviyeleri ve geçmiş olaylar<br>
                    ✓ Jeopolitik olay takibi ve piyasa etkileri<br>
                    ✓ 5 büyük borsanın tatil takvimi<br>
                    ✓ Support breakout trend analizi<br>
                </div>
            </div>
            
            <div class="footer">
                <div class="footer-brand">🤖 BorsaBot v2.0 - Akıllı Küresel Borsa Analiz Sistemi</div>
                <p>Yapay Zeka + Makroekonomik Analiz + Teknik Analiz + Jeopolitik Takibi</p>
                <p style="margin-top: 15px; opacity: 0.7;">Bu email otomatik olarak oluşturulmuştur. Lütfen yanıt vermeyin.</p>
                <p style="margin-top: 10px; font-size: 11px; opacity: 0.6;">{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} UTC+3</p>
            </div>
        </div>
        </body>
    </html>
    """
    
    return html


def send_email(html_body, chart_paths=None, subject=None):
    """Gmail SMTP üzerinden email gönder"""
    
    if subject is None:
        subject = f"📊 Borsa Analiz - {datetime.now().strftime('%d %b %Y')}"
    
    mail_sender = os.environ.get("MAIL_SENDER")
    mail_password = os.environ.get("MAIL_PASSWORD")
    mail_recipient = os.environ.get("MAIL_RECIPIENT")
    
    if not mail_sender or not mail_password or not mail_recipient:
        print("❌ Email ayarları eksik")
        print("   Şu env variables gerekli:")
        print("   - MAIL_SENDER")
        print("   - MAIL_PASSWORD (Gmail App Password)")
        print("   - MAIL_RECIPIENT")
        return False
    
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(mail_sender, mail_password)
        print(f"✅ Gmail'e giriş yapıldı: {mail_sender}")
        
        msg = MIMEMultipart("related")
        msg["From"] = mail_sender
        msg["To"] = mail_recipient
        msg["Subject"] = subject
        
        msg_alternative = MIMEMultipart("alternative")
        msg.attach(msg_alternative)
        msg_alternative.attach(MIMEText(html_body, "html"))
        
        if chart_paths:
            for i, chart_path in enumerate(chart_paths, 1):
                if os.path.exists(chart_path):
                    try:
                        with open(chart_path, "rb") as attachment:
                            image = MIMEImage(attachment.read())
                            image.add_header("Content-ID", f"<chart_{i}>")
                            image.add_header("Content-Disposition", "inline", filename=os.path.basename(chart_path))
                            msg.attach(image)
                        print(f"  📎 Grafik eklendi: {os.path.basename(chart_path)}")
                    except Exception as e:
                        print(f"  ⚠️  Grafik ekleme hatası: {e}")
        
        server.send_message(msg)
        server.quit()
        
        print(f"✅ Email başarıyla gönderildi!")
        print(f"   Alan: {mail_recipient}")
        print(f"   Konu: {subject}")
        return True
        
    except smtplib.SMTPAuthenticationError:
        print("❌ Gmail kimlik doğrulama hatası!")
        print("   → Gmail App Password doğru mu kontrol et")
        print("   → 2FA aktif mi kontrol et (gerekli)")
        return False
    
    except smtplib.SMTPException as e:
        print(f"❌ SMTP hatası: {e}")
        return False
    
    except Exception as e:
        print(f"❌ Email gönderme hatası: {e}")
        return False


if __name__ == "__main__":
    # Test
    test_data = {
        "recommendations": [
            {
                "ticker": "AKBANK.IS",
                "score": 75,
                "rating": "🔥 GÜÇLÜ AL",
                "sector": "finans",
                "price": 1234.50,
                "confidence": "Yüksek",
                "rsi": 35.2,
                "macd_histogram": 0.0045,
                "bollinger_position": "orta",
                "sma_short": 1200,
                "sma_long": 1180,
                "momentum_pct": 2.5,
                "support": 1100,
                "resistance": 1350,
                "risk_pct": 10,
                "reward_pct": 15,
                "signals": ["RSI 35.2 → Oversold", "MACD → Bullish"],
                "fibonacci": {
                    "fib_0.236": 1050,
                    "fib_0.382": 1100,
                    "fib_0.500": 1150,
                    "fib_0.618": 1200,
                    "fib_0.786": 1250
                }
            }
        ],
        "market_mood": "🟢 OLUMLU",
        "sector_scores": {
            "finans": 0.35,
            "teknoloji": 0.25,
            "enerji": -0.15,
            "sağlık": 0.40,
            "genel": 0.2
        },
        "global_analysis": {
            "us_debt": {
                "level": "🔴 AŞIRI YÜKSEK",
                "current_debt_billion": 35500,
                "risk": "Çok Yüksek",
                "impact": "USD zayıflaması, enflasyon baskısı",
                "trend": "📈 Hızlı Artış"
            },
            "commodities": {
                "gold": {"current": 2150, "change": 1.5},
                "silver": {"current": 28.5, "change": -0.8},
                "copper": {"current": 4.15, "change": 2.1},
                "oil": {"current": 85.5, "change": -1.2}
            }
        },
        "trend_opportunities": []
    }
    
    html = generate_html_body(test_data)
    print(f"✅ HTML oluşturuldu ({len(html)} karakter)")
    print(f"   Email template hazır ve test edildi")
