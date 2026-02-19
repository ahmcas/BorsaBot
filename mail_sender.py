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


def generate_html_body(
    recommendations: dict,
    commodity_data: dict = None,
    macro_data: dict = None,
    sector_scores: dict = None,
    holiday_alerts: list = None,
    chart_paths: list = None,
) -> str:
    """Profesyonel HTML Email Oluştur (Koyu Tema) — Swing Trade Dashboard"""
    
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
                    max-width: 750px; 
                    margin: 0 auto; 
                    background: #1c2128;
                    box-shadow: 0 10px 40px rgba(0,0,0,0.5);
                }}
                
                .header {{ 
                    background: linear-gradient(135deg, #1a1b27 0%, #2d333b 100%);
                    color: #e6edf3;
                    padding: 25px 20px;
                    text-align: center;
                    border-bottom: 1px solid #30363d;
                }}
                
                .header h1 {{ font-size: 22px; margin-bottom: 10px; color: #58a6ff; }}
                .header p {{ font-size: 14px; opacity: 0.9; color: #8b949e; }}
                
                .market-summary {{
                    background: #161b22;
                    border-bottom: 1px solid #30363d;
                    padding: 20px 30px;
                    display: grid;
                    grid-template-columns: repeat(4, 1fr);
                    gap: 10px;
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
                    font-size: 16px;
                    font-weight: bold;
                    color: #58a6ff;
                }}
                
                .content {{ padding: 18px; }}
                
                .section {{ margin-bottom: 18px; }}
                
                .section-title {{ 
                    font-size: 16px; 
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
                    padding: 15px;
                    margin-bottom: 20px;
                }}
                
                .stock-header {{ 
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    margin-bottom: 12px;
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
                    font-size: 20px;
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
                    padding: 6px 12px;
                    background: #388bfd1a;
                    color: #58a6ff;
                    border: 1px solid #388bfd66;
                    border-radius: 25px;
                    font-weight: bold;
                    font-size: 12px;
                }}
                
                .metrics {{ 
                    display: grid;
                    grid-template-columns: repeat(3, 1fr);
                    gap: 8px;
                    margin-bottom: 12px;
                }}
                
                .metric-box {{ 
                    background: #30363d;
                    border: 1px solid #444c56;
                    border-radius: 6px;
                    padding: 10px;
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
                    font-size: 16px;
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
                    gap: 8px;
                    margin-bottom: 8px;
                }}
                
                .indicator-item {{ 
                    padding: 6px;
                    background: #21262d;
                    border-radius: 4px;
                    border: 1px solid #30363d;
                }}
                
                .indicator-label {{ 
                    font-size: 10px;
                    color: #8b949e;
                    font-weight: 600;
                    margin-bottom: 5px;
                }}
                
                .indicator-value {{ 
                    font-size: 14px;
                    font-weight: bold;
                    color: #c9d1d9;
                }}
                
                .rr-section {{ 
                    display: grid;
                    grid-template-columns: 1fr 1fr;
                    gap: 10px;
                    margin-bottom: 12px;
                }}
                
                .rr-box {{ 
                    border-radius: 6px;
                    padding: 12px;
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
                    font-size: 18px;
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
                    gap: 6px;
                }}
                
                .fib-item {{ 
                    background: #21262d;
                    padding: 6px;
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
                    font-size: 13px;
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
                
                details[open] > summary span:first-child {{ transform: rotate(90deg); }}
                details summary::-webkit-details-marker {{ display: none; }}
            </style>
        </head>
        <body>
            <div class="container">
                <!-- HEADER -->
                <div class="header">
                    <h1>📊 Borsa Analiz Raporu</h1>
                    <p>{date_str} | Aylık Swing Trade Raporu</p>
                </div>
        """
        
        recs = recommendations.get("recommendations", [])
        total_selected = len(recs)
        market_summary = recommendations.get("market_summary", {})
        avg_score = market_summary.get("avg_score") or (sum(r.get('score', 0) for r in recs) / total_selected if total_selected else 0)
        total_analyzed = market_summary.get("total_analyzed", total_selected)
        bullish_count = market_summary.get("bullish_count", 0)
        bearish_count = market_summary.get("bearish_count", 0)
        neutral_count = market_summary.get("neutral_count", 0)
        
        if total_selected == 0:
            market_mood = "⚪ Veri Yok"
        elif avg_score >= 70:
            market_mood = "🟢 Pozitif"
        elif avg_score >= 55:
            market_mood = "🟡 Nötr"
        else:
            market_mood = "🔴 Negatif"
        
        html += f"""
                <!-- PİYASA GENEL DURUM DASHBOARD -->
                <div class="market-summary">
                    <div class="summary-item">
                        <div class="summary-label">Önerilen Hisse</div>
                        <div class="summary-value">{total_selected}</div>
                    </div>
                    <div class="summary-item">
                        <div class="summary-label">Analiz Edilen</div>
                        <div class="summary-value">{total_analyzed}</div>
                    </div>
                    <div class="summary-item">
                        <div class="summary-label">Ort. Skor</div>
                        <div class="summary-value">{avg_score:.1f}</div>
                    </div>
                    <div class="summary-item">
                        <div class="summary-label">Piyasa Duygusu</div>
                        <div class="summary-value" style="font-size:16px;">{market_mood}</div>
                    </div>
                </div>
                <div class="market-summary" style="grid-template-columns: repeat(3,1fr);">
                    <div class="summary-item">
                        <div class="summary-label">🟢 Yükseliş</div>
                        <div class="summary-value" style="color:#56d364;">{bullish_count}</div>
                    </div>
                    <div class="summary-item">
                        <div class="summary-label">🔴 Düşüş</div>
                        <div class="summary-value" style="color:#f85149;">{bearish_count}</div>
                    </div>
                    <div class="summary-item">
                        <div class="summary-label">⚪ Nötr</div>
                        <div class="summary-value" style="color:#8b949e;">{neutral_count}</div>
                    </div>
                </div>
                
                <!-- CONTENT -->
                <div class="content">
        """
        
        # ══════════════════════════════════════════════
        # ABD MAKRO RİSK BÖLÜMÜ
        # ══════════════════════════════════════════════
        if macro_data:
            debt_info = macro_data.get("us_debt", {})
            dxy_info = macro_data.get("dxy", {})
            geo_risk = macro_data.get("geopolitical_risk", {})
            
            debt_trillion = debt_info.get("debt_trillion", 0)
            gdp_ratio = debt_info.get("gdp_ratio_pct", 0)
            debt_risk = debt_info.get("risk_level", "N/A")
            debt_comment = debt_info.get("comment", "")
            
            dxy_current = dxy_info.get("current", "N/A") if not dxy_info.get("skip") else "N/A"
            dxy_change = dxy_info.get("monthly_change_pct", 0) if not dxy_info.get("skip") else 0
            dxy_trend = dxy_info.get("trend", "N/A") if not dxy_info.get("skip") else "N/A"
            dxy_interp = dxy_info.get("interpretation", "") if not dxy_info.get("skip") else ""
            
            risk_color = {"Düşük": "#56d364", "Orta": "#d29922", "Yüksek": "#f85149", "Kritik": "#ff0000"}.get(debt_risk, "#8b949e")
            
            html += f"""
                    <!-- 🇺🇸 ABD MAKRO RİSK -->
                    <div class="section">
                        <div class="section-title">🇺🇸 ABD Makro Risk</div>
                        <div style="display:grid; grid-template-columns:1fr 1fr; gap:15px; margin-bottom:15px;">
                            <div style="background:#21262d; border-radius:8px; padding:12px; border:1px solid #30363d;">
                                <div style="font-size:12px; color:#8b949e; text-transform:uppercase; margin-bottom:8px;">ABD Ulusal Borcu</div>
                                <div style="font-size:18px; font-weight:bold; color:#f85149;">${debt_trillion}T</div>
                                <div style="font-size:13px; color:#8b949e; margin-top:5px;">GDP'nin %{gdp_ratio}'ı</div>
                                <div style="margin-top:8px; padding:4px 10px; background:{risk_color}22; color:{risk_color}; border-radius:12px; display:inline-block; font-size:12px; font-weight:bold;">Risk: {debt_risk}</div>
                                <div style="font-size:12px; color:#8b949e; margin-top:8px;">{debt_comment}</div>
                            </div>
                            <div style="background:#21262d; border-radius:8px; padding:12px; border:1px solid #30363d;">
                                <div style="font-size:12px; color:#8b949e; text-transform:uppercase; margin-bottom:8px;">DXY Dolar Endeksi</div>
                                <div style="font-size:18px; font-weight:bold; color:#58a6ff;">{dxy_current}</div>
                                <div style="font-size:13px; color:{'#56d364' if dxy_change >= 0 else '#f85149'}; margin-top:5px;">Aylık: {dxy_change:+.2f}%</div>
                                <div style="font-size:13px; color:#8b949e; margin-top:5px;">Trend: {dxy_trend}</div>
                                <div style="font-size:12px; color:#8b949e; margin-top:8px;">{dxy_interp}</div>
                            </div>
                        </div>
                    </div>
            """
            
            # ══════════════════════════════════════════════
            # JEOPOLİTİK RİSK BAROMETRESI
            # ══════════════════════════════════════════════
            if geo_risk:
                geo_level = geo_risk.get("risk_level", "Bilinmiyor")
                geo_risks = geo_risk.get("risks", [])
                geo_sectors = geo_risk.get("affected_sectors", [])
                geo_color = {"Düşük": "#56d364", "Orta": "#d29922", "Yüksek": "#f85149", "Kritik": "#ff0000", "Bilinmiyor": "#8b949e"}.get(geo_level, "#8b949e")
                
                geo_risks_html = ", ".join(geo_risks[:8]) if geo_risks else "Tespit edilmedi"
                geo_sectors_html = ", ".join(geo_sectors) if geo_sectors else "—"
                
                html += f"""
                    <!-- 🌐 JEOPOLİTİK RİSK -->
                    <div class="section">
                        <div class="section-title">🌐 Jeopolitik Risk Barometresi</div>
                        <div style="background:#21262d; border-radius:8px; padding:12px; border:1px solid #30363d;">
                            <div style="display:flex; align-items:center; gap:10px; margin-bottom:15px;">
                                <div style="font-size:24px; font-weight:bold; color:{geo_color};">{geo_level}</div>
                            </div>
                            <div style="font-size:13px; color:#c9d1d9; margin-bottom:8px;"><strong style="color:#8b949e;">Tespit Edilen Riskler:</strong> {geo_risks_html}</div>
                            <div style="font-size:13px; color:#c9d1d9;"><strong style="color:#8b949e;">Etkilenen Sektörler:</strong> {geo_sectors_html}</div>
                        </div>
                    </div>
                """
            
            # ══════════════════════════════════════════════
            # KÜRESEL FIRSAT RADARI (Arz-Talep)
            # ══════════════════════════════════════════════
            supply_demand = macro_data.get("supply_demand_trends", [])
            if supply_demand:
                html += """
                    <!-- 🌍 KÜRESEL FIRSAT RADARI -->
                    <div class="section">
                        <div class="section-title">🌍 Küresel Fırsat Radarı</div>
                        <div style="background:#21262d; border-radius:8px; padding:12px; border:1px solid #30363d;">
                """
                for item in supply_demand[:6]:
                    kw = item.get("keyword", "")
                    impact = item.get("impact", "mixed")
                    sectors = ", ".join(item.get("sectors", []))
                    impact_color = "#56d364" if impact == "bullish" else "#f85149" if impact == "bearish" else "#d29922"
                    html += f"""
                            <div style="display:flex; justify-content:space-between; padding:10px 0; border-bottom:1px solid #30363d; font-size:13px;">
                                <div style="color:#e6edf3; font-weight:600;">{kw}</div>
                                <div>
                                    <span style="color:{impact_color}; font-weight:bold;">{impact.upper()}</span>
                                    <span style="color:#8b949e; margin-left:10px;">→ {sectors}</span>
                                </div>
                            </div>
                    """
                html += """
                        </div>
                    </div>
                """
        
        # ══════════════════════════════════════════════
        # EMTİA PİYASASI
        # ══════════════════════════════════════════════
        if commodity_data:
            commodities_list = [v for v in commodity_data.values() if not v.get("skip")]
            if commodities_list:
                html += """
                    <!-- ⛏️ EMTİA PİYASASI -->
                    <div class="section">
                        <div class="section-title">⛏️ Emtia Piyasası</div>
                        <div style="display:grid; grid-template-columns:repeat(4,1fr); gap:10px;">
                """
                for c in commodities_list:
                    c_name = c.get("name", c.get("ticker", ""))
                    c_price = c.get("current_price", 0)
                    c_change = c.get("daily_change_pct", 0)
                    c_rsi = c.get("rsi", 50)
                    c_trend = c.get("trend", "Nötr")
                    is_record = c.get("record_info", {}).get("is_record", False)
                    c_color = "#56d364" if c_change >= 0 else "#f85149"
                    record_badge = '<div style="color:#ffd700; font-size:11px; font-weight:bold;">🏆 52H REKOR</div>' if is_record else ""
                    html += f"""
                            <div style="background:#21262d; border-radius:8px; padding:10px; border:1px solid #30363d; text-align:center;">
                                <div style="font-size:11px; color:#8b949e; text-transform:uppercase; margin-bottom:5px;">{c_name}</div>
                                <div style="font-size:13px; font-weight:bold; color:#e6edf3;">${c_price:.2f}</div>
                                <div style="font-size:13px; color:{c_color};">{c_change:+.2f}%</div>
                                <div style="font-size:11px; color:#8b949e; margin-top:4px;">RSI: {c_rsi:.0f} | {c_trend}</div>
                                {record_badge}
                            </div>
                    """
                html += """
                        </div>
                    </div>
                """
                
                # Rekor emtialar için özel kutu
                record_commodities = [c for c in commodities_list if c.get("record_info", {}).get("is_record")]
                if record_commodities:
                    html += """
                    <!-- 🏆 EMTİA REKOR TAKİBİ -->
                    <div class="section">
                        <div class="section-title">🏆 Emtia Rekor Takibi</div>
                    """
                    for c in record_commodities:
                        ctx = c.get("context", {})
                        rec_meaning = ctx.get("record_meaning", "")
                        hist_impact = ctx.get("historical_impact", "")
                        affected = ", ".join(ctx.get("affected_sectors", []))
                        dist = c.get("record_info", {}).get("distance_pct", 0)
                        html += f"""
                        <div style="background:#1a1f00; border:1px solid #ffd70066; border-radius:8px; padding:12px; margin-bottom:15px;">
                            <div style="font-size:18px; font-weight:bold; color:#ffd700; margin-bottom:10px;">🏆 {c['name']} yeni rekor! ({dist:+.2f}%)</div>
                            <div style="font-size:13px; color:#c9d1d9; margin-bottom:8px;"><strong style="color:#ffd700;">Anlam:</strong> {rec_meaning}</div>
                            <div style="font-size:13px; color:#c9d1d9; margin-bottom:8px;"><strong style="color:#ffd700;">Tarihi Etki:</strong> {hist_impact}</div>
                            <div style="font-size:13px; color:#c9d1d9;"><strong style="color:#ffd700;">Etkilenen Sektörler:</strong> {affected}</div>
                        </div>
                        """
                    html += "</div>"
        
        # ══════════════════════════════════════════════
        # SEKTÖR SENTIMENT HARİTASI
        # ══════════════════════════════════════════════
        if sector_scores:
            numeric_scores = {k: v for k, v in sector_scores.items()
                              if isinstance(v, (int, float)) and k not in ("genel",)}
            if numeric_scores:
                sorted_sectors = sorted(numeric_scores.items(), key=lambda x: x[1], reverse=True)
                top3 = sorted_sectors[:3]
                bottom3 = sorted_sectors[-3:][::-1]
                
                html += """
                    <!-- 📊 SEKTÖR SENTIMENT HARİTASI -->
                    <div class="section">
                        <div class="section-title">📊 Sektör Sentiment Haritası</div>
                        <div style="display:grid; grid-template-columns:1fr 1fr; gap:15px;">
                            <div>
                                <div style="font-size:13px; color:#56d364; font-weight:bold; margin-bottom:10px;">🟢 En İyi 3 Sektör</div>
                """
                for s, sc in top3:
                    bar_w = min(100, int((sc + 1) * 50))
                    html += f"""
                                <div style="background:#21262d; border-radius:6px; padding:10px; margin-bottom:8px; border:1px solid #30363d;">
                                    <div style="display:flex; justify-content:space-between; font-size:13px;">
                                        <span style="color:#e6edf3; text-transform:capitalize;">{s.replace('_',' ')}</span>
                                        <span style="color:#56d364; font-weight:bold;">{sc:+.3f}</span>
                                    </div>
                                    <div style="background:#30363d; height:4px; border-radius:2px; margin-top:6px;">
                                        <div style="background:#56d364; width:{bar_w}%; height:4px; border-radius:2px;"></div>
                                    </div>
                                </div>
                    """
                html += """
                            </div>
                            <div>
                                <div style="font-size:13px; color:#f85149; font-weight:bold; margin-bottom:10px;">🔴 En Kötü 3 Sektör</div>
                """
                for s, sc in bottom3:
                    bar_w = min(100, int((sc + 1) * 50))
                    html += f"""
                                <div style="background:#21262d; border-radius:6px; padding:10px; margin-bottom:8px; border:1px solid #30363d;">
                                    <div style="display:flex; justify-content:space-between; font-size:13px;">
                                        <span style="color:#e6edf3; text-transform:capitalize;">{s.replace('_',' ')}</span>
                                        <span style="color:#f85149; font-weight:bold;">{sc:+.3f}</span>
                                    </div>
                                    <div style="background:#30363d; height:4px; border-radius:2px; margin-top:6px;">
                                        <div style="background:#f85149; width:{bar_w}%; height:4px; border-radius:2px;"></div>
                                    </div>
                                </div>
                    """
                html += """
                            </div>
                        </div>
                    </div>
                """
        
        html += f"""
                    <!-- SKOR & RATING REHBERİ -->
                    <details style="margin-bottom:18px;">
                        <summary style="cursor:pointer; font-size:16px; font-weight:bold; color:#e6edf3; padding:10px 0; border-bottom:2px solid #58a6ff; list-style:none; display:flex; align-items:center; gap:8px;">
                            <span style="transition:transform 0.2s; display:inline-block;">▶</span> 📖 Skor &amp; Rating Rehberi
                        </summary>
                        <div style="padding-top:12px;">
                        <table style="width:100%; border-collapse: collapse; background: #21262d; border-radius: 8px; overflow: hidden;">
                            <thead>
                                <tr style="background: #30363d;">
                                    <th style="padding: 8px 10px; text-align: left; color: #8b949e; font-size: 12px; text-transform: uppercase; font-weight: 600;">Skor</th>
                                    <th style="padding: 8px 10px; text-align: left; color: #8b949e; font-size: 12px; text-transform: uppercase; font-weight: 600;">Rating</th>
                                    <th style="padding: 8px 10px; text-align: left; color: #8b949e; font-size: 12px; text-transform: uppercase; font-weight: 600;">Anlamı</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr style="border-top: 1px solid #30363d;">
                                    <td style="padding: 6px 10px; color: #58a6ff; font-weight: bold;">≥ 80</td>
                                    <td style="padding: 6px 10px; color: #e6edf3; font-weight: bold;">🔥 GÜÇLÜ AL</td>
                                    <td style="padding: 6px 10px; color: #8b949e; font-size: 13px;">Teknik göstergeler çok olumlu, güçlü alım fırsatı</td>
                                </tr>
                                <tr style="border-top: 1px solid #30363d; background: #161b22;">
                                    <td style="padding: 6px 10px; color: #56d364; font-weight: bold;">≥ 70</td>
                                    <td style="padding: 6px 10px; color: #e6edf3; font-weight: bold;">🟢 AL</td>
                                    <td style="padding: 6px 10px; color: #8b949e; font-size: 13px;">Göstergeler olumlu, alım yapılabilir</td>
                                </tr>
                                <tr style="border-top: 1px solid #30363d;">
                                    <td style="padding: 6px 10px; color: #d29922; font-weight: bold;">≥ 60</td>
                                    <td style="padding: 6px 10px; color: #e6edf3; font-weight: bold;">🟡 TUT</td>
                                    <td style="padding: 6px 10px; color: #8b949e; font-size: 13px;">Mevcut pozisyonu koru, ne al ne sat</td>
                                </tr>
                                <tr style="border-top: 1px solid #30363d; background: #161b22;">
                                    <td style="padding: 6px 10px; color: #d29922; font-weight: bold;">≥ 40</td>
                                    <td style="padding: 6px 10px; color: #e6edf3; font-weight: bold;">🟠 AZALT</td>
                                    <td style="padding: 6px 10px; color: #8b949e; font-size: 13px;">Göstergeler olumsuz, pozisyonu kademeli azalt</td>
                                </tr>
                                <tr style="border-top: 1px solid #30363d;">
                                    <td style="padding: 6px 10px; color: #f85149; font-weight: bold;">&lt; 40</td>
                                    <td style="padding: 6px 10px; color: #e6edf3; font-weight: bold;">🔴 SAT</td>
                                    <td style="padding: 6px 10px; color: #8b949e; font-size: 13px;">Teknik göstergeler çok olumsuz, sat</td>
                                </tr>
                            </tbody>
                        </table>
                        </div>
                    </details>
                    
                    <!-- TEKNİK GÖSTERGE REHBERİ -->
                    <details style="margin-bottom:18px;">
                        <summary style="cursor:pointer; font-size:16px; font-weight:bold; color:#e6edf3; padding:10px 0; border-bottom:2px solid #58a6ff; list-style:none; display:flex; align-items:center; gap:8px;">
                            <span style="transition:transform 0.2s; display:inline-block;">▶</span> 🔬 Teknik Gösterge Rehberi
                        </summary>
                        <div style="padding-top:12px;">
                        <table style="width:100%; border-collapse: collapse; background: #21262d; border-radius: 8px; overflow: hidden;">
                            <thead>
                                <tr style="background: #30363d;">
                                    <th style="padding: 8px 10px; text-align: left; color: #8b949e; font-size: 12px; text-transform: uppercase; font-weight: 600;">Gösterge</th>
                                    <th style="padding: 8px 10px; text-align: left; color: #8b949e; font-size: 12px; text-transform: uppercase; font-weight: 600;">Açıklama</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr style="border-top: 1px solid #30363d;">
                                    <td style="padding: 6px 10px; color: #58a6ff; font-weight: bold; white-space: nowrap;">RSI ({config.RSI_PERIOD})</td>
                                    <td style="padding: 6px 10px; color: #8b949e; font-size: 13px;">{config.RSI_OVERSOLD} altı aşırı satım (alım fırsatı), {config.RSI_OVERBOUGHT} üzeri aşırı alım (satış sinyali)</td>
                                </tr>
                                <tr style="border-top: 1px solid #30363d; background: #161b22;">
                                    <td style="padding: 6px 10px; color: #58a6ff; font-weight: bold; white-space: nowrap;">MACD Histogram</td>
                                    <td style="padding: 6px 10px; color: #8b949e; font-size: 13px;">Pozitif → yükseliş trendi güçleniyor, Negatif → düşüş trendi güçleniyor</td>
                                </tr>
                                <tr style="border-top: 1px solid #30363d;">
                                    <td style="padding: 6px 10px; color: #58a6ff; font-weight: bold; white-space: nowrap;">SMA {config.SMA_SHORT} / SMA {config.SMA_LONG}</td>
                                    <td style="padding: 6px 10px; color: #8b949e; font-size: 13px;">Kısa/uzun vadeli ortalama; fiyat üstündeyse yükseliş, altındaysa düşüş</td>
                                </tr>
                                <tr style="border-top: 1px solid #30363d; background: #161b22;">
                                    <td style="padding: 6px 10px; color: #58a6ff; font-weight: bold; white-space: nowrap;">Bollinger Bantları</td>
                                    <td style="padding: 6px 10px; color: #8b949e; font-size: 13px;">Alt banda yakınsa alım fırsatı, üst banda yakınsa satış sinyali</td>
                                </tr>
                                <tr style="border-top: 1px solid #30363d;">
                                    <td style="padding: 6px 10px; color: #58a6ff; font-weight: bold; white-space: nowrap;">Momentum ({config.MOMENTUM_PERIOD}g)</td>
                                    <td style="padding: 6px 10px; color: #8b949e; font-size: 13px;">Pozitif → yukarı ivme, negatif → aşağı ivme</td>
                                </tr>
                                <tr style="border-top: 1px solid #30363d; background: #161b22;">
                                    <td style="padding: 6px 10px; color: #58a6ff; font-weight: bold; white-space: nowrap;">ATR</td>
                                    <td style="padding: 6px 10px; color: #8b949e; font-size: 13px;">Volatilite ölçüsü — yüksek ATR = yüksek risk ve hareket</td>
                                </tr>
                                <tr style="border-top: 1px solid #30363d;">
                                    <td style="padding: 6px 10px; color: #58a6ff; font-weight: bold; white-space: nowrap;">Fibonacci ({config.FIBONACCI_LOOKBACK}g)</td>
                                    <td style="padding: 6px 10px; color: #8b949e; font-size: 13px;">0.618 → güçlü destek, 0.236 → güçlü direnç noktası</td>
                                </tr>
                                <tr style="border-top: 1px solid #30363d; background: #161b22;">
                                    <td style="padding: 6px 10px; color: #58a6ff; font-weight: bold; white-space: nowrap;">Risk/Reward</td>
                                    <td style="padding: 6px 10px; color: #8b949e; font-size: 13px;">Kazanç/risk oranı ≥ {config.MIN_REWARD_RISK} olmalı (swing trade filtresi)</td>
                                </tr>
                            </tbody>
                        </table>
                        </div>
                    </details>
                    
                    <!-- ÖNERİLER BÖLÜMÜ -->
                    <div class="section">
                        <div class="section-title">🎯 En İyi {config.MAX_RECOMMENDATIONS} Hisse</div>
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
                target_price = rec.get('target_price', resistance)
                stop_loss = rec.get('stop_loss', support)
                expected_gain_pct = rec.get('expected_gain_pct', reward_pct)
                max_risk_pct = rec.get('max_risk_pct', risk_pct)
                rr_ratio = rec.get('reward_risk_ratio', 0)
                timeframe = rec.get('timeframe', '~1 Ay (21 İş Günü)')
                breakout = rec.get('breakout', {})
                
                rsi_color = _rsi_color(rsi)
                rsi_label = _rsi_label(rsi)
                score_pct = min(100, max(0, score))
                
                fib_236 = fibonacci.get('fib_0.236') or 0
                fib_382 = fibonacci.get('fib_0.382') or 0
                fib_618 = fibonacci.get('fib_0.618') or 0
                fib_236_str = f"{currency}{fib_236:.2f}" if fib_236 else "Veri Yok"
                fib_382_str = f"{currency}{fib_382:.2f}" if fib_382 else "Veri Yok"
                fib_618_str = f"{currency}{fib_618:.2f}" if fib_618 else "Veri Yok"
                
                # Breakout etiketi
                breakout_type = breakout.get('type') if breakout else None
                volume_surge = breakout.get('volume_surge', False) if breakout else False
                if breakout_type == "resistance_break":
                    breakout_label = "🔥 DİRENÇ KIRILDI" + (" + 📦 YÜKSEK HACİM" if volume_surge else "")
                    breakout_color = "#ffd700"
                elif breakout_type == "near_resistance":
                    breakout_label = "📈 DİRENÇE YAKIN" + (" + 📦 YÜKSEK HACİM" if volume_surge else "")
                    breakout_color = "#d29922"
                elif breakout_type == "support_bounce":
                    breakout_label = "🔄 DESTEK SEKMESI"
                    breakout_color = "#58a6ff"
                else:
                    breakout_label = "📊 TREND GİRİŞİ"
                    breakout_color = "#8b949e"
                
                html += f"""
                    <div class="stock-card">
                        <!-- BAŞLIK -->
                        <div class="stock-header">
                            <div>
                                <div class="stock-rank">#{i}</div>
                                <div class="ticker">{ticker}</div>
                                <div class="sector">{sector}</div>
                            </div>
                            <div>
                                <div class="rating-badge">{rating}</div>
                                <div style="margin-top:8px; padding:4px 10px; background:{breakout_color}22; color:{breakout_color}; border-radius:12px; font-size:12px; font-weight:bold; text-align:center;">{breakout_label}</div>
                            </div>
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
                        
                        <!-- HEDEF FİYAT / STOP-LOSS / VADE -->
                        <div style="display:grid; grid-template-columns:repeat(3,1fr); gap:12px; margin-bottom:12px;">
                            <div style="background:#1a4a1a; border:1px solid #56d36466; border-radius:8px; padding:10px; text-align:center;">
                                <div style="font-size:11px; color:#56d364; text-transform:uppercase; margin-bottom:6px;">🎯 Hedef Fiyat</div>
                                <div style="font-size:14px; font-weight:bold; color:#56d364;">{currency}{target_price:.2f}</div>
                                <div style="font-size:12px; color:#56d364; margin-top:4px;">+{expected_gain_pct:.1f}%</div>
                            </div>
                            <div style="background:#3d0c0c; border:1px solid #f8514966; border-radius:8px; padding:10px; text-align:center;">
                                <div style="font-size:11px; color:#f85149; text-transform:uppercase; margin-bottom:6px;">🛑 Stop-Loss</div>
                                <div style="font-size:14px; font-weight:bold; color:#f85149;">{currency}{stop_loss:.2f}</div>
                                <div style="font-size:12px; color:#f85149; margin-top:4px;">-{max_risk_pct:.1f}%</div>
                            </div>
                            <div style="background:#162032; border:1px solid #58a6ff66; border-radius:8px; padding:10px; text-align:center;">
                                <div style="font-size:11px; color:#58a6ff; text-transform:uppercase; margin-bottom:6px;">⚖️ R/R Oranı</div>
                                <div style="font-size:14px; font-weight:bold; color:#58a6ff;">{rr_ratio:.2f}x</div>
                                <div style="font-size:12px; color:#8b949e; margin-top:4px;">📅 {timeframe}</div>
                            </div>
                        </div>
                        
                        <!-- TEKNİK GÖSTERGELER -->
                        <div class="technical-indicators">
                            <h4 style="margin-bottom: 15px; color: #e6edf3;">📊 Teknik Göstergeler</h4>
                            <div class="indicator-row">
                                <div class="indicator-item">
                                    <div class="indicator-label">RSI ({config.RSI_PERIOD})</div>
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
                                    <div class="indicator-label">SMA {config.SMA_SHORT}</div>
                                    <div class="indicator-value">{currency}{sma_short:.2f}</div>
                                </div>
                                <div class="indicator-item">
                                    <div class="indicator-label">SMA {config.SMA_LONG}</div>
                                    <div class="indicator-value">{currency}{sma_long:.2f}</div>
                                </div>
                            </div>
                            <div class="indicator-row">
                                <div class="indicator-item">
                                    <div class="indicator-label">Momentum ({config.MOMENTUM_PERIOD}g)</div>
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
                                <div class="rr-label">Max Risk</div>
                                <div class="rr-value">{risk_pct:.1f}%</div>
                            </div>
                            <div class="rr-box reward-box">
                                <div class="rr-label">Tahmini Kazanç</div>
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
                    
                    <!-- 📅 TATİL & VOLATİLİTE UYARISI -->
        """
        
        if holiday_alerts:
            html += """
                    <div class="section">
                        <div class="section-title">📅 Tatil &amp; Volatilite Uyarısı</div>
                        <div style="background:#21262d; border-radius:8px; padding:12px; border:1px solid #30363d;">
            """
            for h in holiday_alerts[:6]:
                impact_color = {"high": "#f85149", "medium": "#d29922", "low": "#56d364"}.get(h.get("impact", "low"), "#8b949e")
                html += f"""
                            <div style="display:flex; justify-content:space-between; align-items:center; padding:10px 0; border-bottom:1px solid #30363d; font-size:13px;">
                                <div>
                                    <span style="color:#d29922; font-size:14px;">⚠️</span>
                                    <strong style="color:#e6edf3; margin-left:6px;">{h.get('exchange','')}</strong>
                                    <span style="color:#8b949e; margin-left:6px;">— {h.get('name','')}</span>
                                </div>
                                <div style="text-align:right;">
                                    <div style="color:#8b949e; font-size:12px;">{h.get('start','')} – {h.get('end','')}</div>
                                    <div style="color:{impact_color}; font-size:11px; font-weight:bold; margin-top:2px;">ETKİ: {h.get('impact','').upper()}</div>
                                </div>
                            </div>
                """
            html += """
                        </div>
                    </div>
            """
        
        html += f"""
                    <!-- DISCLAIMER -->
                    <div class="disclaimer">
                        <strong>⚠️ Önemli Uyarı:</strong> Bu analiz tamamen otomatik olarak üretilmiştir ve 
                        <strong>yatırım tavsiyesi DEĞİLDİR</strong>. Tüm yatırım kararlarınızı kendi araştırmanız, 
                        risk analizi ve profesyonel danışmanlığa dayandırınız. Kripto varlıklar ve hisse senetleri 
                        yüksek riskli yatırımlardır.
                    </div>
                    
                    <!-- SKOR HESAPLAMA BİLGİ KUTUSU -->
                    <details style="margin-bottom:18px;">
                        <summary style="cursor:pointer; font-size:16px; font-weight:bold; color:#e6edf3; padding:10px 0; border-bottom:2px solid #58a6ff; list-style:none; display:flex; align-items:center; gap:8px;">
                            <span style="transition:transform 0.2s; display:inline-block;">▶</span> ℹ️ Skor Nasıl Hesaplanır?
                        </summary>
                        <div style="margin-top:12px; background:#161b22; border:1px solid #30363d; border-radius:8px; padding:12px; font-size:12px; color:#8b949e;">
                            <div>• %60 Teknik Analiz (RSI, MACD, SMA, Bollinger, Momentum)</div>
                            <div>• %40 Haber Sentiment (Sektör bazlı duygu analizi)</div>
                            <div style="margin-top:8px;">• Filtreler: Trend ↑ | Momentum &gt; 0 | R/R &gt; {config.MIN_REWARD_RISK} | Skor ≥ {config.MIN_BUY_SCORE}</div>
                            <div style="margin-top:4px;">• Parametreler: RSI-{config.RSI_PERIOD} | SMA {config.SMA_SHORT}/{config.SMA_LONG} | Momentum-{config.MOMENTUM_PERIOD}g | Lookback-{config.LOOKBACK_DAYS}g</div>
                        </div>
                    </details>
                    
                    <!-- FOOTER -->
                </div>
                
                <div class="footer">
                    <p style="font-size: 16px; font-weight: 600; margin-bottom: 10px; color: #e6edf3;">🤖 BorsaBot v8.0</p>
                    <p>Akıllı Teknik Analiz & Makro Ekonomi & Emtia Takip Sistemi</p>
                    <p style="margin-top: 15px; opacity: 0.8;">
                        Analiz Tarihi: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}<br>
                        Sistem: Teknik Analiz + Haber Sentiment + Fibonacci + Breakout Detection + Makro Analiz
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
                "rsi": 32.3,
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
                "signals": ["📈 SMA → Bullish", "📊 RSI 32.3 → Düşük", "📈 Momentum +3.45%"],
                "fibonacci": {
                    "current": 45.50,
                    "fib_0.236": 47.10,
                    "fib_0.382": 46.20,
                    "fib_0.618": 43.80
                },
                "target_price": 48.30,
                "stop_loss": 42.50,
                "expected_gain_pct": 6.15,
                "max_risk_pct": 4.40,
                "reward_risk_ratio": 1.40,
                "timeframe": "~1 Ay (21 İş Günü)",
                "breakout": {"type": "near_resistance", "volume_surge": True, "resistance": 48.30, "support": 42.50},
            }
        ],
        "market_summary": {
            "avg_score": 72.5,
            "total_analyzed": 10,
            "total_passed_filter": 1,
            "bullish_count": 6,
            "bearish_count": 2,
            "neutral_count": 2,
            "avg_rsi": 48.0,
            "avg_momentum": 1.2,
            "avg_reward_risk": 1.40,
            "source_breakdown": {"historical": 8, "realtime": 1, "fallback": 1},
        }
    }
    
    test_macro = {
        "us_debt": {
            "debt_trillion": 38.8,
            "gdp_ratio_pct": 124,
            "risk_level": "Yüksek",
            "comment": "Tarihsel rekor seviyelerde borç",
        },
        "dxy": {
            "current": 104.2,
            "monthly_change_pct": -1.5,
            "trend": "Düşüş",
            "interpretation": "DXY düşüyor → emtia ve gelişen piyasalar için pozitif",
        },
        "geopolitical_risk": {
            "risk_level": "Orta",
            "risks": ["tariff", "trade war"],
            "affected_sectors": ["enerji", "savunma"],
            "risk_count": 2,
        },
        "supply_demand_trends": [
            {"keyword": "chip shortage", "impact": "bullish", "sectors": ["teknoloji"], "source": "Reuters"},
        ],
    }
    
    test_commodities = {
        "GC=F": {"name": "Altın", "skip": False, "current_price": 2450.5, "daily_change_pct": 0.8,
                 "rsi": 62, "trend": "Yükseliş",
                 "record_info": {"is_record": True, "high_52w": 2450.5, "current": 2450.5, "distance_pct": 0.0},
                 "context": config.COMMODITY_RECORD_CONTEXT.get("GC=F", {})},
        "CL=F": {"name": "Ham Petrol", "skip": False, "current_price": 78.3, "daily_change_pct": -0.5,
                 "rsi": 48, "trend": "Nötr",
                 "record_info": {"is_record": False, "high_52w": 95.0, "current": 78.3, "distance_pct": -17.6},
                 "context": {}},
    }
    
    from macro_analyzer import MacroAnalyzer
    test_holidays = MacroAnalyzer.check_upcoming_holidays(days_ahead=365)[:3]
    
    html = generate_html_body(
        recommendations=test_rec,
        commodity_data=test_commodities,
        macro_data=test_macro,
        sector_scores={"teknoloji": 0.7, "enerji": 0.3, "finans": 0.5, "sağlık": 0.4, "perakende": 0.2, "otomotiv": 0.1},
        holiday_alerts=test_holidays,
    )
    print("✅ HTML başarıyla oluşturuldu")
    print(f"📄 HTML uzunluğu: {len(html)} karakter")
