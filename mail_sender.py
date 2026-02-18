# ============================================================
# mail_sender.py — Email Gönderim Sistemi
# ============================================================
# Bu modül:
# 1) Analiz sonuçlarını HTML email'e formatlar
# 2) Her alınan grafik dosyasını mail'e ekler
# 3) Gmail SMTP üzerinden gönderir
# ============================================================

import os
import base64
from datetime import datetime

try:
    import sendgrid
    from sendgrid.helpers.mail import Mail, Email, To, Content, Attachment, FileContent, FileName, FileType, Disposition
except:
    pass


def generate_html_body(recommendations, chart_paths):
    date_str = datetime.now().strftime("%d %B %Y, %H:%M")
    recs = recommendations.get("recommendations", [])
    
    html = "<h1>Borsa Analiz - " + date_str + "</h1>"
    
    if recs:
        for rec in recs:
            html += "<p><b>" + rec['ticker'] + "</b> - " + rec['rating'] + " - Skor: " + str(rec.get('score', 0)) + "</p>"
    else:
        html += "<p>Bugun oneri yok.</p>"
    
    html += "<p><small>Bu analiz yatirim tavsiyesi degildir.</small></p>"
    
    return html


def send_email(html_body, chart_paths=None, subject=None):
    if subject is None:
        subject = "Borsa Analiz - " + datetime.now().strftime("%d %b")
    
    api_key = os.environ.get("SENDGRID_API_KEY")
    if not api_key:
        print("SENDGRID_API_KEY yok")
        return False
    
    try:
        sg = sendgrid.SendGridAPIClient(api_key=api_key)
        
        mail = Mail(
            from_email=Email(os.environ.get("MAIL_SENDER")),
            to_emails=To(os.environ.get("MAIL_RECIPIENT")),
            subject=subject,
            html_content=Content("text/html", html_body)
        )
        
        if chart_paths:
            for path in chart_paths:
                if os.path.exists(path):
                    with open(path, 'rb') as f:
                        data = base64.b64encode(f.read()).decode()
                    
                    att = Attachment()
                    att.file_content = FileContent(data)
                    att.file_type = FileType('image/png')
                    att.file_name = FileName(os.path.basename(path))
                    att.disposition = Disposition('attachment')
                    mail.add_attachment(att)
        
        response = sg.send(mail)
        
        if response.status_code in [200, 201, 202]:
            print("Email gonderildi!")
            return True
        else:
            print("Hata: " + str(response.status_code))
            return False
    except Exception as e:
        print("Email hatasi: " + str(e))
        return False
