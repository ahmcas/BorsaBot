# ============================================================
# technical_analyzer.py — Teknik Analiz Engine (FIXED)
# ============================================================
# Bu modül:
# 1) yfinance ile hisse verileri çeker
# 2) RSI, MACD, Bollinger, SMA hesaplar
# 3) Fibonacci destek/direnç seviyelerini belirler
# 4) Her hisse için 0-100 arası teknik skor üretir
# ============================================================

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import config


def download_stock_data(ticker: str, period_days: int = 200) -> pd.DataFrame:
    """
    Bir hisse için son N günsünün verisini çeker.
    Döndürür: OHLCV DataFrame
    """
    end_date = datetime.now()
    start_date = end_date - timedelta(days=period_days)

    try:
        df = yf.download(
            ticker,
            start=start_date.strftime("%Y-%m-%d"),
            end=end_date.strftime("%Y-%m-%d"),
            progress=False,
            auto_adjust=True
        )

        if df.empty:
            print(f"[⚠️] {ticker} için veri bulunamadı.")
            return pd.DataFrame()

        # Column flatten (yfinance bazen multi-index döndürür)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        return df

    except Exception as e:
        print(f"[❌] {ticker} veri çekme hatası: {e}")
        return pd.DataFrame()


def calculate_rsi(prices: pd.Series, period: int = 14) -> pd.Series:
    """RSI (Relative Strength Index) hesaplar."""
    try:
        delta = prices.diff()
        gain = delta.where(delta > 0, 0.0)
        loss = (-delta).where(delta < 0, 0.0)

        avg_gain = gain.rolling(window=period).mean()
        avg_loss = loss.rolling(window=period).mean()

        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    except Exception as e:
        print(f"RSI hesaplama hatası: {e}")
        return pd.Series([50] * len(prices))


def calculate_macd(prices: pd.Series,
                   fast: int = 12, slow: int = 26, signal: int = 9) -> dict:
    """
    MACD hesaplar.
    Döndürür: {"macd_line": Series, "signal_line": Series, "histogram": Series}
    """
    try:
        ema_fast = prices.ewm(span=fast, adjust=False).mean()
        ema_slow = prices.ewm(span=slow, adjust=False).mean()

        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=signal, adjust=False).mean()
        histogram = macd_line - signal_line

        return {
            "macd_line": macd_line,
            "signal_line": signal_line,
            "histogram": histogram
        }
    except Exception as e:
        print(f"MACD hesaplama hatası: {e}")
        return {
            "macd_line": pd.Series([0] * len(prices)),
            "signal_line": pd.Series([0] * len(prices)),
            "histogram": pd.Series([0] * len(prices))
        }


def calculate_bollinger_bands(prices: pd.Series, period: int = 20,
                              std_dev: float = 2.0) -> dict:
    """
    Bollinger Bands hesaplar.
    Döndürür: {"upper": Series, "middle": Series, "lower": Series}
    """
    try:
        sma = prices.rolling(window=period).mean()
        std = prices.rolling(window=period).std()

        return {
            "upper": sma + (std * std_dev),
            "middle": sma,
            "lower": sma - (std * std_dev)
        }
    except Exception as e:
        print(f"Bollinger Bands hesaplama hatası: {e}")
        return {
            "upper": prices,
            "middle": prices,
            "lower": prices
        }


def calculate_fibonacci_levels(df: pd.DataFrame, lookback: int = 60) -> dict:
    """
    Son 60 gün içinde Fibonacci destek/direnç seviyelerini hesaplar.
    """
    try:
        recent = df.tail(lookback)
        if recent.empty:
            return {}

        high = float(recent["High"].max())
        low = float(recent["Low"].min())
        diff = high - low

        levels = {}
        for level in config.FIBONACCI_LEVELS:
            levels[f"fib_{level}"] = round(low + (diff * level), 2)

        levels["high"] = round(high, 2)
        levels["low"] = round(low, 2)
        levels["current"] = round(float(df["Close"].iloc[-1]), 2)

        return levels
    except Exception as e:
        print(f"Fibonacci hesaplama hatası: {e}")
        return {}


def calculate_momentum(prices: pd.Series, period: int = 10) -> float:
    """
    Momentum: Son N gün fiyat değişimi (yüzde).
    """
    try:
        if len(prices) < period:
            return 0.0
        
        current = float(prices.iloc[-1])
        past = float(prices.iloc[-period])
        
        if past == 0:
            return 0.0
        
        return float((current - past) / past * 100)
    except Exception as e:
        print(f"Momentum hesaplama hatası: {e}")
        return 0.0


