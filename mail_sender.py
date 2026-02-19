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


def _rsi_color(rsi: float) -> str:
    """RSI değerine göre renk döndür"""
    if rsi < 30:
        return "#f85149"
    elif rsi < 45:
        return "#d29922"
    elif rsi < 55:
        return "#8b949e"
    elif rsi < 70:
        return "#56d364"
    else:
        return "#f85149"


def _rsi_label(rsi: float) -> str:
    """RSI değerine göre Türkçe yorum döndür"""
    if rsi < 30:
        return "Aşırı Satım"
    elif rsi < 45:
        return "Düşük"
    elif rsi < 55:
        return "Nötr"
    elif rsi < 70:
        return "Yüksek"
    else:
        return "Aşırı Alım"


def generate_html_body(recommendations, chart_paths=None) -> str:
    """Profesyonel HTML Email Oluştur (Koyu Tema)"""
    
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
                    background: linear-gradient(135deg, #0d1117 0%, #161b22 100%);
                    color: #e6edf3;
                    line-height: 1.6;
                }}
                
                .container {{ 
                    max-width: 1000px; 
                    margin: 0 auto; 
                    background: #1c2128;
                    box-shadow: 0 10px 40px rgba(0,0,0,0.5);
                }}
                
                .header {{ 
                    background: linear-gradient(135deg, #1a1b27 0%, #2d333b 100%);
                    color: #e6edf3;
                    padding: 40px 30px;
                    text-align: center;
                    border-bottom: 1px solid #30363d;
                }}
                
                .header h1 {{ font-size: 32px; margin-bottom: 10px; color: #58a6ff; }}
                .header p {{ font-size: 14px; opacity: 0.9; color: #8b949e; }}
                
                .market-summary {{
                    background: #161b22;
                    border-bottom: 1px solid #30363d;
                    padding: 20px 30px;
                    display: grid;
                    grid-template-columns: repeat(4, 1fr);
                    gap: 15px;
                    text-align: center;
                }}
                
                .summary-item {{ padding: 10px; }}
                
                .summary-label {{
                    font-size: 11px;
                    color: #8b949e;
                    text-transform: uppercase;
                    font-weight: 600;
                    margin-bottom: 6px;
                }}
                
                .summary-value {{
                    font-size: 22px;
                    font-weight: bold;
                    color: #58a6ff;
                }}
                
                .content {{ padding: 30px; }}
                
                .section {{ margin-bottom: 30px; }}
                
                .section-title {{ 
                    font-size: 22px; 
                    font-weight: bold; 
                    color: #e6edf3;
                    margin-bottom: 20px;
                    padding-bottom: 10px;
                    border-bottom: 3px solid #58a6ff;
                }}
                
                .stock-card {{ 
                    background: #21262d;
                    border-left: 5px solid #58a6ff;
                    border-radius: 8px;
                    padding: 25px;
                    margin-bottom: 20px;
                }}
                
                .stock-header {{ 
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    margin-bottom: 20px;
                }}
                
                .stock-rank {{
                    font-size: 13px;
                    font-weight: 600;
                    color: #58a6ff;
                    background: #30363d;
                    padding: 3px 10px;
                    border-radius: 12px;
                    margin-bottom: 5px;
                    display: inline-block;
                }}
                
                .ticker {{ 
                    font-size: 28px;
                    font-weight: 700;
                    color: #e6edf3;
                }}
                
                .sector {{ 
                    font-size: 12px;
                    color: #8b949e;
                    text-transform: uppercase;
                    margin-top: 5px;
                }}
                
                .rating-badge {{ 
                    display: inline-block;
                    padding: 10px 20px;
                    background: #388bfd1a;
                    color: #58a6ff;
                    border: 1px solid #388bfd66;
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
                    background: #30363d;
                    border: 1px solid #444c56;
                    border-radius: 6px;
                    padding: 15px;
                    text-align: center;
                }}
                
                .metric-label {{ 
                    font-size: 11px;
                    color: #8b949e;
                    text-transform: uppercase;
                    margin-bottom: 8px;
                    font-weight: 600;
                }}
                
                .metric-value {{ 
                    font-size: 24px;
                    font-weight: bold;
                    color: #58a6ff;
                }}
                
                .score-bar-bg {{
                    background: #30363d;
                    border-radius: 10px;
                    height: 8px;
                    width: 100%;
                    margin-top: 8px;
                }}
                
                .technical-indicators {{ 
                    background: #30363d;
                    border: 1px solid #444c56;
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
                    background: #21262d;
                    border-radius: 4px;
                    border: 1px solid #30363d;
                }}
                
                .indicator-label {{ 
                    font-size: 12px;
                    color: #8b949e;
                    font-weight: 600;
                    margin-bottom: 5px;
                }}
                
                .indicator-value {{ 
                    font-size: 18px;
                    font-weight: bold;
                    color: #c9d1d9;
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
                
                .risk-box {{ background: linear-gradient(135deg, #6e1a1a 0%, #3d0c0c 100%); border: 1px solid #f8514966; }}
                .reward-box {{ background: linear-gradient(135deg, #1a4a1a 0%, #0d2e0d 100%); border: 1px solid #56d36466; }}
                
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
                    background: #161b22;
                    border-left: 4px solid #58a6ff;
                    padding: 15px;
                    margin-bottom: 20px;
                    border-radius: 4px;
                }}
                
                .signals h4 {{ 
                    color: #58a6ff;
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
                    color: #c9d1d9;
                }}
                
                .fibonacci {{ 
                    background: #30363d;
                    border: 1px solid #444c56;
                    border-radius: 6px;
                    padding: 15px;
                    margin-bottom: 20px;
                }}
                
                .fibonacci h4 {{ 
                    color: #e6edf3;
                    margin-bottom: 10px;
                    font-size: 14px;
                }}
                
                .fib-grid {{ 
                    display: grid;
                    grid-template-columns: repeat(4, 1fr);
                    gap: 10px;
                }}
                
                .fib-item {{ 
                    background: #21262d;
                    padding: 10px;
                    border-radius: 4px;
                    text-align: center;
                    border: 1px solid #30363d;
                }}
                
                .fib-label {{ 
                    font-size: 11px;
                    color: #8b949e;
                    margin-bottom: 5px;
                }}
                
                .fib-value {{ 
                    font-size: 16px;
                    font-weight: bold;
                    color: #58a6ff;
                }}
                
                .disclaimer {{ 
                    background: #2d1b00;
                    border-left: 4px solid #d29922;
                    padding: 20px;
                    margin: 30px 0;
                    border-radius: 4px;
                    font-size: 12px;
                    color: #e3b341;
                }}
                
                .footer {{ 
                    background: #010409;
                    color: #8b949e;
                    padding: 30px;
                    text-align: center;
                    font-size: 12px;
                    border-top: 1px solid #30363d;
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
                    box-shadow: 0 4px 12px rgba(0,0,0,0.4);
                }}
                
                .no-data {{ 
                    background: #3d0c0c;
                    border-left: 4px solid #f85149;
                    padding: 20px;
                    border-radius: 4px;
                    text-align: center;
                    color: #f85149;
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
        """
        
        recs = recommendations.get("recommendations", [])
        total_selected = len(recs)
        avg_score = (sum(r.get('score', 0) for r in recs) / total_selected) if total_selected else 0
        
        if total_selected == 0:
            market_mood = "⚪ Veri Yok"
        elif avg_score >= 70:
            market_mood = "🟢 Pozitif"
        elif avg_score >= 55:
            market_mood = "🟡 Nötr"
        else:
            market_mood = "🔴 Negatif"
        
        html += f"""
                <!-- PİYASA ÖZETİ -->
                <div class="market-summary">
                    <div class="summary-item">
                        <div class="summary-label">Seçilen Hisse</div>
                        <div class="summary-value">{total_selected}</div>
                    </div>
                    <div class="summary-item">
                        <div class="summary-label">Ort. Skor</div>
                        <div class="summary-value">{avg_score:.1f}</div>
                    </div>
                    <div class="summary-item">
                        <div class="summary-label">Piyasa Duygusu</div>
                        <div class="summary-value" style="font-size:16px;">{market_mood}</div>
                    </div>
                    <div class="summary-item">
                        <div class="summary-label">Analiz Saati</div>
                        <div class="summary-value" style="font-size:14px;">{datetime.now().strftime('%H:%M')}</div>
                    </div>
                </div>
                
                <!-- CONTENT -->
                <div class="content">
                    <!-- SKOR & RATING REHBERİ -->
                    <div class="section">
                        <div class="section-title">📖 Skor &amp; Rating Rehberi</div>
                        <table style="width:100%; border-collapse: collapse; background: #21262d; border-radius: 8px; overflow: hidden;">
                            <thead>
                                <tr style="background: #30363d;">
                                    <th style="padding: 12px 15px; text-align: left; color: #8b949e; font-size: 12px; text-transform: uppercase; font-weight: 600;">Skor</th>
                                    <th style="padding: 12px 15px; text-align: left; color: #8b949e; font-size: 12px; text-transform: uppercase; font-weight: 600;">Rating</th>
                                    <th style="padding: 12px 15px; text-align: left; color: #8b949e; font-size: 12px; text-transform: uppercase; font-weight: 600;">Anlamı</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr style="border-top: 1px solid #30363d;">
                                    <td style="padding: 10px 15px; color: #58a6ff; font-weight: bold;">≥ 80</td>
                                    <td style="padding: 10px 15px; color: #e6edf3; font-weight: bold;">🔥 GÜÇLÜ AL</td>
                                    <td style="padding: 10px 15px; color: #8b949e; font-size: 13px;">Teknik göstergeler çok olumlu, güçlü alım fırsatı</td>
                                </tr>
                                <tr style="border-top: 1px solid #30363d; background: #161b22;">
                                    <td style="padding: 10px 15px; color: #56d364; font-weight: bold;">≥ 70</td>
                                    <td style="padding: 10px 15px; color: #e6edf3; font-weight: bold;">🟢 AL</td>
                                    <td style="padding: 10px 15px; color: #8b949e; font-size: 13px;">Göstergeler olumlu, alım yapılabilir</td>
                                </tr>
                                <tr style="border-top: 1px solid #30363d;">
                                    <td style="padding: 10px 15px; color: #d29922; font-weight: bold;">≥ 60</td>
                                    <td style="padding: 10px 15px; color: #e6edf3; font-weight: bold;">🟡 TUT</td>
                                    <td style="padding: 10px 15px; color: #8b949e; font-size: 13px;">Mevcut pozisyonu koru, ne al ne sat</td>
                                </tr>
                                <tr style="border-top: 1px solid #30363d; background: #161b22;">
                                    <td style="padding: 10px 15px; color: #d29922; font-weight: bold;">≥ 40</td>
                                    <td style="padding: 10px 15px; color: #e6edf3; font-weight: bold;">🟠 AZALT</td>
                                    <td style="padding: 10px 15px; color: #8b949e; font-size: 13px;">Göstergeler olumsuz, pozisyonu kademeli azalt</td>
                                </tr>
                                <tr style="border-top: 1px solid #30363d;">
                                    <td style="padding: 10px 15px; color: #f85149; font-weight: bold;">&lt; 40</td>
                                    <td style="padding: 10px 15px; color: #e6edf3; font-weight: bold;">🔴 SAT</td>
                                    <td style="padding: 10px 15px; color: #8b949e; font-size: 13px;">Teknik göstergeler çok olumsuz, sat</td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                    
                    <!-- TEKNİK GÖSTERGE REHBERİ -->
                    <div class="section">
                        <div class="section-title">🔬 Teknik Gösterge Rehberi</div>
                        <table style="width:100%; border-collapse: collapse; background: #21262d; border-radius: 8px; overflow: hidden;">
                            <thead>
                                <tr style="background: #30363d;">
                                    <th style="padding: 12px 15px; text-align: left; color: #8b949e; font-size: 12px; text-transform: uppercase; font-weight: 600;">Gösterge</th>
                                    <th style="padding: 12px 15px; text-align: left; color: #8b949e; font-size: 12px; text-transform: uppercase; font-weight: 600;">Açıklama</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr style="border-top: 1px solid #30363d;">
                                    <td style="padding: 10px 15px; color: #58a6ff; font-weight: bold; white-space: nowrap;">RSI (14)</td>
                                    <td style="padding: 10px 15px; color: #8b949e; font-size: 13px;">30 altı aşırı satım (alım fırsatı), 70 üzeri aşırı alım (satış sinyali)</td>
                                </tr>
                                <tr style="border-top: 1px solid #30363d; background: #161b22;">
                                    <td style="padding: 10px 15px; color: #58a6ff; font-weight: bold; white-space: nowrap;">MACD Histogram</td>
                                    <td style="padding: 10px 15px; color: #8b949e; font-size: 13px;">Pozitif → yükseliş trendi güçleniyor, Negatif → düşüş trendi güçleniyor</td>
                                </tr>
                                <tr style="border-top: 1px solid #30363d;">
                                    <td style="padding: 10px 15px; color: #58a6ff; font-weight: bold; white-space: nowrap;">Signal Line</td>
                                    <td style="padding: 10px 15px; color: #8b949e; font-size: 13px;">MACD çizgisinin ortalaması; MACD signal line'ı yukarı keserse AL, aşağı keserse SAT sinyali</td>
                                </tr>
                                <tr style="border-top: 1px solid #30363d; background: #161b22;">
                                    <td style="padding: 10px 15px; color: #58a6ff; font-weight: bold; white-space: nowrap;">SMA 20 / SMA 50</td>
                                    <td style="padding: 10px 15px; color: #8b949e; font-size: 13px;">Kısa/uzun vadeli ortalama; fiyat üstündeyse yükseliş, altındaysa düşüş</td>
                                </tr>
                                <tr style="border-top: 1px solid #30363d;">
                                    <td style="padding: 10px 15px; color: #58a6ff; font-weight: bold; white-space: nowrap;">Bollinger Bantları</td>
                                    <td style="padding: 10px 15px; color: #8b949e; font-size: 13px;">Alt banda yakınsa alım fırsatı, üst banda yakınsa satış sinyali</td>
                                </tr>
                                <tr style="border-top: 1px solid #30363d; background: #161b22;">
                                    <td style="padding: 10px 15px; color: #58a6ff; font-weight: bold; white-space: nowrap;">Momentum</td>
                                    <td style="padding: 10px 15px; color: #8b949e; font-size: 13px;">Pozitif → yukarı ivme, negatif → aşağı ivme</td>
                                </tr>
                                <tr style="border-top: 1px solid #30363d;">
                                    <td style="padding: 10px 15px; color: #58a6ff; font-weight: bold; white-space: nowrap;">ATR</td>
                                    <td style="padding: 10px 15px; color: #8b949e; font-size: 13px;">Volatilite ölçüsü — yüksek ATR = yüksek risk ve hareket</td>
                                </tr>
                                <tr style="border-top: 1px solid #30363d; background: #161b22;">
                                    <td style="padding: 10px 15px; color: #58a6ff; font-weight: bold; white-space: nowrap;">Fibonacci</td>
                                    <td style="padding: 10px 15px; color: #8b949e; font-size: 13px;">0.618 → güçlü destek, 0.236 → güçlü direnç noktası</td>
                                </tr>
                                <tr style="border-top: 1px solid #30363d;">
                                    <td style="padding: 10px 15px; color: #58a6ff; font-weight: bold; white-space: nowrap;">Risk/Reward</td>
                                    <td style="padding: 10px 15px; color: #8b949e; font-size: 13px;">Kazanç/risk oranı — kazanç yüksek, risk düşükse iyi fırsat</td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                    
                    <!-- ÖNERİLER BÖLÜMÜ -->
                    <div class="section">
                        <div class="section-title">🎯 Önerilen Hisseler</div>
        """
        
        if recs:
            for i, rec in enumerate(recs, 1):
                ticker = rec.get('ticker', 'N/A')
                sector = rec.get('sector', 'Genel').replace('_', ' ').title()
                score = rec.get('score', 0)
                rating = rec.get('rating', '❓')
                price = rec.get('price', 0)
                
                currency = "₺" if ticker.endswith(".IS") else "$"
                
                rsi = rec.get('rsi') or 0
                macd_hist = rec.get('macd_histogram') or 0
                macd_line = rec.get('macd_line')
                signal_line = rec.get('signal_line')
                bollinger = rec.get('bollinger_position') or 'orta'
                bollinger_upper = rec.get('bollinger_upper')
                bollinger_middle = rec.get('bollinger_middle')
                bollinger_lower = rec.get('bollinger_lower')
                sma_short = rec.get('sma_short') or 0
                sma_long = rec.get('sma_long') or 0
                momentum = rec.get('momentum_pct') or 0
                atr = rec.get('atr')
                trend = rec.get('trend') or 'Nötr'
                trend_strength = rec.get('trend_strength')
                support = rec.get('support') or 0
                resistance = rec.get('resistance') or 0
                reward_pct = rec.get('reward_pct', 0)
                risk_pct = rec.get('risk_pct', 0)
                confidence = rec.get('confidence', 'Orta')
                signals = rec.get('signals', [])
                fibonacci = rec.get('fibonacci', {})
                
                rsi_color = _rsi_color(rsi)
                rsi_label = _rsi_label(rsi)
                score_pct = min(100, max(0, score))
                
                fib_236 = fibonacci.get('fib_0.236') or 0
                fib_382 = fibonacci.get('fib_0.382') or 0
                fib_618 = fibonacci.get('fib_0.618') or 0
                fib_236_str = f"{currency}{fib_236:.2f}" if fib_236 else "Veri Yok"
                fib_382_str = f"{currency}{fib_382:.2f}" if fib_382 else "Veri Yok"
                fib_618_str = f"{currency}{fib_618:.2f}" if fib_618 else "Veri Yok"
                
                html += f"""
                    <div class="stock-card">
                        <!-- BAŞLIK -->
                        <div class="stock-header">
                            <div>
                                <div class="stock-rank">#{i}</div>
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
                                <div class="score-bar-bg">
                                    <div style="background: linear-gradient(90deg, #f85149, #d29922, #7ee787); width: {score_pct:.0f}%; height: 8px; border-radius: 10px;"></div>
                                </div>
                            </div>
                            <div class="metric-box">
                                <div class="metric-label">Fiyat</div>
                                <div class="metric-value">{currency}{price:.2f}</div>
                            </div>
                            <div class="metric-box">
                                <div class="metric-label">Güven</div>
                                <div class="metric-value">{confidence}</div>
                            </div>
                        </div>
                        
                        <!-- TEKNİK GÖSTERGELER -->
                        <div class="technical-indicators">
                            <h4 style="margin-bottom: 15px; color: #e6edf3;">📊 Teknik Göstergeler</h4>
                            <div class="indicator-row">
                                <div class="indicator-item">
                                    <div class="indicator-label">RSI (14)</div>
                                    <div class="indicator-value" style="color: {rsi_color};">{rsi:.1f} <span style="font-size:12px; font-weight:normal; color:{rsi_color};">{rsi_label}</span></div>
                                </div>
                                <div class="indicator-item">
                                    <div class="indicator-label">MACD Histogram</div>
                                    <div class="indicator-value" style="color: {'#56d364' if macd_hist > 0 else '#f85149'};">{macd_hist:.6f}</div>
                                </div>
                            </div>
                            <div class="indicator-row">
                                <div class="indicator-item">
                                    <div class="indicator-label">MACD Line</div>
                                    <div class="indicator-value">{f"{macd_line:.6f}" if macd_line is not None else "N/A"}</div>
                                </div>
                                <div class="indicator-item">
                                    <div class="indicator-label">Signal Line</div>
                                    <div class="indicator-value">{f"{signal_line:.6f}" if signal_line is not None else "N/A"}</div>
                                </div>
                            </div>
                            <div class="indicator-row">
                                <div class="indicator-item">
                                    <div class="indicator-label">SMA 20</div>
                                    <div class="indicator-value">{currency}{sma_short:.2f}</div>
                                </div>
                                <div class="indicator-item">
                                    <div class="indicator-label">SMA 50</div>
                                    <div class="indicator-value">{currency}{sma_long:.2f}</div>
                                </div>
                            </div>
                            <div class="indicator-row">
                                <div class="indicator-item">
                                    <div class="indicator-label">Momentum</div>
                                    <div class="indicator-value" style="color: {'#56d364' if momentum >= 0 else '#f85149'};">{momentum:+.2f}%</div>
                                </div>
                                <div class="indicator-item">
                                    <div class="indicator-label">Bollinger</div>
                                    <div class="indicator-value">{bollinger.title()}</div>
                                </div>
                            </div>
                            <div class="indicator-row">
                                <div class="indicator-item">
                                    <div class="indicator-label">Bollinger Üst</div>
                                    <div class="indicator-value">{f"{currency}{bollinger_upper:.2f}" if bollinger_upper else "N/A"}</div>
                                </div>
                                <div class="indicator-item">
                                    <div class="indicator-label">Bollinger Orta</div>
                                    <div class="indicator-value">{f"{currency}{bollinger_middle:.2f}" if bollinger_middle else "N/A"}</div>
                                </div>
                            </div>
                            <div class="indicator-row">
                                <div class="indicator-item">
                                    <div class="indicator-label">Bollinger Alt</div>
                                    <div class="indicator-value">{f"{currency}{bollinger_lower:.2f}" if bollinger_lower else "N/A"}</div>
                                </div>
                                <div class="indicator-item">
                                    <div class="indicator-label">ATR (14)</div>
                                    <div class="indicator-value">{f"{currency}{atr:.2f}" if atr else "N/A"}</div>
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
                            <div style="background: #30363d; padding: 15px; border-radius: 6px; border: 1px solid #444c56;">
                                <h4 style="color: #8b949e; font-size: 12px; text-transform: uppercase; margin-bottom: 10px;">📈 Trend</h4>
                                <div style="font-size: 16px; font-weight: bold; color: #58a6ff;">{trend}</div>
                                {f'<div style="font-size: 12px; color: #8b949e; margin-top: 5px;">Güç: {trend_strength}</div>' if trend_strength else ''}
                            </div>
                            <div style="background: #30363d; padding: 15px; border-radius: 6px; border: 1px solid #444c56;">
                                <h4 style="color: #8b949e; font-size: 12px; text-transform: uppercase; margin-bottom: 10px;">🎯 Destek/Direnç</h4>
                                <div style="font-size: 12px; color: #c9d1d9;">
                                    Destek: <strong style="color:#56d364;">{currency}{support:.2f}</strong><br>
                                    Direnç: <strong style="color:#f85149;">{currency}{resistance:.2f}</strong>
                                </div>
                            </div>
                        </div>
                        
                        <!-- FIBONACCI SEVİYELERİ -->
                        <div class="fibonacci">
                            <h4>📊 Fibonacci Seviyeleri</h4>
                            <div class="fib-grid">
                                <div class="fib-item">
                                    <div class="fib-label">Mevcut</div>
                                    <div class="fib-value">{currency}{price:.2f}</div>
                                </div>
                                <div class="fib-item">
                                    <div class="fib-label">Fib 0.236</div>
                                    <div class="fib-value">{fib_236_str}</div>
                                </div>
                                <div class="fib-item">
                                    <div class="fib-label">Fib 0.382</div>
                                    <div class="fib-value">{fib_382_str}</div>
                                </div>
                                <div class="fib-item">
                                    <div class="fib-label">Fib 0.618</div>
                                    <div class="fib-value">{fib_618_str}</div>
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
        
        html += f"""
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
                    <p style="font-size: 16px; font-weight: 600; margin-bottom: 10px; color: #e6edf3;">🤖 BorsaBot v7.0</p>
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


def send_email(html_body: str, chart_paths: list = None, rec_count: int = 0) -> bool:
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
        msg["Subject"] = f"📊 Borsa Analiz - {datetime.now().strftime('%d %b %Y')} | {rec_count} Öneri"
        
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
                "rating": "🟢 AL",
                "price": 45.50,
                "rsi": 62.3,
                "macd_histogram": 0.0234,
                "macd_line": 0.0189,
                "signal_line": -0.0045,
                "bollinger_position": "orta",
                "bollinger_upper": 47.80,
                "bollinger_middle": 44.50,
                "bollinger_lower": 41.20,
                "sma_short": 44.20,
                "sma_long": 43.10,
                "momentum_pct": 3.45,
                "atr": 1.25,
                "trend": "Yükseliş",
                "trend_strength": "Güçlü",
                "support": 42.50,
                "resistance": 48.30,
                "reward_pct": 6.15,
                "risk_pct": 4.40,
                "confidence": "Yüksek",
                "signals": ["📈 SMA → Bullish", "📊 RSI 62.3 → Normal", "📈 Momentum +3.45%"],
                "fibonacci": {
                    "current": 45.50,
                    "fib_0.236": 47.10,
                    "fib_0.382": 46.20,
                    "fib_0.618": 43.80
                }
            }
        ]
    }
    
    html = generate_html_body(test_rec)
    print("✅ HTML başarıyla oluşturuldu")
    print(f"📄 HTML uzunluğu: {len(html)} karakter")
