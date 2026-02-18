# ============================================================
# mail_sender.py — Email Gönderim Sistemi
# ============================================================
# Bu modül:
# 1) Analiz sonuçlarını HTML email'e formatlar
# 2) Her alınan grafik dosyasını mail'e ekler
# 3) Gmail SMTP üzerinden gönderir
# ============================================================

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email import encoders
from datetime import datetime


def generate_html_body(recommendations, chart_paths):
    """HTML formatlı email gövdesi oluştur"""
    date_str = datetime.now().strftime("%d %B %Y, %H:%M")
    recs = recommendations.get("recommendations", [])
    
    html = f"""
    <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{ font-family: Arial, sans-serif; background-color: #f5f5f5; }}
                .container {{ max-width: 600px; margin: 0 auto; background-color: #ffffff; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
                h1 {{ color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px; }}
                .rec-item {{ margin: 15px 0; padding: 10px; background-color: #ecf0f1; border-left: 4px solid #3498db; }}
                .ticker {{ font-weight: bold; color: #2c3e50; font-size: 16px; }}
                .rating {{ display: inline-block; margin: 0 10px; padding: 5px 10px; background-color: #3498db; color: white; border-radius: 4px; }}
                .score {{ color: #27ae60; font-weight: bold; }}
                .chart-section {{ margin-top: 30px; text-align: center; }}
                .chart-img {{ max-width: 100%; height: auto; margin: 20px 0; border-radius: 4px; }}
                .footer {{ margin-top: 30px; font-size: 12px; color: #7f8c8d; border-top: 1px solid #ecf0f1; padding-top: 20px; }}
                .market-mood {{ padding: 15px; background-color: #fff3cd; border-left: 4px solid #ffc107; margin: 15px 0; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>📊 Borsa Analiz Raporu</h1>
                <p><strong>Tarih:</strong> {date_str}</p>
                
                <div class="market-mood">
                    <strong>Pazar Durumu:</strong> {recommendations.get('market_mood', '⚪ Belirsiz')}
                </div>
    """
    
    if recs:
        html += "<h2>🎯 Günün Önerileri</h2>"
        for rec in recs:
            rating_html = f"<span class='rating'>{rec.get('rating', 'N/A')}</span>"
            html += f"""
                <div class="rec-item">
                    <div class="ticker">{rec.get('ticker', 'N/A')}</div>
                    {rating_html}
                    <div class="score">Skor: {rec.get('final_score', rec.get('score', 0)):.1f}/100</div>
                    <p>{rec.get('reasoning', '')}</p>
                </div>
            """
    else:
        html += "<p style='color: #e74c3c;'><strong>⚠️ Bugün alım sinyali bulunamadı.</strong></p>"
    
    if chart_paths:
        html += "<div class='chart-section'><h2>📈 Grafik Analizi</h2>"
        for i, path in enumerate(chart_paths, 1):
            filename = os.path.basename(path)
            html += f"<p><strong>Grafik {i}:</strong> {filename}</p><img src='cid:chart_{i}' class='chart-img' alt='Grafik {i}'>"
        html += "</div>"
    
    html += """
                <div class="footer">
                    <p>⚠️ <strong>Önemli:</strong> Bu analiz yatırım tavsiyesi değildir. Kendi risk değerlendirmenizi yapınız.</p>
                    <p>Oto-Analiz Bot tarafından oluşturulmuştur.</p>
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
