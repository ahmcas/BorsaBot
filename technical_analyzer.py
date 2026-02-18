# ============================================================
# technical_analyzer.py — Teknik Analiz Engine (v3 - FIXED)
# ============================================================

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import config

try:
    import requests
except:
    import subprocess
    subprocess.run(["pip", "install", "requests"], check=True)
    import requests


def normalize_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    DataFrame'in standart formatta olmasını sağla.
    Tüm kaynakların çıktısı tutarlı olsun.
    """
    try:
        if df.empty:
            return pd.DataFrame()
        
        # Column names'i normalize et
        df.columns = df.columns.str.strip().str.title()
        
        # Multi-index column'ları flatten et
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        
        # Gerekli sütunlar
        required_cols = ["Open", "High", "Low", "Close", "Volume"]
        
        # Eğer sütunlar yoksa, kontrol et ve rename et
        for col in df.columns:
            col_lower = col.lower()
            if "open" in col_lower and "Open" not in df.columns:
                df.rename(columns={col: "Open"}, inplace=True)
            elif "high" in col_lower and "High" not in df.columns:
                df.rename(columns={col: "High"}, inplace=True)
            elif "low" in col_lower and "Low" not in df.columns:
                df.rename(columns={col: "Low"}, inplace=True)
            elif "close" in col_lower and "Close" not in df.columns:
                df.rename(columns={col: "Close"}, inplace=True)
            elif "volume" in col_lower and "Volume" not in df.columns:
                df.rename(columns={col: "Volume"}, inplace=True)
        
        # Sadece gerekli sütunları tut
        available_cols = [col for col in required_cols if col in df.columns]
        if not available_cols:
            return pd.DataFrame()
        
        df = df[available_cols].copy()
        
        # Data types kontrol et
        for col in ["Open", "High", "Low", "Close", "Volume"]:
            if col in df.columns:
                try:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
                except:
                    pass
        
        # NaN values'leri doldur
        df = df.fillna(method='ffill').fillna(method='bfill')
        
        # Boş satırları sil
        df = df.dropna()
        
        if df.empty:
            return pd.DataFrame()
        
        # Index'i kontrol et (DateTime olmalı)
        if not isinstance(df.index, pd.DatetimeIndex):
            try:
                df.index = pd.to_datetime(df.index)
            except:
                pass
        
        return df
        
    except Exception as e:
        print(f"  [ERROR] DataFrame normalize hatası: {e}")
        return pd.DataFrame()


def download_from_yahoo(ticker: str, period_days: int = 200) -> pd.DataFrame:
    """Yahoo Finance'ten veri çek"""
    try:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=period_days)
        
        df = yf.download(
            ticker,
            start=start_date.strftime("%Y-%m-%d"),
            end=end_date.strftime("%Y-%m-%d"),
            progress=False,
            auto_adjust=True
        )
        
        if df.empty:
            return pd.DataFrame()
        
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        
        return df
    except:
        return pd.DataFrame()


def download_from_alpha_vantage(ticker: str, period_days: int = 200) -> pd.DataFrame:
    """Alpha Vantage'den veri çek"""
    try:
        api_key = config.ALPHA_VANTAGE_KEY
        if not api_key or api_key == "YOUR_ALPHA_VANTAGE_KEY_HERE":
            return pd.DataFrame()
        
        # Türkçe hisse sembolleri için format değişikliği
        symbol = ticker.replace(".IS", "")
        
        url = f"https://www.alphavantage.co/query"
        params = {
            "function": "TIME_SERIES_DAILY",
            "symbol": symbol,
            "apikey": api_key,
            "outputsize": "full"
        }
        
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        if "Time Series (Daily)" not in data:
            return pd.DataFrame()
        
        ts = data["Time Series (Daily)"]
        dates = []
        opens = []
        highs = []
        lows = []
        closes = []
        volumes = []
        
        for date, values in sorted(ts.items())[-period_days:]:
            try:
                dates.append(pd.to_datetime(date))
                opens.append(float(values["1. open"]))
                highs.append(float(values["2. high"]))
                lows.append(float(values["3. low"]))
                closes.append(float(values["4. close"]))
                volumes.append(float(values["6. volume"]))
            except:
                continue
        
        if not closes:
            return pd.DataFrame()
        
        df = pd.DataFrame({
            "Open": opens,
            "High": highs,
            "Low": lows,
            "Close": closes,
            "Volume": volumes
        }, index=dates)
        
        return df
    except:
        return pd.DataFrame()


