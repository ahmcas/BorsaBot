# ============================================================
# mail_sender.py — Email Gönderim Sistemi (Profesyonel Versiyonu)
# ============================================================

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from datetime import datetime


def generate_html_body(recommendations, chart_paths):
    """Detaylı, profesyonel HTML email oluştur"""
    date_str = datetime.now().strftime("%d %B %Y, %H:%M")
    recs = recommendations.get("recommendations", [])
    market_mood = recommendations.get("market_mood", "⚪ Belirsiz")
    
    # Market mood'a göre renk
    mood_colors = {
        "🟢": "#27ae60",
        "🔴": "#e74c3c",
        "🟡": "#f39c12",
        "⚪": "#95a5a6"
    }
    mood_color = mood_colors.get(market_mood[0], "#667eea")
    
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
                .wrapper {{ max-width: 1000px; margin: 0 auto; background: white; }}
                
                .header {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    padding: 40px 30px;
                    color: white;
                    text-align: center;
                    border-bottom: 5px solid {mood_color};
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
                    background: {mood_color};
                    color: white;
                    padding: 20px;
                    text-align: center;
                    font-size: 18px;
                    font-weight: 600;
                    letter-spacing: 0.5px;
                }}
                
                .content {{ padding: 40px 30px; }}
                
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
                .rating-badge.rating-al {{ background: #27ae60; }}
                .rating-badge.rating-tut {{ background: #f39c12; }}
                .rating-badge.rating-sat {{ background: #e74c3c; }}
                
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
                
                <div class="mood-section">{market_mood}</div>
                
                <div class="content">
    """
    
    if recs:
        html += f'<div class="section-title">🎯 Bugün Önerilen Hisseler ({len(recs)} adet)</div>'
        
        for idx, rec in enumerate(recs, 1):
            ticker = rec.get("ticker", "N/A")
            sector = rec.get("sector", "Sektör")
            rating = rec.get("rating", "N/A")
            score = rec.get("score", 0)
            price = rec.get("price", "N/A")
            confidence = rec.get("confidence", "Orta")
            
            # Sinyaller
            signals = rec.get("signals", [])
            
            # Fibonacci
            support = rec.get("support", 0)
            resistance = rec.get("resistance", 0)
            
            # Risk/Reward
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
                        <div class="rating-badge rating-al">{rating}</div>
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
            
            # Sinyaller
            if signals:
                html += """
                    <div class="signals-box">
                        <h4>📊 Teknik Sinyaller</h4>
                """
                for signal in signals[:5]:  # Max 5 sinyal
                    html += f'<div class="signal-item">{signal}</div>'
                
                html += """
                    </div>
                """
            
            html += """
                </div>
            """
    else:
        html += '<div class="no-recommendation">⚠️ Bugün alım sinyali bulunamadı. Pazarı gözlemlemeye devam ediyoruz.</div>'
    
    # Grafikler
    if chart_paths:
        html += """
                <div class="charts-section">
                    <h2>📊 Teknik Analiz Grafikleri</h2>
        """
        for i, path in enumerate(chart_paths, 1):
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
                    <strong>Skor Ağırlıkları:</strong><br>
                    Teknik Analiz: %40 | Temel Analiz: %30 | Haber Sentiment: %20 | Momentum: %10<br>
                    <br>
                    <strong>Veri Kaynakları:</strong> Yahoo Finance, NewsAPI<br>
                    <strong>Analiz Türü:</strong> Günlük (1D) | Veriler son 200 güne dayanır
                </div>
            </div>
            
            <div class="footer">
                <div class="footer-brand">🤖 BorsaBot - Otomatik Borsa Analiz Sistemi</div>
                <p>Yapay Zeka destekli teknik ve haber analizi</p>
                <p style="margin-top: 15px; opacity: 0.7;">Bu email otomatik olarak oluşturulmuştur. Lütfen yanıt vermeyin.</p>
                <p style="margin-top: 10px; font-size: 11px; opacity: 0.6;">{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} UTC</p>
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
                        print(f"  ⚠️ Grafik ekleme hatası: {e}")
        
        server.send_message(msg)
        server.quit()
        
        print(f"✅ Email gönderildi!\n   Alan: {mail_recipient}\n   Konu: {subject}")
        return True
        
    except smtplib.SMTPAuthenticationError:
        print("❌ Gmail kimlik doğrulama hatası!")
        print("   → Gmail App Password doğru mu?")
        return False
    except Exception as e:
        print(f"❌ Email hatası: {e}")
        return False
