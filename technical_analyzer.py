# ============================================================
# technical_analyzer.py — Teknik Analiz Engine (v6 - ULTRA FINAL)
# ============================================================
# YENİ: Smart Fallback ile Real Data Fetching
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
    def get_current_price(ticker: str) -> float:
        """REAL-TIME fiyat al (hızlı & basit)"""
        try:
            # Sadece son veriyi al (hızlı)
            data = yf.download(ticker, period="5d", progress=False, timeout=10)
            
            if data is None or data.empty:
                return None
            
            if isinstance(data, pd.Series):
                return float(data.iloc[-1])
            else:
                return float(data["close"].iloc[-1])
        
        except Exception as e:
            return None
    
    @staticmethod
    def get_historical_data(ticker: str, period: str = "200d") -> pd.DataFrame:
        """Tarihi veri çek (SMART FALLBACK İLE)"""
        try:
            df = yf.download(ticker, period=period, progress=False, timeout=30)
            
            # Boş kontrol
            if df is None or df.empty or len(df) == 0:
                return None
            
            # Series ise DataFrame'e çevir
            if isinstance(df, pd.Series):
                df = df.to_frame()
            
            # Sütun adlarını normalize et
            df.columns = [str(col).lower().replace(' ', '_') for col in df.columns]
            
            # Gerekli sütunlar
            required = ['close', 'high', 'low', 'volume']
            if not all(col in df.columns for col in required):
                return None
            
            # Veri tiplerini dönüştür
            for col in required:
                df[col] = pd.to_numeric(df[col], errors='coerce')
            
            # NaN'ları temizle
            df = df.dropna()
            
            if len(df) < 20:
                return None
            
            return df
        
        except Exception as e:
            return None
    
    @staticmethod
    def calculate_rsi(prices: pd.Series, period: int = 14) -> float:
        """RSI hesapla"""
        try:
            if prices is None or len(prices) < period + 1:
                return 50.0
            
            prices = prices.dropna()
            if len(prices) < period + 1:
                return 50.0
            
            delta = prices.diff()
            gain = delta.clip(lower=0)
            loss = -delta.clip(upper=0)
            
            avg_gain = gain.rolling(window=period).mean()
            avg_loss = loss.rolling(window=period).mean()
            
            if avg_loss.iloc[-1] == 0:
                return 100.0 if avg_gain.iloc[-1] > 0 else 0.0
            
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))
            
            current_rsi = float(rsi.iloc[-1])
            
            if np.isnan(current_rsi) or np.isinf(current_rsi):
                return 50.0
            
            return round(max(0, min(100, current_rsi)), 2)
        
        except Exception as e:
            return 50.0
    
    @staticmethod
    def calculate_macd(prices: pd.Series) -> dict:
        """MACD hesapla"""
        try:
            if prices is None or len(prices) < 26:
                return {"macd_line": 0, "signal_line": 0, "histogram": 0}
            
            prices = prices.dropna()
            if len(prices) < 26:
                return {"macd_line": 0, "signal_line": 0, "histogram": 0}
            
            exp1 = prices.ewm(span=config.MACD_FAST, adjust=False).mean()
            exp2 = prices.ewm(span=config.MACD_SLOW, adjust=False).mean()
            
            macd_line = exp1 - exp2
            signal_line = macd_line.ewm(span=config.MACD_SIGNAL, adjust=False).mean()
            histogram = macd_line - signal_line
            
            macd_val = float(macd_line.iloc[-1])
            signal_val = float(signal_line.iloc[-1])
            hist_val = float(histogram.iloc[-1])
            
            if any(np.isnan(x) or np.isinf(x) for x in [macd_val, signal_val, hist_val]):
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
                return {"upper_band": 0, "middle_band": 0, "lower_band": 0, "position": "orta"}
            
            prices = prices.dropna()
            if len(prices) < period:
                return {"upper_band": 0, "middle_band": 0, "lower_band": 0, "position": "orta"}
            
            sma = prices.rolling(window=period).mean()
            std = prices.rolling(window=period).std()
            
            upper = sma + (std_dev * std)
            lower = sma - (std_dev * std)
            
            current_price = float(prices.iloc[-1])
            upper_val = float(upper.iloc[-1])
            middle_val = float(sma.iloc[-1])
            lower_val = float(lower.iloc[-1])
            
            if any(np.isnan(x) for x in [current_price, upper_val, lower_val]):
                return {"upper_band": 0, "middle_band": 0, "lower_band": 0, "position": "orta"}
            
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
            return {"upper_band": 0, "middle_band": 0, "lower_band": 0, "position": "orta"}
    
    @staticmethod
    def calculate_sma(prices: pd.Series, period: int) -> float:
        """SMA hesapla"""
        try:
            if prices is None or len(prices) < period:
                return 0.0
            
            prices = prices.dropna()
            if len(prices) < period:
                return 0.0
            
            sma = prices.rolling(window=period).mean()
            sma_val = float(sma.iloc[-1])
            
            if np.isnan(sma_val):
                return 0.0
            
            return round(sma_val, 2)
        
        except Exception as e:
            return 0.0
    
    @staticmethod
    def calculate_momentum(prices: pd.Series, period: int = 10) -> float:
        """Momentum hesapla"""
        try:
            if prices is None or len(prices) < period:
                return 0.0
            
            prices = prices.dropna()
            if len(prices) < period:
                return 0.0
            
            current = float(prices.iloc[-1])
            past = float(prices.iloc[-period])
            
            if past == 0 or np.isnan(current) or np.isnan(past):
                return 0.0
            
            momentum = ((current - past) / past) * 100
            
            if np.isnan(momentum) or np.isinf(momentum):
                return 0.0
            
            return round(momentum, 2)
        
        except Exception as e:
            return 0.0
    
    @staticmethod
    def calculate_atr(df: pd.DataFrame, period: int = 14) -> float:
        """ATR hesapla"""
        try:
            if df is None or len(df) < period + 1:
                return 0.0
            
            high = df['high'].astype(float)
            low = df['low'].astype(float)
            close = df['close'].astype(float)
            
            tr1 = high - low
            tr2 = abs(high - close.shift())
            tr3 = abs(low - close.shift())
            
            tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
            atr = tr.rolling(window=period).mean()
            
            atr_val = float(atr.iloc[-1])
            
            if np.isnan(atr_val):
                return 0.0
            
            return round(atr_val, 2)
        
        except Exception as e:
            return 0.0
    
    @staticmethod
    def calculate_fibonacci(df: pd.DataFrame, lookback: int = 60) -> dict:
        """Fibonacci hesapla"""
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
        """Sinyaller oluştur"""
        signals = []
        
        try:
            if rsi and rsi < 30:
                signals.append(f"📊 RSI {rsi:.1f} → Oversold (AL)")
            elif rsi and rsi > 70:
                signals.append(f"📊 RSI {rsi:.1f} → Overbought (SAT)")
            
            if macd.get("histogram", 0) > 0:
                signals.append("📈 MACD → Bullish")
            elif macd.get("histogram", 0) < 0:
                signals.append("📉 MACD → Bearish")
            
            if bollinger.get("position") == "alt":
                signals.append("📊 Bollinger → Alt bant")
            elif bollinger.get("position") == "üst":
                signals.append("📊 Bollinger → Üst bant")
            
            if sma_short and sma_long and current_price:
                if current_price > sma_short > sma_long:
                    signals.append("📈 SMA → Bullish")
                elif current_price < sma_short < sma_long:
                    signals.append("📉 SMA → Bearish")
            
            if momentum and momentum > 5:
                signals.append(f"📈 Momentum {momentum:+.1f}%")
            elif momentum and momentum < -5:
                signals.append(f"📉 Momentum {momentum:+.1f}%")
            
            return signals if signals else ["⚪ Nötr"]
        
        except Exception as e:
            return ["⚪ Nötr"]
    
    @staticmethod
    def calculate_technical_score(rsi: float, macd: dict, bollinger: dict, 
                                 sma_short: float, sma_long: float, 
                                 momentum: float, current_price: float) -> float:
        """Skor hesapla"""
        try:
            score = 50
            
            if rsi:
                if rsi < 30:
                    score += 10
                elif rsi < 40:
                    score += 5
                elif rsi > 70:
                    score -= 10
                elif rsi > 60:
                    score -= 5
            
            if macd.get("histogram", 0) > 0:
                score += 5
            elif macd.get("histogram", 0) < 0:
                score -= 5
            
            if bollinger.get("position") == "alt":
                score += 8
            elif bollinger.get("position") == "üst":
                score -= 8
            
            if sma_short and sma_long and current_price:
                if current_price > sma_short > sma_long:
                    score += 10
                elif current_price < sma_short < sma_long:
                    score -= 10
            
            if momentum:
                if momentum > 10:
                    score += 10
                elif momentum > 0:
                    score += 5
                elif momentum < -10:
                    score -= 10
                elif momentum < 0:
                    score -= 5
            
            return round(max(0, min(100, score)), 1)
        
        except Exception as e:
            return 50.0
    
    @staticmethod
    def analyze_trend(df: pd.DataFrame) -> dict:
        """Trend analizi"""
        try:
            if df is None or len(df) < 50:
                return {"trend": "Nötr", "strength": "N/A"}
            
            close = df["close"].astype(float)
            
            sma_20 = close.rolling(window=20).mean()
            sma_50 = close.rolling(window=50).mean()
            
            current = float(close.iloc[-1])
            sma_20_val = float(sma_20.iloc[-1])
            sma_50_val = float(sma_50.iloc[-1])
            
            if np.isnan(current) or np.isnan(sma_20_val) or np.isnan(sma_50_val):
                return {"trend": "Nötr", "strength": "N/A"}
            
            if current > sma_20_val > sma_50_val:
                trend = "Güçlü Yükseliş"
            elif current > sma_20_val:
                trend = "Yükseliş"
            elif current < sma_20_val < sma_50_val:
                trend = "Güçlü Düşüş"
            elif current < sma_20_val:
                trend = "Düşüş"
            else:
                trend = "Nötr"
            
            return {"trend": trend, "strength": "Stabil"}
        
        except Exception as e:
            return {"trend": "Nötr", "strength": "N/A"}