def download_from_iex(ticker: str, period_days: int = 200) -> pd.DataFrame:
    """IEX Cloud'dan veri çek"""
    try:
        api_key = config.IEX_API_KEY
        
        symbol = ticker.replace(".IS", "")
        
        url = f"https://cloud.iexapis.com/stable/stock/{symbol}/chart/1y"
        params = {"token": api_key}
        
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        if not data or isinstance(data, dict) and "message" in data:
            return pd.DataFrame()
        
        dates = []
        opens = []
        highs = []
        lows = []
        closes = []
        volumes = []
        
        for candle in data[-period_days:]:
            try:
                dates.append(pd.to_datetime(candle["date"]))
                opens.append(float(candle.get("open", 0)) or 0)
                highs.append(float(candle.get("high", 0)) or 0)
                lows.append(float(candle.get("low", 0)) or 0)
                closes.append(float(candle.get("close", 0)) or 0)
                volumes.append(float(candle.get("volume", 0)) or 0)
            except:
                continue
        
        if not closes:
            return pd.DataFrame()
        
        df = pd.DataFrame({
            "Open": opens,
            "High": highs,
            "Low": lows,
            "Close": closes,
            "Volume": volumes
        }, index=dates)
        
        return df
    except:
        return pd.DataFrame()


def download_from_polygon(ticker: str, period_days: int = 200) -> pd.DataFrame:
    """Polygon.io'dan veri çek"""
    try:
        api_key = config.POLYGON_API_KEY
        
        if ticker.endswith(".IS"):
            return pd.DataFrame()
        
        symbol = ticker
        url = f"https://api.polygon.io/v2/aggs/ticker/{symbol}/range/1/day"
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=period_days)
        
        params = {
            "from": start_date.strftime("%Y-%m-%d"),
            "to": end_date.strftime("%Y-%m-%d"),
            "apiKey": api_key
        }
        
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        if "results" not in data:
            return pd.DataFrame()
        
        dates = []
        opens = []
        highs = []
        lows = []
        closes = []
        volumes = []
        
        for agg in data["results"]:
            try:
                dates.append(pd.to_datetime(agg["t"], unit="ms"))
                opens.append(float(agg.get("o", 0)) or 0)
                highs.append(float(agg.get("h", 0)) or 0)
                lows.append(float(agg.get("l", 0)) or 0)
                closes.append(float(agg.get("c", 0)) or 0)
                volumes.append(float(agg.get("v", 0)) or 0)
            except:
                continue
        
        if not closes:
            return pd.DataFrame()
        
        df = pd.DataFrame({
            "Open": opens,
            "High": highs,
            "Low": lows,
            "Close": closes,
            "Volume": volumes
        }, index=dates)
        
        return df
    except:
        return pd.DataFrame()


def download_stock_data(ticker: str, period_days: int = 200) -> pd.DataFrame:
    """
    Çoklu kaynaklardan veri çek. DataFrame'in standart formatı kontrol et.
    """
    
    sources = [
        ("Yahoo Finance", lambda: download_from_yahoo(ticker, period_days)),
        ("Alpha Vantage", lambda: download_from_alpha_vantage(ticker, period_days)),
        ("IEX Cloud", lambda: download_from_iex(ticker, period_days)),
        ("Polygon.io", lambda: download_from_polygon(ticker, period_days)),
    ]
    
    for source_name, source_func in sources:
        try:
            df = source_func()
            
            if df.empty:
                continue
            
            # DataFrame'i normalize et
            df = normalize_dataframe(df)
            
            if df.empty or len(df) < 60:
                continue
            
            print(f"  📊 {ticker} - {source_name} ✅")
            return df
            
        except Exception as e:
            pass
    
    print(f"  ❌ {ticker} - Hiçbir kaynaktan veri alınamadı")
    return pd.DataFrame()


