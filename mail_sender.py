# ============================================================
# mail_sender.py — Email Gönderim Sistemi (v7 - KOMPLE FINAL HATASIZ)
# ============================================================

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from datetime import datetime
import config


def generate_html_body(recommendations, chart_paths=None):
    """HTML email body oluştur"""
    
    date_str = datetime.now().strftime("%d %B %Y, %H:%M")
    
    html = f"""
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {{ font-family: Arial, sans-serif; background: #f5f5f5; color: #333; }}
            .wrapper {{ max-width: 1200px; margin: 0 auto; background: white; }}
            .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                      padding: 40px 30px; color: white; text-align: center; }}
            .content {{ padding: 40px 30px; }}
            .section-title {{ font-size: 24px; font-weight: bold; color: #2c3e50; 
                             margin: 30px 0 20px 0; padding-bottom: 10px; 
                             border-bottom: 3px solid #667eea; }}
            .stock-card {{ background: #f8f9fa; border-left: 5px solid #667eea; 
                          border-radius: 8px; padding: 25px; margin-bottom: 25px; }}
            .rating-badge {{ display: inline-block; padding: 10px 20px; 
                            background: #27ae60; color: white; border-radius: 25px; 
                            font-weight: bold; font-size: 14px; }}
            .footer {{ background: #2c3e50; color: white; padding: 30px; 
                      text-align: center; font-size: 12px; }}
            .disclaimer {{ background: #fffbf5; border-left: 4px solid #f39c12; 
                          padding: 20px; margin: 30px 0; border-radius: 4px; 
                          font-size: 12px; color: #d68910; }}
            .metric-box {{ background: white; border: 2px solid #ecf0f1; 
                          border-radius: 6px; padding: 15px; text-align: center; }}
            .metric-label {{ font-size: 11px; color: #95a5a6; text-transform: uppercase; 
                            margin-bottom: 8px; font-weight: 600; }}
            .metric-value {{ font-size: 24px; font-weight: bold; color: #667eea; }}
            table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
            th {{ background: #667eea; color: white; padding: 12px; text-align: left; }}
            td {{ padding: 12px; border-bottom: 1px solid #ecf0f1; }}
            tr:hover {{ background: #f9f9f9; }}
        </style>
    </head>
    <body>
        <div class="wrapper">
            <div class="header">
                <h1>📊 Borsa Analiz Raporu</h1>
                <div class="date">{date_str} | Günlük Analiz</div>
            </div>
            
            <div class="content">
                <div class="section-title">🎯 Önerilen Hisseler</div>
    """
    
    # Önerilen hisseler
    recs = recommendations.get("recommendations", [])
    
    if recs:
        for i, rec in enumerate(recs, 1):
            html += f"""
                <div class="stock-card">
                    <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 20px;">
                        <div>
                            <h2 style="font-size: 28px; font-weight: 700; color: #2c3e50; margin-bottom: 5px;">
                                {rec.get('ticker', 'N/A')}
                            </h2>
                            <div style="font-size: 12px; color: #7f8c8d; text-transform: uppercase; margin-bottom: 10px;">
                                {rec.get('sector', 'genel').replace('_', ' ').title()}
                            </div>
                        </div>
                        <span class="rating-badge">{rec.get('rating', '?')}</span>
                    </div>
                    
                    <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px; margin: 20px 0;">
                        <div class="metric-box">
                            <div class="metric-label">Skor</div>
                            <div class="metric-value">{rec.get('score', 0):.1f}</div>
                        </div>
                        <div class="metric-box">
                            <div class="metric-label">Fiyat</div>
                            <div class="metric-value">${rec.get('price', 0):.2f}</div>
                        </div>
                        <div class="metric-box">
                            <div class="metric-label">Güven</div>
                            <div class="metric-value">{rec.get('confidence', '?')}</div>
                        </div>
                    </div>
                    
                    <div style="background: white; border: 1px solid #ecf0f1; border-radius: 6px; padding: 15px; margin: 15px 0;">
                        <h4 style="color: #2c3e50; margin-bottom: 10px;">📊 Teknik Göstergeler</h4>
                        <table>
                            <tr>
                                <td><strong>RSI:</strong></td>
                                <td>{rec.get('rsi', 'N/A')}</td>
                                <td><strong>MACD:</strong></td>
                                <td>{rec.get('macd_histogram', 'N/A')}</td>
                            </tr>
                            <tr>
                                <td><strong>SMA 20:</strong></td>
                                <td>{rec.get('sma_short', 'N/A')}</td>
                                <td><strong>SMA 50:</strong></td>
                                <td>{rec.get('sma_long', 'N/A')}</td>
                            </tr>
                            <tr>
                                <td><strong>Momentum:</strong></td>
                                <td>{rec.get('momentum_pct', 0):+.2f}%</td>
                                <td><strong>Bollinger:</strong></td>
                                <td>{rec.get('bollinger_position', 'N/A')}</td>
                            </tr>
                        </table>
                    </div>
                    
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin: 15px 0;">
                        <div style="background: rgba(231, 76, 60, 0.08); border-left: 4px solid #e74c3c; padding: 15px; border-radius: 4px;">
                            <h4 style="color: #e74c3c; font-size: 12px; text-transform: uppercase; margin-bottom: 8px;">Risk Seviyesi</h4>
                            <div style="font-size: 20px; color: #e74c3c; font-weight: 700;">{rec.get('risk_pct', 0):.1f}%</div>
                        </div>
                        <div style="background: rgba(39, 174, 96, 0.08); border-left: 4px solid #27ae60; padding: 15px; border-radius: 4px;">
                            <h4 style="color: #27ae60; font-size: 12px; text-transform: uppercase; margin-bottom: 8px;">Potansiyel Kazanç</h4>
                            <div style="font-size: 20px; color: #27ae60; font-weight: 700;">{rec.get('reward_pct', 0):+.1f}%</div>
                        </div>
                    </div>
                    
                    <div style="background: white; border: 1px solid #ecf0f1; border-radius: 6px; padding: 15px; margin: 15px 0;">
                        <h4 style="color: #2c3e50; margin-bottom: 10px;">🎯 Fibonacci Seviyeleri</h4>
                        <table>
                            <tr>
                                <td><strong>Destek:</strong></td>
                                <td>${rec.get('support', 0):.2f}</td>
                                <td><strong>Direnç:</strong></td>
                                <td>${rec.get('resistance', 0):.2f}</td>
                            </tr>
                        </table>
                    </div>
                    
                    <div style="background: #f0f7ff; border-left: 4px solid #3498db; padding: 15px; margin: 15px 0; border-radius: 4px;">
                        <h4 style="color: #3498db; margin-bottom: 10px;">💡 Sinyaller</h4>
                        <ul style="list-style: none; padding: 0;">
    """
            
            for signal in rec.get('signals', [])[:5]:
                html += f"<li style=\"margin: 5px 0; font-size: 13px;\">{signal}</li>"
            
            html += """
                        </ul>
                    </div>
                </div>
            """
    else:
        html += """
                <div style="background: #fef5f5; border-left: 4px solid #e74c3c; padding: 20px; border-radius: 4px; text-align: center; color: #e74c3c; font-weight: 600;">
                    ❌ Bugün için alım sinyali bulunamadı
                </div>
        """
    
    html += """
                <div class="disclaimer">
                    <strong>⚠️ Önemli Uyarı:</strong> Bu analiz tamamen otomatik olarak üretilmiştir ve 
                    <strong>yatırım tavsiyesi DEĞİLDİR</strong>. Tüm yatırım kararlarınızı kendi araştırmanız, 
                    risk analizi ve profesyonel danışmanlığa dayandırınız.
                </div>
                
                <div class="section-title">ℹ️ Sistem Detayları</div>
                <div style="background: #f8f9fa; padding: 20px; border-radius: 6px; font-size: 13px; line-height: 1.8; color: #2c3e50;">
                    <strong>Kullanılan Göstergeler:</strong> RSI, MACD, Bollinger Bands, SMA, Fibonacci, Momentum<br>
                    <strong>Analiz Türü:</strong> Günlük (1D) | <strong>Veri Kaynağı:</strong> Yahoo Finance<br>
                    <strong>Hisse Sayısı:</strong> 92 (BIST 47 + Global 45)<br>
                    <strong>Son Güncelleme:</strong> {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}
                </div>
            </div>
            
            <div class="footer">
                <div style="font-size: 14px; font-weight: 600; margin-bottom: 10px;">🤖 BorsaBot v3.0</div>
                <p>Akıllı Küresel Borsa Analiz Sistemi</p>
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
    
    mail_sender = config.MAIL_SENDER
    mail_password = config.MAIL_PASSWORD
    mail_recipient = config.MAIL_RECIPIENT
    
    if not mail_sender or not mail_password or not mail_recipient:
        print("❌ Email ayarları eksik")
        print("   Şu config değişkenleri gerekli:")
        print("   - MAIL_SENDER")
        print("   - MAIL_PASSWORD")
        print("   - MAIL_RECIPIENT")
        return False
    
    try:
        server = smtplib.SMTP(config.SMTP_SERVER, config.SMTP_PORT)
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
        print("   → 2FA aktif mı kontrol et (gerekli)")
        return False
    
    except smtplib.SMTPException as e:
        print(f"❌ SMTP hatası: {e}")
        return False
    
    except Exception as e:
        print(f"❌ Email gönderme hatası: {e}")
        return False


if __name__ == "__main__":
    print("✅ mail_sender.py yüklendi başarıyla")
