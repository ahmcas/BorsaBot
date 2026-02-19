# ============================================================
# macro_analyzer.py — Makro Ekonomik Analiz (v1)
# ============================================================
# ABD Borç, DXY, Jeopolitik Risk, Arz-Talep, Tatil Takibi
# ============================================================

import warnings
warnings.filterwarnings('ignore')

from datetime import datetime, timedelta

try:
    import yfinance as yf
except ImportError:
    import subprocess
    subprocess.run(["pip", "install", "yfinance"], check=True)
    import yfinance as yf

import config
from technical_analyzer import TechnicalAnalyzer


class MacroAnalyzer:
    """Makro Ekonomik Analiz"""

    @staticmethod
    def analyze_dxy() -> dict:
        """Dolar Endeksi (DXY) analizi"""
        try:
            import pandas as pd
            ticker = config.DXY_TICKER
            df = yf.download(ticker, period="250d", progress=False, timeout=30)

            if df is None or df.empty:
                return {"ticker": ticker, "skip": True, "reason": "Veri alınamadı"}

            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)
            df.columns = [str(c).lower().replace(" ", "_") for c in df.columns]

            for col in ["close", "high", "low", "volume"]:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors="coerce")
            df = df.dropna(subset=["close"])

            if len(df) < 20:
                return {"ticker": ticker, "skip": True, "reason": "Yetersiz veri"}

            close = df["close"]
            current = float(close.iloc[-1])

            rsi = TechnicalAnalyzer.calculate_rsi(close, period=config.RSI_PERIOD)
            sma_s = TechnicalAnalyzer.calculate_sma(close, config.SMA_SHORT)

            # 1 aylık değişim
            month_ago_idx = max(0, len(close) - config.MOMENTUM_PERIOD)
            month_ago_price = float(close.iloc[month_ago_idx])
            monthly_change = round(((current - month_ago_price) / month_ago_price) * 100, 2) if month_ago_price else 0

            trend_info = TechnicalAnalyzer.analyze_trend(df)
            trend = trend_info.get("trend", "Nötr")

            # Yorumlama
            if monthly_change < -2:
                interpretation = "DXY düşüyor → emtia ve gelişen piyasalar için pozitif"
            elif monthly_change > 2:
                interpretation = "DXY yükseliyor → emtia baskı altında, dikkat"
            else:
                interpretation = "DXY nötr → piyasalar üzerinde belirgin etki yok"

            return {
                "ticker": ticker,
                "skip": False,
                "current": round(current, 2),
                "monthly_change_pct": monthly_change,
                "rsi": rsi,
                "sma_short": sma_s,
                "trend": trend,
                "interpretation": interpretation,
            }

        except Exception as e:
            return {"ticker": config.DXY_TICKER, "skip": True, "reason": str(e)[:100]}

    @staticmethod
    def get_us_debt_analysis() -> dict:
        """ABD borç analizi"""
        debt = config.US_DEBT_TRILLION
        gdp_ratio = config.US_DEBT_GDP_RATIO

        if gdp_ratio >= 130:
            risk_level = "Kritik"
            comment = "Borç sürdürülemez seviyeye yaklaşıyor, dolar değer kaybı riski yüksek"
        elif gdp_ratio >= 120:
            risk_level = "Yüksek"
            comment = "Tarihsel rekor seviyelerde borç; faiz ödemeleri bütçeyi zorluyor"
        elif gdp_ratio >= 100:
            risk_level = "Orta"
            comment = "GDP'yi aşan borç seviyesi; uzun vadede sürdürülebilirlik sorgulanıyor"
        else:
            risk_level = "Düşük"
            comment = "Borç kontrollü seviyelerde"

        return {
            "debt_trillion": debt,
            "gdp_ratio_pct": gdp_ratio,
            "risk_level": risk_level,
            "comment": comment,
            "context": (
                f"ABD borcu ${debt}T (GDP'nin %{gdp_ratio}'ı). "
                "Yüksek borç → faiz ödemeleri artar → dolar baskı altında → "
                "emtia ve altın için pozitif ortam."
            ),
        }

    @staticmethod
    def analyze_geopolitical_risk(news_data: list) -> dict:
        """Jeopolitik risk analizi"""
        try:
            keywords = config.GEOPOLITICAL_KEYWORDS
            detected_risks = []
            affected_sectors = set()

            for article in news_data:
                title = (article.get("title") or "").lower()
                desc = (article.get("description") or "").lower()
                text = f"{title} {desc}"

                for kw in keywords:
                    if kw.lower() in text:
                        if kw not in detected_risks:
                            detected_risks.append(kw)
                        # Enerji/savunma her zaman etkilenir
                        affected_sectors.update(["enerji", "savunma"])

            risk_count = len(detected_risks)
            if risk_count == 0:
                risk_level = "Düşük"
            elif risk_count <= 2:
                risk_level = "Orta"
            elif risk_count <= 5:
                risk_level = "Yüksek"
            else:
                risk_level = "Kritik"

            return {
                "risk_level": risk_level,
                "risks": detected_risks[:10],
                "affected_sectors": list(affected_sectors),
                "risk_count": risk_count,
            }

        except Exception:
            return {"risk_level": "Bilinmiyor", "risks": [], "affected_sectors": [], "risk_count": 0}

    @staticmethod
    def detect_supply_demand_trends(news_data: list) -> list:
        """Arz-talep trend tespiti"""
        try:
            keywords = config.SUPPLY_DEMAND_KEYWORDS
            detected = []

            for article in news_data:
                title = (article.get("title") or "").lower()
                desc = (article.get("description") or "").lower()
                text = f"{title} {desc}"

                for kw, info in keywords.items():
                    if kw.lower() in text:
                        entry = {
                            "keyword": kw,
                            "impact": info["impact"],
                            "sectors": info["sectors"],
                            "source": article.get("source", ""),
                        }
                        # Tekrar ekleme
                        if kw not in [d["keyword"] for d in detected]:
                            detected.append(entry)

            return detected

        except Exception:
            return []

    @staticmethod
    def check_upcoming_holidays(days_ahead: int = 14) -> list:
        """Yaklaşan borsa tatillerini kontrol et"""
        try:
            today = datetime.now().date()
            cutoff = today + timedelta(days=days_ahead)
            alerts = []

            for exchange, holidays in config.MARKET_HOLIDAYS_2026.items():
                for h in holidays:
                    start = datetime.strptime(h["start"], "%Y-%m-%d").date()
                    end = datetime.strptime(h["end"], "%Y-%m-%d").date()

                    # Tatil önümüzdeki days_ahead gün içinde mi?
                    if start <= cutoff and end >= today:
                        days_to_start = (start - today).days
                        alerts.append({
                            "exchange": exchange,
                            "name": h["name"],
                            "start": h["start"],
                            "end": h["end"],
                            "impact": h["impact"],
                            "days_to_start": max(0, days_to_start),
                            "message": (
                                f"⚠️ {exchange} — {h['name']} "
                                f"({h['start']} – {h['end']}) "
                                f"[Etki: {h['impact'].upper()}]"
                            ),
                        })

            # Yakın tarihten uzağa sırala
            alerts.sort(key=lambda x: x["days_to_start"])
            return alerts

        except Exception:
            return []