def score_technical(df: pd.DataFrame) -> dict:
    """
    Bir hisse için teknik skor hesaplar (0-100 arası).
    
    Score kriterleri:
    - RSI: 30-70 arası normal → 30 altı oversold → 70 üstü overbought
    - MACD: Histogram pozitif = bullish
    - Bollinger: Fiyat bant altında = potansiyel alım
    - SMA: Fiyat > SMA50 = yukarı trend
    - Momentum: Pozitif momentum olumlu
    """
    if df.empty or len(df) < 60:
        return {
            "score": 0,
            "rsi": 50,
            "macd_histogram": 0,
            "bollinger_position": "unknown",
            "momentum_pct": 0,
            "sma_short": 0,
            "sma_long": 0,
            "fibonacci": {},
            "signals": ["Yeterli veri yok"],
            "current_price": 0
        }

    try:
        close = df["Close"].squeeze()
        score = 50  # Başlangıç neutral
        signals = []

        # --- RSI Analizi (max ±15 puan) ---
        rsi = calculate_rsi(close, config.RSI_PERIOD)
        current_rsi = float(rsi.iloc[-1]) if not pd.isna(rsi.iloc[-1]) else 50

        if current_rsi < 30:
            rsi_bonus = 15
            signals.append(f"RSI {current_rsi:.1f} → Oversold (Alım Sinyali)")
        elif current_rsi < 45:
            rsi_bonus = 8
            signals.append(f"RSI {current_rsi:.1f} → Düşük Bölge")
        elif current_rsi > 70:
            rsi_bonus = -15
            signals.append(f"RSI {current_rsi:.1f} → Overbought (Dikkat)")
        elif current_rsi > 55:
            rsi_bonus = 3
            signals.append(f"RSI {current_rsi:.1f} → Normal-Güçlü")
        else:
            rsi_bonus = 0
            signals.append(f"RSI {current_rsi:.1f} → Neutral")

        score += rsi_bonus

        # --- MACD Analizi (max ±15 puan) ---
        macd = calculate_macd(close, config.MACD_FAST, config.MACD_SLOW, config.MACD_SIGNAL)
        hist_current = float(macd["histogram"].iloc[-1]) if not pd.isna(macd["histogram"].iloc[-1]) else 0
        hist_prev = float(macd["histogram"].iloc[-2]) if len(macd["histogram"]) > 1 else 0

        if hist_current > 0 and hist_prev > 0:
            macd_bonus = 15
            signals.append("MACD → Güçlü Bullish (Histogram pozitif)")
        elif hist_current > 0 and hist_prev <= 0:
            macd_bonus = 12
            signals.append("MACD → Bullish Crossover (Alım Sinyali)")
        elif hist_current < 0 and hist_prev > 0:
            macd_bonus = -12
            signals.append("MACD → Bearish Crossover (Satım Sinyali)")
        elif hist_current < 0:
            macd_bonus = -8
            signals.append("MACD → Bearish")
        else:
            macd_bonus = 0

        score += macd_bonus

        # --- Bollinger Band Analizi (max ±10 puan) ---
        bollinger = calculate_bollinger_bands(close, config.BOLLINGER_PERIOD)
        current_price = float(close.iloc[-1])
        upper = float(bollinger["upper"].iloc[-1]) if not pd.isna(bollinger["upper"].iloc[-1]) else current_price
        lower = float(bollinger["lower"].iloc[-1]) if not pd.isna(bollinger["lower"].iloc[-1]) else current_price

        if current_price < lower:
            bb_bonus = 10
            signals.append("Bollinger → Fiyat Alt Bantın Altında (Alım Potansiyeli)")
        elif current_price < lower * 1.02:
            bb_bonus = 5
            signals.append("Bollinger → Alt Bant Yakınında")
        elif current_price > upper:
            bb_bonus = -8
            signals.append("Bollinger → Fiyat Üst Bantın Üstünde (Dikkat)")
        else:
            bb_bonus = 0
            signals.append("Bollinger → Band İçinde (Normal)")

        score += bb_bonus

        # --- SMA Analizi (max ±10 puan) ---
        sma_short = float(close.rolling(window=config.SMA_SHORT).mean().iloc[-1]) if len(close) >= config.SMA_SHORT else current_price
        sma_long = float(close.rolling(window=config.SMA_LONG).mean().iloc[-1]) if len(close) >= config.SMA_LONG else current_price

        if current_price > sma_long and sma_short > sma_long:
            sma_bonus = 10
            signals.append("SMA → Güçlü Yukarı Trend (Fiyat > SMA20 > SMA50)")
        elif current_price > sma_long:
            sma_bonus = 5
            signals.append("SMA → Yukarı Trend")
        elif current_price < sma_long:
            sma_bonus = -5
            signals.append("SMA → Aşağı Trend")
        else:
            sma_bonus = 0

        score += sma_bonus

        # --- Momentum Analizi (max ±10 puan) ---
        momentum = calculate_momentum(close, 10)
        if momentum > 5:
            mom_bonus = 10
            signals.append(f"Momentum → Güçlü Pozitif ({momentum:+.1f}%)")
        elif momentum > 0:
            mom_bonus = 5
            signals.append(f"Momentum → Pozitif ({momentum:+.1f}%)")
        elif momentum < -5:
            mom_bonus = -10
            signals.append(f"Momentum → Güçlü Negatif ({momentum:+.1f}%)")
        elif momentum < 0:
            mom_bonus = -3
            signals.append(f"Momentum → Negatif ({momentum:+.1f}%)")
        else:
            mom_bonus = 0

        score += mom_bonus

        # Skoru 0-100 arası sınırla
        score = max(0, min(100, score))

        # Fibonacci
        fib = calculate_fibonacci_levels(df)

        return {
            "score": round(score, 1),
            "rsi": round(current_rsi, 1),
            "macd_histogram": round(hist_current, 4),
            "bollinger_position": "alt" if current_price < lower else ("üst" if current_price > upper else "orta"),
            "momentum_pct": round(momentum, 2),
            "sma_short": round(sma_short, 2),
            "sma_long": round(sma_long, 2),
            "fibonacci": fib,
            "signals": signals,
            "current_price": round(current_price, 2)
        }

    except Exception as e:
        print(f"Score hesaplama hatası: {e}")
        return {
            "score": 0,
            "rsi": 50,
            "macd_histogram": 0,
            "bollinger_position": "unknown",
            "momentum_pct": 0,
            "sma_short": 0,
            "sma_long": 0,
            "fibonacci": {},
            "signals": [f"Hata: {str(e)}"],
            "current_price": 0
        }


