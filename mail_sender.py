# ============================================================
# mail_sender.py — Email Gönderim Sistemi (Geliştirilmiş)
# ============================================================
# Bu modül:
# 1) Detaylı analiz sonuçlarını HTML email'e formatlar
# 2) Teknik indikatörleri gösterir
# 3) Risk/Potansiyel analizi
# 4) Fibonacci seviyeleri
# 5) Grafikleri embed eder
# ============================================================

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from datetime import datetime


def get_market_mood_color(mood):
    """Pazar duygusuna göre renk döndür"""
    if "Çok Olumlu" in mood or "Güçlü" in mood:
        return "#27ae60"  # Yeşil
    elif "Olumlu" in mood:
        return "#2ecc71"  # Açık Yeşil
    elif "Olumsuz" in mood:
        return "#e74c3c"  # Kırmızı
    elif "Çok Olumsuz" in mood:
        return "#c0392b"  # Koyu Kırmızı
    else:
        return "#95a5a6"  # Gri


def generate_html_body(recommendations, chart_paths):
    """Detaylı HTML formatlı email gövdesi oluştur"""
    date_str = datetime.now().strftime("%d %B %Y, %H:%M")
    recs = recommendations.get("recommendations", [])
    market_mood = recommendations.get("market_mood", "⚪ Belirsiz")
    mood_color = get_market_mood_color(market_mood)
    
    html = f"""
    <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                * {{ margin: 0; padding: 0; box-sizing: border-box; }}
                body {{ 
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%);
                    color: #e0e0e0;
                    line-height: 1.6;
                }}
                .container {{
                    max-width: 900px;
                    margin: 0 auto;
                    background: #1f1f1f;
                    border-radius: 12px;
                    overflow: hidden;
                    box-shadow: 0 10px 40px rgba(0,0,0,0.5);
                }}
                .header {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    padding: 30px 20px;
                    text-align: center;
                    color: white;
                }}
                .header h1 {{
                    font-size: 28px;
                    margin-bottom: 5px;
                    font-weight: 700;
                }}
                .header p {{
                    font-size: 13px;
                    opacity: 0.9;
                }}
                .market-mood {{
                    background: {mood_color};
                    color: white;
                    padding: 15px 20px;
                    margin: 0;
                    text-align: center;
                    font-size: 16px;
                    font-weight: 600;
                }}
                .content {{
                    padding: 30px 20px;
                }}
                .section-title {{
                    font-size: 18px;
                    font-weight: 700;
                    color: #667eea;
                    margin-top: 25px;
                    margin-bottom: 15px;
                    border-bottom: 2px solid #667eea;
                    padding-bottom: 10px;
                    display: flex;
                    align-items: center;
                }}
                .section-title::before {{
                    content: '●';
                    margin-right: 10px;
                    font-size: 20px;
                }}
                .stock-card {{
                    background: linear-gradient(135deg, #2a2a2a 0%, #1f1f1f 100%);
                    border-left: 5px solid #667eea;
                    border-radius: 8px;
                    padding: 20px;
                    margin-bottom: 20px;
                    box-shadow: 0 4px 15px rgba(0,0,0,0.3);
                }}
                .stock-header {{
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    margin-bottom: 15px;
                    padding-bottom: 10px;
                    border-bottom: 1px solid #404040;
                }}
                .stock-rank {{
                    font-size: 24px;
                    font-weight: 700;
                    color: #667eea;
                }}
                .stock-ticker {{
                    font-size: 22px;
                    font-weight: 700;
                    color: #fff;
                }}
                .stock-sector {{
                    font-size: 12px;
                    color: #999;
                    text-transform: uppercase;
                    letter-spacing: 1px;
                    margin-top: 5px;
                }}
                .rating-badge {{
                    display: inline-block;
                    padding: 8px 16px;
                    background: #27ae60;
                    color: white;
                    border-radius: 20px;
                    font-weight: 600;
                    font-size: 14px;
                    box-shadow: 0 2px 10px rgba(39, 174, 96, 0.3);
                }}
                .rating-badge.al {{
                    background: #27ae60;
                }}
                .rating-badge.tut {{
                    background: #f39c12;
                }}
                .rating-badge.sat {{
                    background: #e74c3c;
                }}
                .price-score-section {{
                    display: grid;
                    grid-template-columns: 1fr 1fr 1fr;
                    gap: 15px;
                    margin: 15px 0;
                    text-align: center;
                }}
                .metric-box {{
                    background: rgba(102, 126, 234, 0.1);
                    border: 1px solid #667eea;
                    border-radius: 6px;
                    padding: 12px;
                }}
                .metric-label {{
                    font-size: 12px;
                    color: #aaa;
                    text-transform: uppercase;
                    letter-spacing: 0.5px;
                }}
                .metric-value {{
                    font-size: 20px;
                    font-weight: 700;
                    color: #667eea;
                    margin-top: 5px;
                }}
                .indicators-section {{
                    background: rgba(0,0,0,0.2);
                    border-radius: 6px;
                    padding: 12px;
                    margin: 15px 0;
                    font-size: 13px;
                }}
                .indicator {{
                    padding: 6px 0;
                    display: flex;
                    justify-content: space-between;
                    border-bottom: 1px solid rgba(255,255,255,0.05);
                }}
                .indicator:last-child {{
                    border-bottom: none;
                }}
                .indicator-name {{
                    color: #aaa;
                }}
                .indicator-value {{
                    color: #667eea;
                    font-weight: 600;
                }}
                .risk-potential {{
                    display: grid;
                    grid-template-columns: 1fr 1fr;
                    gap: 10px;
                    margin-top: 15px;
                }}
                .risk-box {{
                    background: rgba(231, 76, 60, 0.1);
                    border: 1px solid #e74c3c;
                    border-radius: 6px;
                    padding: 12px;
                    text-align: center;
                }}
                .risk-label {{
                    font-size: 12px;
                    color: #e74c3c;
                    text-transform: uppercase;
                    font-weight: 600;
                }}
                .risk-value {{
                    font-size: 18px;
                    color: #e74c3c;
                    font-weight: 700;
                    margin-top: 5px;
                }}
                .potential-box {{
                    background: rgba(39, 174, 96, 0.1);
                    border: 1px solid #27ae60;
                    border-radius: 6px;
                    padding: 12px;
                    text-align: center;
                }}
                .potential-label {{
                    font-size: 12px;
                    color: #27ae60;
                    text-transform: uppercase;
                    font-weight: 600;
                }}
                .potential-value {{
                    font-size: 18px;
                    color: #27ae60;
                    font-weight: 700;
                    margin-top: 5px;
                }}
                .fibonacci-section {{
                    background: rgba(0,0,0,0.2);
                    border-radius: 6px;
                    padding: 12px;
                    margin-top: 10px;
                    font-size: 12px;
                }}
                .fib-level {{
                    display: flex;
                    justify-content: space-between;
                    padding: 5px 0;
                    border-bottom: 1px solid rgba(255,255,255,0.05);
                }}
                .fib-level:last-child {{
                    border-bottom: none;
                }}
                .fib-name {{
                    color: #aaa;
                }}
                .fib-value {{
                    color: #667eea;
                    font-weight: 600;
                }}
                .charts-section {{
                    margin-top: 30px;
                    text-align: center;
                }}
                .charts-title {{
                    font-size: 16px;
                    font-weight: 700;
                    color: #667eea;
                    margin-bottom: 20px;
                }}
                .chart-img {{
                    max-width: 100%;
                    height: auto;
                    border-radius: 8px;
                    margin-bottom: 20px;
                    border: 1px solid #404040;
                    box-shadow: 0 4px 15px rgba(0,0,0,0.3);
                }}
                .footer {{
                    background: #0a0a0a;
                    padding: 20px;
                    text-align: center;
                    font-size: 12px;
                    color: #777;
                    border-top: 1px solid #404040;
                }}
                .footer p {{
                    margin: 5px 0;
                }}
                .disclaimer {{
                    background: rgba(243, 156, 18, 0.1);
                    border-left: 3px solid #f39c12;
                    padding: 12px;
                    margin: 20px 0;
                    border-radius: 4px;
                    font-size: 12px;
                    color: #f39c12;
                }}
                .no-recommendation {{
                    background: rgba(231, 76, 60, 0.1);
                    border-left: 3px solid #e74c3c;
                    padding: 15px;
                    border-radius: 4px;
                    text-align: center;
                    color: #e74c3c;
                    font-weight: 600;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>📊 Borsa Analiz Raporu</h1>
                    <p>{date_str} | Günlük Analiz</p>
                </div>
                
                <div class="market-mood">{market_mood}</div>
                
                <div class="content">
    """
    
    if recs:
        html += '<div class="section-title">🎯 Bugün Önerilen Hisseler ({} adet)</div>'.format(len(recs))
        
        for idx, rec in enumerate(recs, 1):
            ticker = rec.get('ticker', 'N/A')
            sector = rec.get('sector', 'Sektör Bilinmiyor')
            rating = rec.get('rating', 'N/A')
            score = rec.get('final_score', rec.get('score', 0))
            price = rec.get('current_price', 'N/A')
            reasoning = rec.get('reasoning', '')
            
            # Rating badge sınıfı
            rating_class = 'al' if 'AL' in rating.upper() else ('tut' if 'TUT' in rating.upper() else 'sat')
            
            html += f"""
                <div class="stock-card">
                    <div class="stock-header">
                        <div>
                            <div class="stock-rank">#{idx}</div>
                            <div class="stock-ticker">{ticker}</div>
                            <div class="stock-sector">{sector}</div>
                        </div>
                        <div class="rating-badge {rating_class}">🔥 {rating}</div>
                    </div>
                    
                    <div class="price-score-section">
                        <div class="metric-box">
                            <div class="metric-label">Fiyat</div>
                            <div class="metric-value">{price}</div>
                        </div>
                        <div class="metric-box">
                            <div class="metric-label">Skor</div>
                            <div class="metric-value">{score:.1f}/100</div>
                        </div>
                        <div class="metric-box">
                            <div class="metric-label">Güven</div>
                            <div class="metric-value">{'Yüksek' if score >= 70 else ('Orta' if score >= 50 else 'Düşük')}</div>
                        </div>
                    </div>
            """
            
            # Teknik Göstergeler
            if rec.get('technical_indicators'):
                indicators = rec.get('technical_indicators', {})
                html += '<div class="indicators-section"><strong>📈 Teknik Göstergeler</strong>'
                
                for ind_name, ind_value in indicators.items():
                    html += f'<div class="indicator"><span class="indicator-name">{ind_name}</span><span class="indicator-value">{ind_value}</span></div>'
                
                html += '</div>'
            
            # Risk & Potansiyel
            risk = rec.get('risk_percentage', 'N/A')
            potential = rec.get('potential_percentage', 'N/A')
            
            if risk != 'N/A' or potential != 'N/A':
                html += f"""
                <div class="risk-potential">
                    <div class="risk-box">
                        <div class="risk-label">⚠️ Destek (Risk)</div>
                        <div class="risk-value">{risk}</div>
                    </div>
                    <div class="potential-box">
                        <div class="potential-label">💰 Direnç (Potansiyel)</div>
                        <div class="potential-value">{potential}</div>
                    </div>
                </div>
                """
            
            # Fibonacci Seviyeleri
            if rec.get('fibonacci_levels'):
                fib = rec.get('fibonacci_levels', {})
                html += '<div class="fibonacci-section"><strong>Fibonacci Seviyeleri:</strong>'
                
                for level_name, level_value in fib.items():
                    html += f'<div class="fib-level"><span class="fib-name">{level_name}</span><span class="fib-value">{level_value}</span></div>'
                
                html += '</div>'
            
            # Analiz Nedeni
            if reasoning:
                html += f'<div style="margin-top: 10px; padding: 10px; background: rgba(102, 126, 234, 0.05); border-radius: 4px; font-size: 13px;"><strong>Analiz:</strong> {reasoning}</div>'
            
            html += '</div>'  # stock-card kapat
    else:
        html += '<div class="no-recommendation">⚠️ Bugün alım sinyali bulunamadı. Pazarı gözlemlemeye devam ediyoruz.</div>'
    
    # Grafikler
    if chart_paths:
        html += '<div class="charts-section"><div class="charts-title">📊 Teknik Analiz Grafikleri</div>'
        
        for i, path in enumerate(chart_paths, 1):
            filename = os.path.basename(path)
            html += f'<img src="cid:chart_{i}" class="chart-img" alt="Grafik {i}">'
        
        html += '</div>'
    
    # Disclaimer
    html += """
                <div class="disclaimer">
                    ⚠️ <strong>Önemli Uyarı:</strong> Bu analiz yatırım tavsiyesi değildir. 
                    Tüm yatırım kararlarınızı kendi araştırmanız ve risk analizi üzerine temellendiriniz. 
                    Geçmiş performans, gelecekteki sonuçları garanti etmez.
                </div>
                
                <div class="section-title">📋 Analiz Parametreleri</div>
                <div style="background: rgba(0,0,0,0.2); border-radius: 6px; padding: 12px; font-size: 12px; line-height: 2;">
                    <strong>Kullanılan Göstergeler:</strong> RSI (14), MACD (12,26,9), Bollinger Bands (20), SMA (20,50), Fibonacci Retracements<br>
                    <strong>Veri Kaynağı:</strong> Yahoo Finance, NewsAPI<br>
                    <strong>Analiz Süresi:</strong> 1 Gün | Ağırlıklar: Teknik %40, Temel %30, Haber %20, Momentum %10
                </div>
            </div>
            
            <div class="footer">
                <p>🤖 BorsaBot - Otomatik Borsa Analiz Sistemi</p>
                <p>Yapay Zeka destekli teknik ve temel analiz</p>
                <p style="margin-top: 10px; color: #555;">Bu email otomatik olarak oluşturulmuştur. Lütfen yanıt vermeyin.</p>
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
    
    # GitHub Secrets'ten değerleri oku
    mail_sender = os.environ.get("MAIL_SENDER")
    mail_password = os.environ.get("MAIL_PASSWORD")
    mail_recipient = os.environ.get("MAIL_RECIPIENT")
    
    # Kontrol et
    if not mail_sender:
        print("❌ MAIL_SENDER environment variable tanımlanmamış")
        return False
    if not mail_password:
        print("❌ MAIL_PASSWORD environment variable tanımlanmamış")
        return False
    if not mail_recipient:
        print("❌ MAIL_RECIPIENT environment variable tanımlanmamış")
        return False
    
    try:
        # Gmail SMTP sunucusuna bağlan
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()  # TLS şifrelemesini başlat
        
        # Giriş yap
        server.login(mail_sender, mail_password)
        print(f"✅ Gmail'e giriş yapıldı: {mail_sender}")
        
        # Email mesajını oluştur
        msg = MIMEMultipart("related")
        msg["From"] = mail_sender
        msg["To"] = mail_recipient
        msg["Subject"] = subject
        
        # HTML gövdesini ekle
        msg_alternative = MIMEMultipart("alternative")
        msg.attach(msg_alternative)
        msg_alternative.attach(MIMEText(html_body, "html"))
        
        # Grafikleri ekle (varsa)
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
                        print(f"  ⚠️  Grafik ekleme hatası: {chart_path} - {e}")
                else:
                    print(f"  ⚠️  Grafik bulunamadı: {chart_path}")
        
        # Email'i gönder
        server.send_message(msg)
        server.quit()
        
        print(f"✅ Email başarıyla gönderildi!")
        print(f"   Gönderen: {mail_sender}")
        print(f"   Alan: {mail_recipient}")
        print(f"   Konu: {subject}")
        return True
        
    except smtplib.SMTPAuthenticationError:
        print("❌ Gmail kimlik doğrulama hatası!")
        print("   ⚠️  Lütfen şunları kontrol edin:")
        print("   1. MAIL_SENDER doğru Gmail adresi mi?")
        print("   2. MAIL_PASSWORD 'Uygulama Şifresi' mi? (normal şifre değil)")
        print("   3. Gmail hesabında 2FA aktif mi?")
        print("   → Yeni uygulama şifresi oluştur: https://myaccount.google.com/apppasswords")
        return False
        
    except smtplib.SMTPException as e:
        print(f"❌ SMTP hata: {e}")
        return False
        
    except Exception as e:
        print(f"❌ Email gönderme hatası: {e}")
        import traceback
        traceback.print_exc()
        return False
