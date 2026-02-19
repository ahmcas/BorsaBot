# ============================================================
# commodity_analyzer.py — Emtia Analiz Motoru (v1)
# ============================================================
# Altın, Gümüş, Bakır, Petrol vb. emtia analizleri
# ============================================================

import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')

try:
    import yfinance as yf
except ImportError:
    import subprocess
    subprocess.run(["pip", "install", "yfinance"], check=True)
    import yfinance as yf

import config
from technical_analyzer import TechnicalAnalyzer


class CommodityAnalyzer:
    """Emtia Piyasası Analizi"""

    @staticmethod
    def analyze_single_commodity(name: str, ticker: str) -> dict:
        """Tek emtia analiz et"""
        try:
            df = yf.download(ticker, period="250d", progress=False, timeout=30)

            if df is None or df.empty:
                return {"name": name, "ticker": ticker, "skip": True, "reason": "Veri alınamadı"}

            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)
            df.columns = [str(c).lower().replace(" ", "_") for c in df.columns]

            required = ["close", "high", "low", "volume"]
            if not all(c in df.columns for c in required):
                return {"name": name, "ticker": ticker, "skip": True, "reason": "Eksik sütun"}

            for col in required:
                df[col] = pd.to_numeric(df[col], errors="coerce")
            df = df.dropna()

            if len(df) < 20:
                return {"name": name, "ticker": ticker, "skip": True, "reason": "Yetersiz veri"}

            close = df["close"]
            current_price = float(close.iloc[-1])

            # Göstergeler
            rsi = TechnicalAnalyzer.calculate_rsi(close, period=config.RSI_PERIOD)
            sma_s = TechnicalAnalyzer.calculate_sma(close, config.SMA_SHORT)
            sma_l = TechnicalAnalyzer.calculate_sma(close, config.SMA_LONG)
            momentum = TechnicalAnalyzer.calculate_momentum(close, period=config.MOMENTUM_PERIOD)

            # Trend
            trend_info = TechnicalAnalyzer.analyze_trend(df)

            # Günlük değişim
            prev_close = float(close.iloc[-2]) if len(close) > 1 else current_price
            daily_change_pct = round(((current_price - prev_close) / prev_close) * 100, 2) if prev_close else 0

            # 52 haftalık rekor
            record_info = CommodityAnalyzer.check_52week_record(ticker, df)

            # Bağlam bilgisi
            context = config.COMMODITY_RECORD_CONTEXT.get(ticker, {})

            return {
                "name": name,
                "ticker": ticker,
                "skip": False,
                "current_price": round(current_price, 4),
                "daily_change_pct": daily_change_pct,
                "rsi": rsi,
                "sma_short": sma_s,
                "sma_long": sma_l,
                "momentum_pct": momentum,
                "trend": trend_info.get("trend", "Nötr"),
                "trend_strength": trend_info.get("strength", "N/A"),
                "record_info": record_info,
                "context": context,
            }

        except Exception as e:
            return {"name": name, "ticker": ticker, "skip": True, "reason": str(e)[:100]}

    @staticmethod
    def check_52week_record(ticker: str, df: pd.DataFrame) -> dict:
        """52 haftalık rekor kontrolü"""
        try:
            high_52w = float(df["high"].tail(252).max())
            current = float(df["close"].iloc[-1])
            is_record = current >= high_52w * 0.99  # %1 yakınlık
            return {
                "is_record": is_record,
                "high_52w": round(high_52w, 4),
                "current": round(current, 4),
                "distance_pct": round(((current - high_52w) / high_52w) * 100, 2),
            }
        except Exception:
            return {"is_record": False, "high_52w": 0, "current": 0, "distance_pct": 0}

    @staticmethod
    def analyze_all_commodities() -> dict:
        """Tüm emtiaları analiz et"""
        print("\n⛏️  Emtia Analizi Başlıyor...")
        results = {}

        for name, ticker in config.COMMODITIES.items():
            result = CommodityAnalyzer.analyze_single_commodity(name, ticker)
            results[ticker] = result

            if not result.get("skip"):
                record_flag = "🏆 REKOR!" if result["record_info"]["is_record"] else ""
                print(
                    f"   {'✅'} {name:20s} | ${result['current_price']:>10.2f} "
                    f"| {result['daily_change_pct']:+.2f}% | RSI: {result['rsi']:5.1f} "
                    f"| {result['trend']:15s} {record_flag}"
                )
            else:
                print(f"   ❌ {name:20s} — {result.get('reason', 'Bilinmeyen hata')}")

        print(f"✅ {sum(1 for r in results.values() if not r.get('skip'))}/{len(results)} emtia analiz edildi")
        return results

    @staticmethod
    def get_commodity_summary(results: dict = None) -> list:
        """Emtia özet raporu — her emtia için mini bilgi"""
        if results is None:
            results = CommodityAnalyzer.analyze_all_commodities()

        summary = []
        for ticker, data in results.items():
            if data.get("skip"):
                continue
            summary.append({
                "name": data["name"],
                "ticker": ticker,
                "price": data["current_price"],
                "change_pct": data["daily_change_pct"],
                "rsi": data["rsi"],
                "trend": data["trend"],
                "is_record": data["record_info"]["is_record"],
                "distance_pct": data["record_info"]["distance_pct"],
                "context": data.get("context", {}),
            })
        return summary


if __name__ == "__main__":
    print("🧪 Commodity Analyzer Testi")
    print("=" * 70)

    # En az 3 emtia analiz et
    test_commodities = {
        "Altın": "GC=F",
        "Bakır": "HG=F",
        "Ham Petrol (WTI)": "CL=F",
    }

    for name, ticker in test_commodities.items():
        result = CommodityAnalyzer.analyze_single_commodity(name, ticker)
        if not result.get("skip"):
            print(f"\n{name} ({ticker}):")
            print(f"  Fiyat: ${result['current_price']}")
            print(f"  Günlük: {result['daily_change_pct']:+.2f}%")
            print(f"  RSI: {result['rsi']}")
            print(f"  Trend: {result['trend']}")
            print(f"  52W Rekor: {result['record_info']['is_record']} ({result['record_info']['distance_pct']:+.2f}%)")
        else:
            print(f"\n{name}: HATA — {result.get('reason')}")