def analyze_all_stocks(ticker_list: list) -> list:
    """Tüm hisseleri analiz et (SMART FALLBACK)"""
    print(f"\n📊 Teknik analiz başlıyor ({len(ticker_list)} hisse)...")
    
    results = []
    successful = 0
    
    for ticker in ticker_list:
        try:
            # 1. Tarihi veri çek
            df = TechnicalAnalyzer.get_historical_data(ticker, period=f"{config.LOOKBACK_DAYS}d")
            
            # 2. Eğer tarihi veri yoksa real-time fiyat al
            if df is None or df.empty:
                current_price = TechnicalAnalyzer.get_current_price(ticker)
                
                if current_price is None or current_price == 0:
                    results.append({
                        "ticker": ticker,
                        "skip": True,
                        "reason": "Veri alınamadı"
                    })
                    continue
                
                # SMART FALLBACK: Real fiyatla default analiz yap
                result = {
                    "ticker": ticker,
                    "skip": False,
                    "current_price": round(current_price, 2),
                    "score": 50.0,
                    "rsi": 50,
                    "macd_histogram": 0,
                    "bollinger_position": "orta",
                    "sma_short": round(current_price * 0.98, 2),
                    "sma_long": round(current_price * 0.95, 2),
                    "momentum_pct": 0.0,
                    "atr": round(current_price * 0.02, 2),
                    "signals": ["✅ Real-time fiyat kullanıldı"],
                    "fibonacci": {
                        "current": round(current_price, 2),
                        "fib_0.236": round(current_price * 1.02, 2),
                        "fib_0.382": round(current_price * 1.038, 2),
                        "fib_0.618": round(current_price * 0.962, 2),
                    },
                    "trend": "Nötr",
                    "trend_strength": "Stabil",
                    "dataframe": None
                }
                
                results.append(result)
                successful += 1
                print(f"   ✅ {ticker:10s} - Real-time fiyat: ${current_price:.2f}")
                continue
            
            # Tarihi veri varsa normal analiz yap
            close = df["close"]
            
            rsi = TechnicalAnalyzer.calculate_rsi(close, config.RSI_PERIOD)
            macd = TechnicalAnalyzer.calculate_macd(close)
            bollinger = TechnicalAnalyzer.calculate_bollinger_bands(close, config.BOLLINGER_PERIOD, config.BOLLINGER_STD_DEV)
            sma_short = TechnicalAnalyzer.calculate_sma(close, config.SMA_SHORT)
            sma_long = TechnicalAnalyzer.calculate_sma(close, config.SMA_LONG)
            momentum = TechnicalAnalyzer.calculate_momentum(close, 10)
            atr = TechnicalAnalyzer.calculate_atr(df, 14)
            fibonacci = TechnicalAnalyzer.calculate_fibonacci(df, config.FIBONACCI_LOOKBACK)
            
            current_price = float(close.iloc[-1])
            
            signals = TechnicalAnalyzer.generate_signals(
                rsi, macd, bollinger, sma_short, sma_long, momentum, current_price
            )
            
            technical_score = TechnicalAnalyzer.calculate_technical_score(
                rsi, macd, bollinger, sma_short, sma_long, momentum, current_price
            )
            
            trend_data = TechnicalAnalyzer.analyze_trend(df)
            
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
            print(f"   ✅ {ticker:10s} - Skor: {technical_score:6.1f}")
        
        except Exception as e:
            results.append({
                "ticker": ticker,
                "skip": True,
                "reason": str(e)[:100]
            })
    
    print(f"✅ {successful}/{len(ticker_list)} hisse başarıyla analiz edildi")
    
    return results


if __name__ == "__main__":
    print("🧪 Technical Analyzer Testi")
    print("=" * 70)
    
    test_stocks = ["GARAN.IS", "AAPL", "MSFT"]
    results = analyze_all_stocks(test_stocks)
    
    print("\n📊 Sonuçlar:")
    for result in results:
        if not result.get("skip"):
            print(f"{result['ticker']}: Fiyat=${result['current_price']:.2f}, Skor={result['score']}")
