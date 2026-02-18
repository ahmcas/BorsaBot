# ============================================================
# technical_analyzer.py — Teknik Analiz Engine (v3 - KOMPLE FINAL)
# ============================================================

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

try:
    import yfinance as yf
except:
    import subprocess
    subprocess.run(["pip", "install", "yfinance"], check=True)
    import yfinance as yf

import config


class TechnicalAnalyzer:
    """Teknik Analiz - RSI, MACD, Bollinger, SMA, Fibonacci"""
    
    @staticmethod
    def get_historical_data(ticker: str, period: str = "200d") -> pd.DataFrame:
        """Tarihi veri çek"""
        try:
            df = yf.download(ticker, period=period, progress=False, timeout=30)
            
            if df.empty:
                return None
            
            # İngilizce sütun adları
            df.columns = [col.replace(' ', '').lower() for col in df.columns]
            
            # Gerekli sütunlar kontrol et
            required_cols = ['close', 'high', 'low', 'volume']
            if not all(col in df.columns for col in required_cols):
                return None
            
            return df
            
        except Exception as e:
            print(f"[ERROR] Veri çekme hatası ({ticker}): {e}")
            return None
    
    @staticmethod
    def calculate_rsi(prices: pd.Series, period: int = 14) -> float:
        """RSI (Relative Strength Index) hesapla"""
        try:
            if len(prices) < period:
                return None
            
            delta = prices.diff()
            gain = delta.where(delta > 0, 0.0)
            loss = (-delta).where(delta < 0, 0.0)
            
            avg_gain = gain.rolling(window=period).mean()
            avg_loss = loss.rolling(window=period).mean()
            
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))
            
            return round(float(rsi.iloc[-1]), 2)
            
        except Exception as e:
            return None
    
    @staticmethod
    def calculate_macd(prices: pd.Series) -> dict:
        """MACD hesapla"""
        try:
            exp1 = prices.ewm(span=config.MACD_FAST, adjust=False).mean()
            exp2 = prices.ewm(span=config.MACD_SLOW, adjust=False).mean()
            
            macd_line = exp1 - exp2
            signal_line = macd_line.ewm(span=config.MACD_SIGNAL, adjust=False).mean()
            histogram = macd_line - signal_line
            
            return {
                "macd_line": round(float(macd_line.iloc[-1]), 6),
                "signal_line": round(float(signal_line.iloc[-1]), 6),
                "histogram": round(float(histogram.iloc[-1]), 6)
            }
            
        except Exception as e:
            return {"macd_line": None, "signal_line": None, "histogram": None}
    
    @staticmethod
    def calculate_bollinger_bands(prices: pd.Series, period: int = 20, std_dev: float = 2.0) -> dict:
        """Bollinger Bands hesapla"""
        try:
            sma = prices.rolling(window=period).mean()
            std = prices.rolling(window=period).std()
            
            upper_band = sma + (std_dev * std)
            lower_band = sma - (std_dev * std)
            
            current_price = prices.iloc[-1]
            
            # Pozisyon belirle
            if current_price > upper_band.iloc[-1]:
                position = "üst"
            elif current_price < lower_band.iloc[-1]:
                position = "alt"
            else:
                position = "orta"
            
            return {
                "upper_band": round(float(upper_band.iloc[-1]), 2),
                "middle_band": round(float(sma.iloc[-1]), 2),
                "lower_band": round(float(lower_band.iloc[-1]), 2),
                "position": position
            }
            
        except Exception as e:
            return {
                "upper_band": None,
                "middle_band": None,
                "lower_band": None,
                "position": None
            }
    
    @staticmethod
    def calculate_sma(prices: pd.Series, period: int) -> float:
        """Simple Moving Average hesapla"""
        try:
            if len(prices) < period:
                return None
            
            sma = prices.rolling(window=period).mean()
            return round(float(sma.iloc[-1]), 2)
            
        except Exception as e:
            return None
    
    @staticmethod
    def calculate_momentum(prices: pd.Series, period: int = 10) -> float:
        """Momentum hesapla (% değişim)"""
        try:
            if len(prices) < period:
                return None
            
            momentum = ((prices.iloc[-1] - prices.iloc[-period]) / prices.iloc[-period]) * 100
            return round(float(momentum), 2)
            
        except Exception as e:
            return None
    
    @staticmethod
    def calculate_fibonacci(df: pd.DataFrame, lookback: int = 60) -> dict:
        """Fibonacci Retracement hesapla"""
        try:
            high = df["high"].tail(lookback).max()
            low = df["low"].tail(lookback).min()
            current = df["close"].iloc[-1]
            
            distance = high - low
            
            fib_levels = {}
            for level in config.FIBONACCI_LEVELS:
                fib_levels[f"fib_{level}"] = round(high - (distance * level), 2)
            
            return {
                "current": round(current, 2),
                "high": round(high, 2),
                "low": round(low, 2),
                **fib_levels
            }
            
        except Exception as e:
            return {}
    
    @staticmethod
    def generate_signals(rsi: float, macd: dict, bollinger: dict, sma_short: float, 
                        sma_long: float, momentum: float, current_price: float) -> list:
        """Teknik sinyaller oluştur"""
        signals = []
        
        try:
            # RSI Sinyalleri
            if rsi and rsi < 30:
                signals.append(f"📊 RSI {rsi} → Oversold (Al sinyali)")
            elif rsi and rsi > 70:
                signals.append(f"📊 RSI {rsi} → Overbought (Sat sinyali)")
            
            # MACD Sinyalleri
            if macd.get("histogram"):
                if macd["histogram"] > 0 and macd["macd_line"] > macd["signal_line"]:
                    signals.append("📈 MACD → Bullish (Yukarı kesişim)")
                elif macd["histogram"] < 0 and macd["macd_line"] < macd["signal_line"]:
                    signals.append("📉 MACD → Bearish (Aşağı kesişim)")
            
            # Bollinger Bands Sinyalleri
            if bollinger.get("position"):
                if bollinger["position"] == "alt":
                    signals.append(f"📊 Bollinger → Alt bant yaklaştı (Al)")
                elif bollinger["position"] == "üst":
                    signals.append(f"📊 Bollinger → Üst bant yaklaştı (Sat)")
            
            # SMA Sinyalleri
            if sma_short and sma_long and current_price:
                if current_price > sma_short > sma_long:
                    signals.append(f"📈 SMA → Bullish (Fiyat > SMA20 > SMA50)")
                elif current_price < sma_short < sma_long:
                    signals.append(f"📉 SMA → Bearish (Fiyat < SMA20 < SMA50)")
            
            # Momentum Sinyalleri
            if momentum:
                if momentum > 5:
                    signals.append(f"📈 Momentum → Güçlü yukarı ({momentum:+.1f}%)")
                elif momentum < -5:
                    signals.append(f"📉 Momentum → Güçlü aşağı ({momentum:+.1f}%)")
            
            return signals if signals else ["⚪ Açık sinyal yok"]
            
        except Exception as e:
            return ["⚠️ Sinyal oluşturma hatası"]
    
    @staticmethod
    def calculate_technical_score(rsi: float, macd: dict, bollinger: dict, 
                                 sma_short: float, sma_long: float, 
                                 momentum: float, current_price: float) -> float:
        """Teknik skor hesapla (0-100)"""
        try:
            score = 50  # Başlangıç
            
            # RSI kontribüsyonu (-15 ile +15)
            if rsi:
                if rsi < 30:
                    score += 10
                elif rsi < 40:
                    score += 5
                elif rsi > 70:
                    score -= 10
                elif rsi > 60:
                    score -= 5
            
            # MACD kontribüsyonu (-10 ile +10)
            if macd.get("histogram"):
                if macd["histogram"] > 0:
                    score += 5
                else:
                    score -= 5
            
            # Bollinger kontribüsyonu (-10 ile +10)
            if bollinger.get("position"):
                if bollinger["position"] == "alt":
                    score += 8
                elif bollinger["position"] == "üst":
                    score -= 8
            
            # SMA kontribüsyonu (-15 ile +15)
            if sma_short and sma_long and current_price:
                if current_price > sma_short > sma_long:
                    score += 10
                elif current_price < sma_short < sma_long:
                    score -= 10
                elif current_price > sma_short:
                    score += 5
                elif current_price < sma_short:
                    score -= 5
            
            # Momentum kontribüsyonu (-15 ile +15)
            if momentum:
                if momentum > 10:
                    score += 10
                elif momentum > 0:
                    score += 5
                elif momentum < -10:
                    score -= 10
                elif momentum < 0:
                    score -= 5
            
            # 0-100 arasında sınırla
            score = max(0, min(100, score))
            
            return round(score, 1)
            
        except Exception as e:
            return 50.0


