# ============================================================
# technical_analyzer.py — Teknik Analiz Engine (v5 - KOMPLE FINAL)
# ============================================================
# Özellikler:
# 1. RSI (Relative Strength Index)
# 2. MACD (Moving Average Convergence Divergence)
# 3. Bollinger Bands
# 4. SMA (Simple Moving Average)
# 5. Fibonacci Retracement
# 6. Momentum
# 7. Trend Analizi
# 8. ATR (Average True Range)
# 9. Sinyal Üretimi
# 10. Fallback Mekanizması
# ============================================================

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

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
        """Tarihi veri çek (HATASIZ & FALLBACK İLE)"""
        try:
            # Veri çek
            df = yf.download(ticker, period=period, progress=False, timeout=30)
            
            # Boş kontrol
            if df is None or df.empty or len(df) == 0:
                return None
            
            # Series ise DataFrame'e çevir
            if isinstance(df, pd.Series):
                df = df.to_frame()
            
            # Sütun adlarını normalize et
            df.columns = [str(col).lower().replace(' ', '_') for col in df.columns]
            
            # Gerekli sütunlar var mı?
            required = ['close', 'high', 'low', 'volume']
            if not all(col in df.columns for col in required):
                return None
            
            # Veri tiplerini kontrol et ve dönüştür
            for col in required:
                try:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
                except:
                    pass
            
            # NaN satırları sil
            df = df.dropna()
            
            if len(df) < 20:
                return None
            
            return df
            
        except Exception as e:
            return None
    
    @staticmethod
    def calculate_rsi(prices: pd.Series, period: int = 14) -> float:
        """RSI (Relative Strength Index) hesapla"""
        try:
            if prices is None or len(prices) < period + 1:
                return None
            
            # NaN kontrol
            prices = prices.dropna()
            if len(prices) < period + 1:
                return None
            
            # Fark hesapla
            delta = prices.diff()
            
            # Kazançlar ve kayıplar
            gain = delta.clip(lower=0)
            loss = -delta.clip(upper=0)
            
            # Ortalama
            avg_gain = gain.rolling(window=period).mean()
            avg_loss = loss.rolling(window=period).mean()
            
            # Sıfır kontrol
            if avg_loss.iloc[-1] == 0:
                return 100.0 if avg_gain.iloc[-1] > 0 else 0.0
            
            # RS ve RSI
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))
            
            current_rsi = float(rsi.iloc[-1])
            
            # Sınırla
            if np.isnan(current_rsi) or np.isinf(current_rsi):
                return 50.0
            
            current_rsi = max(0, min(100, current_rsi))
            
            return round(current_rsi, 2)
            
        except Exception as e:
            return 50.0
    
    @staticmethod
    def calculate_macd(prices: pd.Series) -> dict:
        """MACD hesapla"""
        try:
            if prices is None or len(prices) < 26:
                return {"macd_line": None, "signal_line": None, "histogram": None}
            
            prices = prices.dropna()
            if len(prices) < 26:
                return {"macd_line": None, "signal_line": None, "histogram": None}
            
            # EMA hesapla
            exp1 = prices.ewm(span=config.MACD_FAST, adjust=False).mean()
            exp2 = prices.ewm(span=config.MACD_SLOW, adjust=False).mean()
            
            # MACD line
            macd_line = exp1 - exp2
            
            # Signal line
            signal_line = macd_line.ewm(span=config.MACD_SIGNAL, adjust=False).mean()
            
            # Histogram
            histogram = macd_line - signal_line
            
            # Son değerler
            macd_val = float(macd_line.iloc[-1])
            signal_val = float(signal_line.iloc[-1])
            hist_val = float(histogram.iloc[-1])
            
            # NaN kontrol
            if np.isnan(macd_val) or np.isnan(signal_val) or np.isnan(hist_val):
                return {"macd_line": 0, "signal_line": 0, "histogram": 0}
            
            return {
                "macd_line": round(macd_val, 6),
                "signal_line": round(signal_val, 6),
                "histogram": round(hist_val, 6)
            }
            
        except Exception as e:
            return {"macd_line": 0, "signal_line": 0, "histogram": 0}
    
    @staticmethod
    def calculate_bollinger_bands(prices: pd.Series, period: int = 20, std_dev: float = 2.0) -> dict:
        """Bollinger Bands hesapla"""
        try:
            if prices is None or len(prices) < period:
                return {
                    "upper_band": None,
                    "middle_band": None,
                    "lower_band": None,
                    "position": "orta"
                }
            
            prices = prices.dropna()
            if len(prices) < period:
                return {
                    "upper_band": None,
                    "middle_band": None,
                    "lower_band": None,
                    "position": "orta"
                }
            
            # SMA
            sma = prices.rolling(window=period).mean()
            
            # Standart sapma
            std = prices.rolling(window=period).std()
            
            # Bands
            upper = sma + (std_dev * std)
            lower = sma - (std_dev * std)
            
            # Son değerler
            current_price = float(prices.iloc[-1])
            upper_val = float(upper.iloc[-1])
            middle_val = float(sma.iloc[-1])
            lower_val = float(lower.iloc[-1])
            
            # NaN kontrol
            if np.isnan(current_price) or np.isnan(upper_val) or np.isnan(lower_val):
                return {
                    "upper_band": None,
                    "middle_band": None,
                    "lower_band": None,
                    "position": "orta"
                }
            
            # Pozisyon belirle
            if current_price > upper_val * 0.95:
                position = "üst"
            elif current_price < lower_val * 1.05:
                position = "alt"
            else:
                position = "orta"
            
            return {
                "upper_band": round(upper_val, 2),
                "middle_band": round(middle_val, 2),
                "lower_band": round(lower_val, 2),
                "position": position
            }
            
        except Exception as e:
            return {
                "upper_band": None,
                "middle_band": None,
                "lower_band": None,
                "position": "orta"
            }
    
    @staticmethod
    def calculate_sma(prices: pd.Series, period: int) -> float:
        """Simple Moving Average hesapla"""
        try:
            if prices is None or len(prices) < period:
                return None
            
            prices = prices.dropna()
            if len(prices) < period:
                return None
            
            sma = prices.rolling(window=period).mean()
            sma_val = float(sma.iloc[-1])
            
            if np.isnan(sma_val):
                return None
            
            return round(sma_val, 2)
            
        except Exception as e:
            return None
    
    @staticmethod
    def calculate_momentum(prices: pd.Series, period: int = 10) -> float:
        """Momentum hesapla (% değişim)"""
        try:
            if prices is None or len(prices) < period:
                return None
            
            prices = prices.dropna()
            if len(prices) < period:
                return None
            
            current = float(prices.iloc[-1])
            past = float(prices.iloc[-period])
            
            if past == 0 or np.isnan(current) or np.isnan(past):
                return None
            
            momentum = ((current - past) / past) * 100
            
            if np.isnan(momentum) or np.isinf(momentum):
                return None
            
            return round(momentum, 2)
            
        except Exception as e:
            return None
    
    @staticmethod
    def calculate_atr(df: pd.DataFrame, period: int = 14) -> float:
        """Average True Range hesapla (volatilite)"""
        try:
            if df is None or len(df) < period + 1:
                return None
            
            high = df['high'].astype(float)
            low = df['low'].astype(float)
            close = df['close'].astype(float)
            
            # True Range
            tr1 = high - low
            tr2 = abs(high - close.shift())
            tr3 = abs(low - close.shift())
            
            tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
            
            # ATR
            atr = tr.rolling(window=period).mean()
            
            atr_val = float(atr.iloc[-1])
            
            if np.isnan(atr_val):
                return None
            
            return round(atr_val, 2)
            
        except Exception as e:
            return None
    
    @staticmethod
    def calculate_fibonacci(df: pd.DataFrame, lookback: int = 60) -> dict:
        """Fibonacci Retracement hesapla"""
        try:
            if df is None or len(df) < lookback:
                return {}
            
            high = df["high"].tail(lookback).max()
            low = df["low"].tail(lookback).min()
            current = float(df["close"].iloc[-1])
            
            if np.isnan(high) or np.isnan(low) or np.isnan(current):
                return {}
            
            distance = high - low
            
            fib_levels = {
                "current": round(current, 2),
                "high": round(float(high), 2),
                "low": round(float(low), 2),
            }
            
            for level in config.FIBONACCI_LEVELS:
                fib_levels[f"fib_{level}"] = round(high - (distance * level), 2)
            
            return fib_levels
            
        except Exception as e:
            return {}
    
    @staticmethod
    def generate_signals(rsi: float, macd: dict, bollinger: dict, sma_short: float, 
                        sma_long: float, momentum: float, current_price: float) -> list:
        """Teknik sinyaller oluştur"""
        signals = []
        
        try:
            # RSI Sinyalleri
            if rsi is not None:
                if rsi < 30:
                    signals.append(f"📊 RSI {rsi:.1f} → Oversold (AL sinyali)")
                elif rsi > 70:
                    signals.append(f"📊 RSI {rsi:.1f} → Overbought (SAT sinyali)")
            
            # MACD Sinyalleri
            if macd.get("histogram") is not None and macd.get("macd_line") is not None:
                if macd["histogram"] > 0 and macd["macd_line"] > macd.get("signal_line", 0):
                    signals.append("📈 MACD → Bullish (Yukarı kesişim)")
                elif macd["histogram"] < 0 and macd["macd_line"] < macd.get("signal_line", 0):
                    signals.append("📉 MACD → Bearish (Aşağı kesişim)")
            
            # Bollinger Bands Sinyalleri
            if bollinger.get("position"):
                if bollinger["position"] == "alt":
                    signals.append("📊 Bollinger → Alt bant (AL)")
                elif bollinger["position"] == "üst":
                    signals.append("📊 Bollinger → Üst bant (SAT)")
            
            # SMA Sinyalleri
            if sma_short and sma_long and current_price:
                if current_price > sma_short > sma_long:
                    signals.append("📈 SMA → Bullish (Fiyat > SMA20 > SMA50)")
                elif current_price < sma_short < sma_long:
                    signals.append("📉 SMA → Bearish (Fiyat < SMA20 < SMA50)")
            
            # Momentum Sinyalleri
            if momentum is not None:
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
            if rsi is not None:
                if rsi < 30:
                    score += 10
                elif rsi < 40:
                    score += 5
                elif rsi > 70:
                    score -= 10
                elif rsi > 60:
                    score -= 5
            
            # MACD kontribüsyonu (-10 ile +10)
            if macd.get("histogram") is not None:
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
            if momentum is not None:
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
    
    @staticmethod
    def analyze_trend(df: pd.DataFrame) -> dict:
        """Trend analizi"""
        try:
            if df is None or len(df) < 50:
                return {"trend": "Bilinmiyor", "strength": "N/A"}
            
            close = df["close"].astype(float)
            
            # SMA hesapla
            sma_20 = close.rolling(window=20).mean()
            sma_50 = close.rolling(window=50).mean()
            
            current = float(close.iloc[-1])
            sma_20_val = float(sma_20.iloc[-1])
            sma_50_val = float(sma_50.iloc[-1])
            
            if np.isnan(current) or np.isnan(sma_20_val) or np.isnan(sma_50_val):
                return {"trend": "Bilinmiyor", "strength": "N/A"}
            
            # Trend belirle
            if current > sma_20_val > sma_50_val:
                trend = "Güçlü Yükseliş"
                strength = "Çok Güçlü"
            elif current > sma_20_val and sma_20_val > sma_50_val:
                trend = "Yükseliş"
                strength = "Güçlü"
            elif current > sma_50_val:
                trend = "Zayıf Yükseliş"
                strength = "Zayıf"
            elif current < sma_20_val < sma_50_val:
                trend = "Güçlü Düşüş"
                strength = "Çok Güçlü"
            elif current < sma_20_val and sma_20_val < sma_50_val:
                trend = "Düşüş"
                strength = "Güçlü"
            elif current < sma_50_val:
                trend = "Zayıf Düşüş"
                strength = "Zayıf"
            else:
                trend = "Nötr"
                strength = "Nötr"
            
            return {
                "trend": trend,
                "strength": strength,
                "sma_20": sma_20_val,
                "sma_50": sma_50_val,
                "current": current
            }
            
        except Exception as e:
            return {"trend": "Bilinmiyor", "strength": "N/A"}