if __name__ == "__main__":
    print("🧪 Macro Analyzer Testi")
    print("=" * 70)

    # DXY Analizi
    print("\n📊 DXY (Dolar Endeksi):")
    dxy = MacroAnalyzer.analyze_dxy()
    if not dxy.get("skip"):
        print(f"  Mevcut: {dxy['current']}")
        print(f"  Aylık Değişim: {dxy['monthly_change_pct']:+.2f}%")
        print(f"  RSI: {dxy['rsi']}")
        print(f"  Trend: {dxy['trend']}")
        print(f"  Yorum: {dxy['interpretation']}")
    else:
        print(f"  HATA: {dxy.get('reason')}")

    # ABD Borç Analizi
    print("\n🇺🇸 ABD Borç Analizi:")
    debt = MacroAnalyzer.get_us_debt_analysis()
    print(f"  Borç: ${debt['debt_trillion']}T")
    print(f"  GDP Oranı: %{debt['gdp_ratio_pct']}")
    print(f"  Risk: {debt['risk_level']}")
    print(f"  Yorum: {debt['comment']}")

    # Tatil Kontrolü
    print("\n📅 Yaklaşan Tatiller (14 gün):")
    holidays = MacroAnalyzer.check_upcoming_holidays(days_ahead=14)
    if holidays:
        for h in holidays:
            print(f"  {h['message']}")
    else:
        print("  Yaklaşan tatil yok")

    # Jeopolitik Risk (boş veri ile)
    print("\n🌐 Jeopolitik Risk (örnek veri):")
    sample_articles = [
        {"title": "NATO tensions rise amid conflict", "description": "military crisis escalates"},
        {"title": "Oil trade war fears", "description": "tariff sanctions imposed"},
    ]
    geo = MacroAnalyzer.analyze_geopolitical_risk(sample_articles)
    print(f"  Risk Seviyesi: {geo['risk_level']}")
    print(f"  Tespit Edilen: {geo['risks']}")

    # Arz-Talep
    sd = MacroAnalyzer.detect_supply_demand_trends(sample_articles)
    print(f"\n🔍 Arz-Talep Trendleri: {len(sd)} tespit edildi")
    for item in sd:
        print(f"  • {item['keyword']} → {item['impact']} ({', '.join(item['sectors'])})")
