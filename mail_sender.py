# ============================================================
# mail_sender.py — Email Gönderim Sistemi (v6 - ULTRA FINAL)
# ============================================================
# Özellikler:
# 1. Profesyonel HTML Email
# 2. Grafikleri ekle
# 3. Detaylı analiz raporu
# 4. Gmail SMTP
# ============================================================

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from datetime import datetime
import config


def generate_html_body(recommendations, chart_paths=None) -> str:
    """Profesyonel HTML Email Oluştur"""
    
    try:
        date_str = datetime.now().strftime("%d %B %Y, %H:%M")
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                * {{ margin: 0; padding: 0; box-sizing: border-box; }}
                
                body {{ 
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: #333;
                    line-height: 1.6;
                }}
                
                .container {{ 
                    max-width: 1000px; 
                    margin: 0 auto; 
                    background: white;
                    box-shadow: 0 10px 40px rgba(0,0,0,0.1);
                }}
                
                .header {{ 
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 40px 30px;
                    text-align: center;
                }}
                
                .header h1 {{ font-size: 32px; margin-bottom: 10px; }}
                .header p {{ font-size: 14px; opacity: 0.9; }}
                
                .content {{ padding: 30px; }}
                
                .section {{ margin-bottom: 30px; }}
                
                .section-title {{ 
                    font-size: 22px; 
                    font-weight: bold; 
                    color: #2c3e50;
                    margin-bottom: 20px;
                    padding-bottom: 10px;
                    border-bottom: 3px solid #667eea;
                }}
                
                .stock-card {{ 
                    background: #f8f9fa;
                    border-left: 5px solid #667eea;
                    border-radius: 8px;
                    padding: 25px;
                    margin-bottom: 20px;
                    transition: transform 0.2s;
                }}
                
                .stock-card:hover {{ transform: translateX(5px); }}
                
                .stock-header {{ 
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    margin-bottom: 20px;
                }}
                
                .ticker {{ 
                    font-size: 28px;
                    font-weight: 700;
                    color: #2c3e50;
                }}
                
                .sector {{ 
                    font-size: 12px;
                    color: #7f8c8d;
                    text-transform: uppercase;
                    margin-top: 5px;
                }}
                
                .rating-badge {{ 
                    display: inline-block;
                    padding: 10px 20px;
                    background: #667eea;
                    color: white;
                    border-radius: 25px;
                    font-weight: bold;
                    font-size: 14px;
                }}
                
                .metrics {{ 
                    display: grid;
                    grid-template-columns: repeat(3, 1fr);
                    gap: 15px;
                    margin-bottom: 20px;
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
                    margin-bottom: 8px;
                    font-weight: 600;
                }}
                
                .metric-value {{ 
                    font-size: 24px;
                    font-weight: bold;
                    color: #667eea;
                }}
                
                .technical-indicators {{ 
                    background: white;
                    border: 1px solid #ecf0f1;
                    border-radius: 6px;
                    padding: 15px;
                    margin-bottom: 20px;
                }}
                
                .indicator-row {{ 
                    display: grid;
                    grid-template-columns: repeat(2, 1fr);
                    gap: 15px;
                    margin-bottom: 15px;
                }}
                
                .indicator-item {{ 
                    padding: 10px;
                    background: #f8f9fa;
                    border-radius: 4px;
                }}
                
                .indicator-label {{ 
                    font-size: 12px;
                    color: #7f8c8d;
                    font-weight: 600;
                    margin-bottom: 5px;
                }}
                
                .indicator-value {{ 
                    font-size: 18px;
                    font-weight: bold;
                    color: #2c3e50;
                }}
                
                .rr-section {{ 
                    display: grid;
                    grid-template-columns: 1fr 1fr;
                    gap: 15px;
                    margin-bottom: 20px;
                }}
                
                .rr-box {{ 
                    border-radius: 6px;
                    padding: 20px;
                    color: white;
                    text-align: center;
                }}
                
                .risk-box {{ background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%); }}
                .reward-box {{ background: linear-gradient(135deg, #27ae60 0%, #229954 100%); }}
                
                .rr-label {{ 
                    font-size: 12px;
                    text-transform: uppercase;
                    margin-bottom: 10px;
                    opacity: 0.9;
                }}
                
                .rr-value {{ 
                    font-size: 28px;
                    font-weight: bold;
                }}
                
                .signals {{ 
                    background: #f0f7ff;
                    border-left: 4px solid #3498db;
                    padding: 15px;
                    margin-bottom: 20px;
                    border-radius: 4px;
                }}
                
                .signals h4 {{ 
                    color: #3498db;
                    margin-bottom: 10px;
                    font-size: 14px;
                }}
                
                .signals ul {{ 
                    list-style: none;
                    padding: 0;
                }}
                
                .signals li {{ 
                    padding: 5px 0;
                    font-size: 13px;
                    color: #2c3e50;
                }}
                
                .fibonacci {{ 
                    background: white;
                    border: 1px solid #ecf0f1;
                    border-radius: 6px;
                    padding: 15px;
                    margin-bottom: 20px;
                }}
                
                .fibonacci h4 {{ 
                    color: #2c3e50;
                    margin-bottom: 10px;
                    font-size: 14px;
                }}
                
                .fib-grid {{ 
                    display: grid;
                    grid-template-columns: repeat(3, 1fr);
                    gap: 10px;
                }}
                
                .fib-item {{ 
                    background: #f8f9fa;
                    padding: 10px;
                    border-radius: 4px;
                    text-align: center;
                }}
                
                .fib-label {{ 
                    font-size: 11px;
                    color: #7f8c8d;
                    margin-bottom: 5px;
                }}
                
                .fib-value {{ 
                    font-size: 16px;
                    font-weight: bold;
                    color: #667eea;
                }}
                
                .disclaimer {{ 
                    background: #fffbf5;
                    border-left: 4px solid #f39c12;
                    padding: 20px;
                    margin: 30px 0;
                    border-radius: 4px;
                    font-size: 12px;
                    color: #d68910;
                }}
                
                .footer {{ 
                    background: #2c3e50;
                    color: white;
                    padding: 30px;
                    text-align: center;
                    font-size: 12px;
                }}
                
                .footer p {{ margin: 5px 0; }}
                
                .chart {{ 
                    margin: 20px 0;
                    text-align: center;
                }}
                
                .chart img {{ 
                    max-width: 100%;
                    height: auto;
                    border-radius: 6px;
                    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
                }}
                
                .no-data {{ 
                    background: #fef5f5;
                    border-left: 4px solid #e74c3c;
                    padding: 20px;
                    border-radius: 4px;
                    text-align: center;
                    color: #e74c3c;
                    font-weight: 600;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <!-- HEADER -->
                <div class="header">
                    <h1>📊 Borsa Analiz Raporu</h1>
                    <p>{date_str} | Günlük Teknik Analiz</p>
                </div>
                
                <!-- CONTENT -->
                <div class="content">
                    <!-- ÖNERİLER BÖLÜMÜ -->
                    <div class="section">
                        <div class="section-title">🎯 Önerilen Hisseler</div>
        """
        
        recs = recommendations.get("recommendations", [])
        
        if recs:
            for i, rec in enumerate(recs, 1):
                ticker = rec.get('ticker', 'N/A')
                sector = rec.get('sector', 'Genel').replace('_', ' ').title()
                score = rec.get('score', 0)
                rating = rec.get('rating', '❓')
                price = rec.get('price', 0)
                
                rsi = rec.get('rsi', 0)
                macd = rec.get('macd_histogram', 0)
                bollinger = rec.get('bollinger_position', 'orta')
                sma_short = rec.get('sma_short', 0)
                sma_long = rec.get('sma_long', 0)
                momentum = rec.get('momentum_pct', 0)
                trend = rec.get('trend', 'Nötr')
                support = rec.get('support', 0)
                resistance = rec.get('resistance', 0)
                reward_pct = rec.get('reward_pct', 0)
                risk_pct = rec.get('risk_pct', 0)
                confidence = rec.get('confidence', 'Orta')
                signals = rec.get('signals', [])
                
                html += f"""
                    <div class="stock-card">
                        <!-- BAŞLIK -->
                        <div class="stock-header">
                            <div>
                                <div class="ticker">{ticker}</div>
                                <div class="sector">{sector}</div>
                            </div>
                            <div class="rating-badge">{rating}</div>
                        </div>
                        
                        <!-- METRIKLER -->
                        <div class="metrics">
                            <div class="metric-box">
                                <div class="metric-label">Skor</div>
                                <div class="metric-value">{score:.1f}</div>
                            </div>
                            <div class="metric-box">
                                <div class="metric-label">Fiyat</div>
                                <div class="metric-value">${price:.2f}</div>
                            </div>
                            <div class="metric-box">
                                <div class="metric-label">Güven</div>
                                <div class="metric-value">{confidence}</div>
                            </div>
                        </div>
                        
                        <!-- TEKNİK GÖSTERGELER -->
                        <div class="technical-indicators">
                            <h4 style="margin-bottom: 15px; color: #2c3e50;">📊 Teknik Göstergeler</h4>
                            <div class="indicator-row">
                                <div class="indicator-item">
                                    <div class="indicator-label">RSI (14)</div>
                                    <div class="indicator-value">{rsi:.1f}</div>
                                </div>
                                <div class="indicator-item">
                                    <div class="indicator-label">MACD Histogram</div>
                                    <div class="indicator-value">{macd:.6f}</div>
                                </div>
                            </div>
                            <div class="indicator-row">
                                <div class="indicator-item">
                                    <div class="indicator-label">SMA 20</div>
                                    <div class="indicator-value">${sma_short:.2f}</div>
                                </div>
                                <div class="indicator-item">
                                    <div class="indicator-label">SMA 50</div>
                                    <div class="indicator-value">${sma_long:.2f}</div>
                                </div>
                            </div>
                            <div class="indicator-row">
                                <div class="indicator-item">
                                    <div class="indicator-label">Momentum</div>
                                    <div class="indicator-value">{momentum:+.2f}%</div>
                                </div>
                                <div class="indicator-item">
                                    <div class="indicator-label">Bollinger</div>
                                    <div class="indicator-value">{bollinger.title()}</div>
                                </div>
                            </div>
                        </div>
                        
                        <!-- RISK/REWARD -->
                        <div class="rr-section">
                            <div class="rr-box risk-box">
                                <div class="rr-label">Risk Seviyesi</div>
                                <div class="rr-value">{risk_pct:.1f}%</div>
                            </div>
                            <div class="rr-box reward-box">
                                <div class="rr-label">Potansiyel Kazanç</div>
                                <div class="rr-value">{reward_pct:+.1f}%</div>
                            </div>
                        </div>
                        
                        <!-- SİNYALLER -->
                        <div class="signals">
                            <h4>⚡ Analiz Sinyalleri</h4>
                            <ul>
        """
                
                for signal in signals[:5]:
                    html += f"<li>✓ {signal}</li>"
                
                html += f"""
                            </ul>
                        </div>
                        
                        <!-- TREND VE SEVİYELER -->
                        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-bottom: 20px;">
                            <div style="background: #f8f9fa; padding: 15px; border-radius: 6px;">
                                <h4 style="color: #2c3e50; font-size: 12px; text-transform: uppercase; margin-bottom: 10px;">📈 Trend</h4>
                                <div style="font-size: 16px; font-weight: bold; color: #667eea;">{trend}</div>
                            </div>
                            <div style="background: #f8f9fa; padding: 15px; border-radius: 6px;">
                                <h4 style="color: #2c3e50; font-size: 12px; text-transform: uppercase; margin-bottom: 10px;">🎯 Destek/Direnç</h4>
                                <div style="font-size: 12px; color: #2c3e50;">
                                    Destek: <strong>${support:.2f}</strong><br>
                                    Direnç: <strong>${resistance:.2f}</strong>
                                </div>
                            </div>
                        </div>
                        
                        <!-- FIBONACCI SEVİYELERİ -->
                        <div class="fibonacci">
                            <h4>📊 Fibonacci Seviyeleri</h4>
                            <div class="fib-grid">
                                <div class="fib-item">
                                    <div class="fib-label">Mevcut</div>
                                    <div class="fib-value">${price:.2f}</div>
                                </div>
                                <div class="fib-item">
                                    <div class="fib-label">Fib 0.618</div>
                                    <div class="fib-value">${support:.2f}</div>
                                </div>
                                <div class="fib-item">
                                    <div class="fib-label">Fib 0.236</div>
                                    <div class="fib-value">${resistance:.2f}</div>
                                </div>
                            </div>
                        </div>
                    </div>
                """
        else:
            html += """
                    <div class="no-data">
                        ❌ Bugün için uygun alım sinyali bulunamadı
                    </div>
            """
        
        html += """
                    </div>
                    
                    <!-- DISCLAIMER -->
                    <div class="disclaimer">
                        <strong>⚠️ Önemli Uyarı:</strong> Bu analiz tamamen otomatik olarak üretilmiştir ve 
                        <strong>yatırım tavsiyesi DEĞİLDİR</strong>. Tüm yatırım kararlarınızı kendi araştırmanız, 
                        risk analizi ve profesyonel danışmanlığa dayandırınız. Kripto varlıklar ve hisse senetleri 
                        yüksek riskli yatırımlardır.
                    </div>
                    
                    <!-- FOOTER -->
                </div>
                
                <div class="footer">
                    <p style="font-size: 16px; font-weight: 600; margin-bottom: 10px;">🤖 BorsaBot v7.0</p>
                    <p>Akıllı Teknik Analiz & Haber Sentimen Sistemi</p>
                    <p style="margin-top: 15px; opacity: 0.8;">
                        Analiz Tarihi: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}<br>
                        Sistem: Otomatik Teknik Analiz + Haber Sentiment + Fibonacci Retracement
                    </p>
                    <p style="margin-top: 15px; opacity: 0.6; font-size: 11px;">
                        Bu email otomatik olarak oluşturulmuştur. Lütfen yanıt vermeyin.
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html
    
    except Exception as e:
        print(f"❌ HTML oluşturma hatası: {e}")
        return "<html><body><h1>Email oluşturulamadı</h1></body></html>"


def send_email(html_body: str, chart_paths: list = None) -> bool:
    """Gmail SMTP ile Email Gönder"""
    
    try:
        # Config kontrol
        mail_sender = config.MAIL_SENDER
        mail_password = config.MAIL_PASSWORD
        mail_recipient = config.MAIL_RECIPIENT
        
        if not mail_sender or not mail_password or not mail_recipient:
            print("❌ Email ayarları eksik (.env dosyasını kontrol et)")
            print(f"   MAIL_SENDER: {bool(mail_sender)}")
            print(f"   MAIL_PASSWORD: {bool(mail_password)}")
            print(f"   MAIL_RECIPIENT: {bool(mail_recipient)}")
            return False
        
        # Gmail SMTP Bağlantısı
        print("   📤 Gmail'e bağlanıyor...")
        server = smtplib.SMTP(config.SMTP_SERVER, config.SMTP_PORT)
        server.starttls()
        server.login(mail_sender, mail_password)
        print(f"   ✅ Gmail'e giriş yapıldı: {mail_sender}")
        
        # Email Oluştur
        msg = MIMEMultipart("related")
        msg["From"] = mail_sender
        msg["To"] = mail_recipient
        msg["Subject"] = f"📊 Borsa Analiz - {datetime.now().strftime('%d %b %Y')}"
        
        # HTML Body
        msg_alternative = MIMEMultipart("alternative")
        msg.attach(msg_alternative)
        msg_alternative.attach(MIMEText(html_body, "html"))
        
        # Grafikleri Ekle
        if chart_paths:
            print("   📎 Grafikler ekleniyor...")
            for i, chart_path in enumerate(chart_paths, 1):
                if os.path.exists(chart_path):
                    try:
                        with open(chart_path, "rb") as attachment:
                            image = MIMEImage(attachment.read())
                            image.add_header("Content-ID", f"<chart_{i}>")
                            image.add_header("Content-Disposition", "inline", 
                                           filename=os.path.basename(chart_path))
                            msg.attach(image)
                        print(f"      ✅ {os.path.basename(chart_path)}")
                    except Exception as e:
                        print(f"      ⚠️  Grafik eklenemiyor: {e}")
        
        # Email Gönder
        print("   📤 Email gönderiliyor...")
        server.send_message(msg)
        server.quit()
        
        print(f"   ✅ Email başarıyla gönderildi!")
        print(f"      Gönderici: {mail_sender}")
        print(f"      Alıcı: {mail_recipient}")
        
        return True
    
    except smtplib.SMTPAuthenticationError:
        print("❌ Gmail Kimlik Doğrulama Hatası!")
        print("   → Gmail App Password doğru mu?")
        print("   → 2FA aktif mi kontrol et (gereklidir)")
        return False
    
    except smtplib.SMTPException as e:
        print(f"❌ SMTP Hatası: {e}")
        return False
    
    except Exception as e:
        print(f"❌ Email gönderme hatası: {e}")
        return False


if __name__ == "__main__":
    print("✅ mail_sender.py yüklendi başarıyla")
    
    # Test
    test_rec = {
        "recommendations": [
            {
                "ticker": "GARAN.IS",
                "sector": "Finans",
                "score": 72.5,
                "rating": "🟢🟢 ÜBERGEWICHT",
                "price": 45.50,
                "rsi": 62.3,
                "macd_histogram": 0.0234,
                "bollinger_position": "orta",
                "sma_short": 44.20,
                "sma_long": 43.10,
                "momentum_pct": 3.45,
                "trend": "Yükseliş",
                "support": 42.50,
                "resistance": 48.30,
                "reward_pct": 6.15,
                "risk_pct": 4.40,
                "confidence": "Yüksek",
                "signals": ["📈 SMA → Bullish", "📊 RSI 62.3 → Normal", "📈 Momentum +3.45%"]
            }
        ]
    }
    
    html = generate_html_body(test_rec)
    print("✅ HTML başarıyla oluşturuldu")
    print(f"📄 HTML uzunluğu: {len(html)} karakter")
