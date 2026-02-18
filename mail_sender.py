# ============================================================
# mail_sender.py — Email Gönderim Sistemi (v5 - KOMPLE FINAL)
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
    """
    Market mood'u detaylı analiz et.
    Hangi sektörler yukarı/aşağı gidiyor göster.
    """
    
    # Sektörleri skora göre sırala
    sorted_sectors = sorted(sector_scores.items(), key=lambda x: x[1], reverse=True)
    
    # Emoji'ler
    emoji_map = {
        "finans": "🏦", "teknoloji": "💻", "enerji": "⚡", "sağlık": "💊",
        "perakende": "🛒", "gıda": "🍔", "telekom": "📱", "otomotiv": "🚗",
        "inşaat_gayrimenkul": "🏗️", "sigortalar": "🛡️", "turizm": "✈️",
        "savunma": "🎖️", "tekstil": "👕", "kimya": "🧪", "orman": "🌲", "medya": "📺",
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
        description = f"Piyasalar panik modunda. Keskin satışlar yaşanıyor. Ekonomik endişeler yüksek. Acil koruma gerekli."
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
    """Detaylı, profesyonel HTML email oluştur (KOMPLE VERSİYON)"""
    date_str = datetime.now().strftime("%d %B %Y, %H:%M")
    recs = recommendations.get("recommendations", [])
    sector_scores = recommendations.get("sector_scores", {})
    global_analysis = recommendations.get("global_analysis", {})
    advanced_analysis = recommendations.get("advanced_analysis", {})
    trend_opportunities = recommendations.get("trend_opportunities", [])
    sector_recommendations = recommendations.get("sector_recommendations", {})
    geo_news = recommendations.get("geo_news", [])
    supply_chain = recommendations.get("supply_chain", {})
    vix_data = advanced_analysis.get("vix", {})
    correlations = recommendations.get("correlations", {})
    
    # Detaylı market mood analiz yap
    mood_analysis = generate_detailed_market_mood("", sector_scores