def calculate_rsi(prices: pd.Series, period: int = 14) -> pd.Series:
    """RSI (Relative Strength Index) hesapla"""
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
        return pd.Series([50] * len(prices))


def calculate_macd(prices: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> dict:
    """MACD hesapla"""
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
        return {
            "macd_line": pd.Series([0] * len(prices)),
            "signal_line": pd.Series([0] * len(prices)),
            "histogram": pd.Series([0] * len(prices))
        }


def calculate_bollinger_bands(prices: pd.Series, period: int = 20, std_dev: float = 2.0) -> dict:
    """Bollinger Bands hesapla"""
    try:
        sma = prices.rolling(window=period).mean()
        std = prices.rolling(window=period).std()

        return {
            "upper": sma + (std * std_dev),
            "middle": sma,
            "lower": sma - (std * std_dev)
        }
    except Exception as e:
        return {
            "upper": prices,
            "middle": prices,
            "lower": prices
        }


def calculate_fibonacci_levels(df: pd.DataFrame, lookback: int = 60) -> dict:
    """
    Son 60 gün içinde Fibonacci destek/direnç seviyelerini hesapla.
    """
    try:
        if df.empty:
            return {}
        
        recent = df.tail(lookback)
        if recent.empty or len(recent) < 20:
            return {}
        
        # High ve Low'u doğru şekilde al
        try:
            high = float(recent["High"].max())
            low = float(recent["Low"].min())
        except:
            try:
                high = float(recent.iloc[:, 1].max())  # High genellikle 2. sütun
                low = float(recent.iloc[:, 2].min())   # Low genellikle 3. sütun
            except:
                return {}
        
        # Kontrol et
        if high <= 0 or low <= 0 or high <= low:
            return {}
        
        diff = high - low
        
        if diff <= 0:
            return {}
        
        # Fibonacci seviyeleri hesapla
        levels = {}
        
        for level in config.FIBONACCI_LEVELS:
            try:
                fib_value = low + (diff * level)
                if fib_value > 0:
                    levels[f"fib_{level}"] = round(fib_value, 2)
            except:
                continue
        
        # Mevcut fiyat
        try:
            current = float(df["Close"].iloc[-1])
        except:
            try:
                current = float(df.iloc[-1, 3])
            except:
                current = (high + low) / 2
        
        levels["high"] = round(high, 2)
        levels["low"] = round(low, 2)
        levels["current"] = round(current, 2)
        
        return levels
        
    except Exception as e:
        return {}


def calculate_momentum(prices: pd.Series, period: int = 10) -> float:
    """Momentum hesapla: Son N gün fiyat değişimi (yüzde)"""
    try:
        if len(prices) < period:
            return 0.0
        
        current = float(prices.iloc[-1])
        past = float(prices.iloc[-period])
        
        if past == 0:
            return 0.0
        
        return float((current - past) / past * 100)
    except Exception as e:
        return 0.0


def score_technical(df: pd.DataFrame) -> dict:
    """
    Bir hisse için teknik skor hesaplar (0-100 arası).
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
            "fibonacci": {
                "fib_0.236": 0,
                "fib_0.382": 0,
                "fib_0.500": 0,
                "fib_0.618": 0,
                "fib_0.786": 0,
                "high": 0,
                "low": 0,
                "current": 0
            },
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
            signals.append("MACD ��� Bullish Crossover (Alım Sinyali)")
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

        # Fibonacci - Kontrollü hesaplama
        try:
            fib = calculate_fibonacci_levels(df)
            
            # Fibonacci valid mi kontrol et
            if fib and len(fib) >= 5:
                # Tüm level'lar var mı kontrol et
                required_levels = ["fib_0.236", "fib_0.382", "fib_0.500", "fib_0.618", "fib_0.786"]
                for level in required_levels:
                    if level not in fib:
                        fib[level] = 0  # Eksik olanları 0 ile doldur
            else:
                fib = {
                    "fib_0.236": 0,
                    "fib_0.382": 0,
                    "fib_0.500": 0,
                    "fib_0.618": 0,
                    "fib_0.786": 0,
                    "high": 0,
                    "low": 0,
                    "current": current_price
                }
        except:
            fib = {
                "fib_0.236": 0,
                "fib_0.382": 0,
                "fib_0.500": 0,
                "fib_0.618": 0,
                "fib_0.786": 0,
                "high": 0,
                "low": 0,
                "current": current_price
            }

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
        print(f"[ERROR] Score hesaplama hatası: {e}")
        return {
            "score": 0,
            "rsi": 50,
            "macd_histogram": 0,
            "bollinger_position": "unknown",
            "momentum_pct": 0,
            "sma_short": 0,
            "sma_long": 0,
            "fibonacci": {
                "fib_0.236": 0,
                "fib_0.382": 0,
                "fib_0.500": 0,
                "fib_0.618": 0,
                "fib_0.786": 0,
                "high": 0,
                "low": 0,
                "current": 0
            },
            "signals": [f"Hata: {str(e)}"],
            "current_price": 0
        }


def analyze_stock(ticker: str) -> dict:
    """Bir hisse için tam teknik analiz yapar."""
    df = download_stock_data(ticker, period_days=200)

    if df.empty:
        return {
            "ticker": ticker,
            "score": 0,
            "error": "Veri bulunamadı",
            "skip": True,
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
    result["skip"] = False

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

    for i, ticker in enumerate(tickers, 1):
        try:
            result = analyze_stock(ticker)
            results.append(result)
            
            if result.get("skip"):
                error_count += 1
                print(f"[{i:3d}/{len(tickers)}] ⏭️  {ticker}")
            else:
                success_count += 1
                score = result.get("score", 0)
                print(f"[{i:3d}/{len(tickers)}] ✅ {ticker} - Skor: {score:.1f}")
                
        except Exception as e:
            print(f"[{i:3d}/{len(tickers)}] ❌ {ticker} - Hata")
            error_count += 1
            results.append({
                "ticker": ticker,
                "score": 0,
                "error": str(e),
                "skip": True
            })

    print(f"\n✅ Başarılı: {success_count} | ⏭️  Geçildi: {error_count}")

    # Score'a göre azalan sıra
    results.sort(key=lambda x: x.get("score", 0), reverse=True)

    return results


if __name__ == "__main__":
    # Test: Sadece 3 hisse analiz et
    test_tickers = ["AKBANK.IS", "GARAN.IS", "AAPL"]
    results = analyze_all_stocks(test_tickers)

    print("\n\n📋 SONUÇLAR:")
    print("=" * 70)
    for r in results:
        if not r.get("skip"):
            print(f"\n🏷️  {r['ticker']}")
            print(f"   Skor: {r.get('score', 0)}/100")
            print(f"   Fiyat: {r.get('current_price', 'N/A')}")
            print(f"   RSI: {r.get('rsi', 'N/A')}")
            if "signals" in r:
                for sig in r["signals"][:3]:
                    print(f"   → {sig}")
            if "fibonacci" in r and r['fibonacci']:
                fib = r['fibonacci']
                print(f"   Fibonacci: High={fib.get('high', 0)}, Low={fib.get('low', 0)}")
                print(f"              0.500={fib.get('fib_0.500', 0)}, 0.618={fib.get('fib_0.618', 0)}")