def analyze_stock(ticker: str) -> dict:
    """Bir hisse için tam teknik analiz yapar."""
    print(f"  📈 {ticker} analiz edildi...")
    df = download_stock_data(ticker, period_days=200)

    if df.empty:
        return {
            "ticker": ticker,
            "score": 0,
            "error": "Veri bulunamadı",
            "rsi": 0,
            "macd_histogram": 0,
            "bollinger_position": "unknown",
            "momentum_pct": 0,
            "sma_short": 0,
            "sma_long": 0,
            "fibonacci": {},
            "signals": [],
            "current_price": 0,
            "dataframe": pd.DataFrame()
        }

    result = score_technical(df)
    result["ticker"] = ticker
    result["dataframe"] = df  # Grafik için sakla

    return result


def analyze_all_stocks(tickers: list = None) -> list:
    """
    Tüm hisseleri analiz eder.
    Döndürür: Score'a göre sıralanmış analiz listesi
    """
    if tickers is None:
        tickers = config.ALL_STOCKS

    print(f"\n📊 {len(tickers)} hisse analiz başlıyor...\n")

    results = []
    error_count = 0
    success_count = 0

    for ticker in tickers:
        try:
            result = analyze_stock(ticker)
            results.append(result)
            
            if result.get("error"):
                error_count += 1
            else:
                success_count += 1
                
        except Exception as e:
            print(f"  ❌ {ticker} hatası: {e}")
            error_count += 1
            results.append({
                "ticker": ticker,
                "score": 0,
                "error": str(e)
            })

    print(f"\n✅ Başarılı: {success_count} | ❌ Hata: {error_count}")

    # Score'a göre azalan sıra
    results.sort(key=lambda x: x.get("score", 0), reverse=True)

    return results


if __name__ == "__main__":
    # Test: Sadece 3 hisse analiz et
    test_tickers = ["THYAO.IS", "AAPL", "NVDA"]
    results = analyze_all_stocks(test_tickers)

    print("\n\n📋 SONUÇLAR:")
    print("=" * 60)
    for r in results:
        print(f"\n🏷️  {r['ticker']}")
        print(f"   Skor: {r.get('score', 0)}/100")
        print(f"   Fiyat: {r.get('current_price', 'N/A')}")
        if "signals" in r:
            for sig in r["signals"][:3]:
                print(f"   → {sig}")
        if "fibonacci" in r and r['fibonacci']:
            print(f"   Fibonacci: {r['fibonacci']}")