def analyze_all_stocks(ticker_list: list) -> list:
    """Tüm hisseleri analiz et"""
    print(f"\n📊 Teknik analiz başlıyor ({len(ticker_list)} hisse)...")
    
    results = []
    
    for ticker in ticker_list:
        try:
            # Veri çek
            df = TechnicalAnalyzer.get_historical_data(ticker, period=f"{config.LOOKBACK_DAYS}d")
            
            if df is None or df.empty:
                results.append({
                    "ticker": ticker,
                    "skip": True,
                    "reason": "Veri alınamadı"
                })
                continue
            
            close = df["close"].squeeze()
            
            # Teknik göstergeler hesapla
            rsi = TechnicalAnalyzer.calculate_rsi(close, config.RSI_PERIOD)
            macd = TechnicalAnalyzer.calculate_macd(close)
            bollinger = TechnicalAnalyzer.calculate_bollinger_bands(close, config.BOLLINGER_PERIOD, config.BOLLINGER_STD_DEV)
            sma_short = TechnicalAnalyzer.calculate_sma(close, config.SMA_SHORT)
            sma_long = TechnicalAnalyzer.calculate_sma(close, config.SMA_LONG)
            momentum = TechnicalAnalyzer.calculate_momentum(close, 10)
            fibonacci = TechnicalAnalyzer.calculate_fibonacci(df, config.FIBONACCI_LOOKBACK)
            
            # Mevcut fiyat
            current_price = float(close.iloc[-1])
            
            # Sinyaller oluştur
            signals = TechnicalAnalyzer.generate_signals(
                rsi, macd, bollinger, sma_short, sma_long, momentum, current_price
            )
            
            # Skor hesapla
            technical_score = TechnicalAnalyzer.calculate_technical_score(
                rsi, macd, bollinger, sma_short, sma_long, momentum, current_price
            )
            
            # Sonuç
            result = {
                "ticker": ticker,
                "skip": False,
                "current_price": current_price,
                "score": technical_score,
                "rsi": rsi,
                "macd_histogram": macd.get("histogram"),
                "bollinger_position": bollinger.get("position"),
                "sma_short": sma_short,
                "sma_long": sma_long,
                "momentum_pct": momentum,
                "signals": signals,
                "fibonacci": fibonacci,
                "dataframe": df
            }
            
            results.append(result)
            
        except Exception as e:
            print(f"⚠️  {ticker}: {str(e)[:50]}")
            results.append({
                "ticker": ticker,
                "skip": True,
                "reason": str(e)[:100]
            })
    
    # Başarılı analiz sayısı
    successful = len([r for r in results if not r.get("skip")])
    print(f"✅ {successful}/{len(ticker_list)} hisse başarıyla analiz edildi")
    
    return results


if __name__ == "__main__":
    print("🧪 Technical Analyzer Testi")
    print("=" * 50)
    
    # Test
    test_stocks = ["AKBANK.IS", "AAPL"]
    results = analyze_all_stocks(test_stocks)
    
    print("\n📊 Sonuçlar:")
    for result in results:
        if not result.get("skip"):
            print(f"\n{result['ticker']}")
            print(f"  Skor: {result['score']}")
            print(f"  RSI: {result['rsi']}")
            print(f"  Momentum: {result['momentum_pct']:+.2f}%")