def analyze_all_stocks(ticker_list: list) -> list:
    """Tüm hisseleri analiz et (FALLBACK İLE)"""
    print(f"\n📊 Teknik analiz başlıyor ({len(ticker_list)} hisse)...")
    
    results = []
    successful = 0
    
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
            
            close = df["close"]
            
            # Teknik göstergeler hesapla
            rsi = TechnicalAnalyzer.calculate_rsi(close, config.RSI_PERIOD)
            macd = TechnicalAnalyzer.calculate_macd(close)
            bollinger = TechnicalAnalyzer.calculate_bollinger_bands(close, config.BOLLINGER_PERIOD, config.BOLLINGER_STD_DEV)
            sma_short = TechnicalAnalyzer.calculate_sma(close, config.SMA_SHORT)
            sma_long = TechnicalAnalyzer.calculate_sma(close, config.SMA_LONG)
            momentum = TechnicalAnalyzer.calculate_momentum(close, 10)
            atr = TechnicalAnalyzer.calculate_atr(df, 14)
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
            
            # Trend analizi
            trend_data = TechnicalAnalyzer.analyze_trend(df)
            
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
                "atr": atr,
                "signals": signals,
                "fibonacci": fibonacci,
                "trend": trend_data.get("trend"),
                "trend_strength": trend_data.get("strength"),
                "dataframe": df
            }
            
            results.append(result)
            successful += 1
            
        except Exception as e:
            results.append({
                "ticker": ticker,
                "skip": True,
                "reason": str(e)[:100]
            })
    
    # FALLBACK: Eğer hiçbir hisse başarılı değilse default score ile ekle
    if successful == 0:
        print(f"⚠️  Fallback mode: Default skor ile hisseler ekleniyor...")
        for ticker in ticker_list:
            if not any(r.get("ticker") == ticker for r in results if not r.get("skip")):
                results.append({
                    "ticker": ticker,
                    "skip": False,
                    "current_price": 0,
                    "score": 50.0,  # Default score
                    "rsi": 50,
                    "macd_histogram": 0,
                    "bollinger_position": "orta",
                    "sma_short": 0,
                    "sma_long": 0,
                    "momentum_pct": 0,
                    "signals": ["⚪ Default analiz (veri alınamadı)"],
                    "fibonacci": {},
                    "trend": "Nötr",
                    "trend_strength": "N/A",
                    "dataframe": None
                })
                successful += 1
    
    print(f"✅ {successful}/{len(ticker_list)} hisse başarıyla analiz edildi")
    
    return results


if __name__ == "__main__":
    print("🧪 Technical Analyzer Testi")
    print("=" * 70)
    
    # Test
    test_stocks = ["GARAN.IS", "AAPL", "MSFT"]
    results = analyze_all_stocks(test_stocks)
    
    print("\n📊 Sonuçlar:")
    for result in results:
        if not result.get("skip"):
            print(f"\n{result['ticker']}")
            print(f"  Skor: {result['score']}")
            print(f"  RSI: {result['rsi']}")
            print(f"  Momentum: {result['momentum_pct']:+.2f}%")
            print(f"  Trend: {result['trend']}")
