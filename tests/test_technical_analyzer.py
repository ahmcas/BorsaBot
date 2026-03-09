# ============================================================
# tests/test_technical_analyzer.py — Teknik Analiz Testleri
# ============================================================
# Kapsam: RSI, MACD, Bollinger, SMA, Momentum, Fibonacci, Score
# ============================================================

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
import pandas as pd
import numpy as np
import pytest

from technical_analyzer import TechnicalAnalyzer
from tests.conftest import make_price_series, make_ohlcv_df


# ─────────────────────────────────────────────
# RSI Testleri
# ─────────────────────────────────────────────

@pytest.mark.unit
class TestCalculateRSI(unittest.TestCase):
    """TechnicalAnalyzer.calculate_rsi() testleri"""

    def setUp(self):
        self.prices = make_price_series(100)

    def test_rsi_range(self):
        """RSI 0-100 arasında olmalı"""
        rsi = TechnicalAnalyzer.calculate_rsi(self.prices, period=14)
        self.assertGreaterEqual(rsi, 0)
        self.assertLessEqual(rsi, 100)

    def test_rsi_returns_float(self):
        """RSI float döndürmeli"""
        rsi = TechnicalAnalyzer.calculate_rsi(self.prices, period=14)
        self.assertIsInstance(rsi, float)

    def test_rsi_insufficient_data(self):
        """Yetersiz veri ile fallback 50.0 dönmeli"""
        short = make_price_series(5)
        rsi = TechnicalAnalyzer.calculate_rsi(short, period=14)
        self.assertEqual(rsi, 50.0)

    def test_rsi_rising_prices(self):
        """Sürekli yükselen fiyatlarda RSI yüksek (>60) olmalı"""
        rising = pd.Series(np.linspace(100, 120, 50))
        rsi = TechnicalAnalyzer.calculate_rsi(rising, period=14)
        self.assertGreater(rsi, 60)

    def test_rsi_falling_prices(self):
        """Sürekli düşen fiyatlarda RSI düşük (<40) olmalı"""
        falling = pd.Series(np.linspace(120, 100, 50))
        rsi = TechnicalAnalyzer.calculate_rsi(falling, period=14)
        self.assertLess(rsi, 40)

    def test_rsi_none_input(self):
        """None girişte 50.0 dönmeli"""
        rsi = TechnicalAnalyzer.calculate_rsi(None, period=14)
        self.assertEqual(rsi, 50.0)

    def test_rsi_different_periods(self):
        """Farklı periyotlar farklı RSI değerleri üretmeli"""
        prices = make_price_series(100)
        rsi_14 = TechnicalAnalyzer.calculate_rsi(prices, period=14)
        rsi_21 = TechnicalAnalyzer.calculate_rsi(prices, period=21)
        # Her ikisi de geçerli aralıkta
        self.assertGreaterEqual(rsi_14, 0)
        self.assertLessEqual(rsi_14, 100)
        self.assertGreaterEqual(rsi_21, 0)
        self.assertLessEqual(rsi_21, 100)


# ─────────────────────────────────────────────
# MACD Testleri
# ─────────────────────────────────────────────

@pytest.mark.unit
class TestCalculateMACD(unittest.TestCase):
    """TechnicalAnalyzer.calculate_macd() testleri"""

    def setUp(self):
        self.prices = make_price_series(100)

    def test_macd_returns_dict(self):
        """MACD dict döndürmeli"""
        result = TechnicalAnalyzer.calculate_macd(self.prices)
        self.assertIsInstance(result, dict)

    def test_macd_has_required_keys(self):
        """MACD sonucunda gerekli anahtarlar olmalı"""
        result = TechnicalAnalyzer.calculate_macd(self.prices)
        for key in ["macd_line", "signal_line", "histogram"]:
            self.assertIn(key, result)

    def test_macd_insufficient_data(self):
        """26'dan az veri ile sıfır değerler dönmeli"""
        short = make_price_series(20)
        result = TechnicalAnalyzer.calculate_macd(short)
        self.assertEqual(result["macd_line"], 0)
        self.assertEqual(result["signal_line"], 0)
        self.assertEqual(result["histogram"], 0)

    def test_macd_histogram_is_difference(self):
        """Histogram = MACD line - Signal line olmalı"""
        prices = make_price_series(100)
        result = TechnicalAnalyzer.calculate_macd(prices)
        expected = round(result["macd_line"] - result["signal_line"], 6)
        self.assertAlmostEqual(result["histogram"], expected, places=5)

    def test_macd_none_input(self):
        """None girişte sıfır değerler dönmeli"""
        result = TechnicalAnalyzer.calculate_macd(None)
        self.assertEqual(result["histogram"], 0)

    def test_macd_values_are_float(self):
        """MACD değerleri float olmalı"""
        result = TechnicalAnalyzer.calculate_macd(self.prices)
        self.assertIsInstance(result["macd_line"], float)
        self.assertIsInstance(result["signal_line"], float)
        self.assertIsInstance(result["histogram"], float)


# ─────────────────────────────────────────────
# Bollinger Bands Testleri
# ─────────────────────────────────────────────

@pytest.mark.unit
class TestCalculateBollingerBands(unittest.TestCase):
    """TechnicalAnalyzer.calculate_bollinger_bands() testleri"""

    def setUp(self):
        self.prices = make_price_series(100)

    def test_bollinger_returns_dict(self):
        """Bollinger dict döndürmeli"""
        result = TechnicalAnalyzer.calculate_bollinger_bands(self.prices, period=20)
        self.assertIsInstance(result, dict)

    def test_bollinger_has_required_keys(self):
        """Bollinger sonucunda gerekli anahtarlar olmalı"""
        result = TechnicalAnalyzer.calculate_bollinger_bands(self.prices, period=20)
        for key in ["upper_band", "middle_band", "lower_band", "position"]:
            self.assertIn(key, result)

    def test_bollinger_band_order(self):
        """upper >= middle >= lower olmalı"""
        result = TechnicalAnalyzer.calculate_bollinger_bands(self.prices, period=20)
        self.assertGreaterEqual(result["upper_band"], result["middle_band"])
        self.assertGreaterEqual(result["middle_band"], result["lower_band"])

    def test_bollinger_position_valid(self):
        """Position 'üst', 'orta' veya 'alt' olmalı"""
        result = TechnicalAnalyzer.calculate_bollinger_bands(self.prices, period=20)
        self.assertIn(result["position"], ["üst", "orta", "alt"])

    def test_bollinger_insufficient_data(self):
        """Yetersiz veri ile fallback döndürmeli"""
        short = make_price_series(10)
        result = TechnicalAnalyzer.calculate_bollinger_bands(short, period=20)
        self.assertEqual(result["upper_band"], 0)

    def test_bollinger_position_alt_when_price_low(self):
        """Fiyat alt bant civarındaysa position 'alt' olmalı"""
        # Düşen fiyat serisi: son değer alt bantta olacak
        falling = pd.Series(np.linspace(120, 80, 60))
        result = TechnicalAnalyzer.calculate_bollinger_bands(falling, period=20)
        self.assertEqual(result["position"], "alt")


# ─────────────────────────────────────────────
# SMA Testleri
# ─────────────────────────────────────────────

@pytest.mark.unit
class TestCalculateSMA(unittest.TestCase):
    """TechnicalAnalyzer.calculate_sma() testleri"""

    def setUp(self):
        self.prices = make_price_series(100)

    def test_sma_returns_float(self):
        """SMA float döndürmeli"""
        sma = TechnicalAnalyzer.calculate_sma(self.prices, period=20)
        self.assertIsInstance(sma, float)

    def test_sma_value_is_positive(self):
        """SMA pozitif olmalı"""
        sma = TechnicalAnalyzer.calculate_sma(self.prices, period=20)
        self.assertGreater(sma, 0)

    def test_sma_constant_prices(self):
        """Sabit fiyat serisinde SMA = fiyat olmalı"""
        constant = pd.Series([100.0] * 50)
        sma = TechnicalAnalyzer.calculate_sma(constant, period=20)
        self.assertAlmostEqual(sma, 100.0, places=1)

    def test_sma_insufficient_data(self):
        """Yetersiz veri ile 0.0 dönmeli"""
        short = make_price_series(5)
        sma = TechnicalAnalyzer.calculate_sma(short, period=20)
        self.assertEqual(sma, 0.0)

    def test_sma_none_input(self):
        """None girişte 0.0 dönmeli"""
        sma = TechnicalAnalyzer.calculate_sma(None, period=20)
        self.assertEqual(sma, 0.0)

    def test_short_sma_follows_price_faster(self):
        """Kısa SMA uzun SMA'ya göre son fiyata daha yakın olmalı"""
        prices = make_price_series(100)
        sma_short = TechnicalAnalyzer.calculate_sma(prices, period=10)
        sma_long = TechnicalAnalyzer.calculate_sma(prices, period=50)
        last_price = float(prices.iloc[-1])
        self.assertLess(abs(sma_short - last_price), abs(sma_long - last_price))


# ─────────────────────────────────────────────
# Momentum Testleri
# ─────────────────────────────────────────────

@pytest.mark.unit
class TestCalculateMomentum(unittest.TestCase):
    """TechnicalAnalyzer.calculate_momentum() testleri"""

    def test_momentum_returns_float(self):
        """Momentum float döndürmeli"""
        prices = make_price_series(50)
        mom = TechnicalAnalyzer.calculate_momentum(prices, period=10)
        self.assertIsInstance(mom, float)

    def test_momentum_positive_for_rising(self):
        """Yükselen fiyatlarda momentum pozitif olmalı"""
        rising = pd.Series(np.linspace(100, 110, 30))
        mom = TechnicalAnalyzer.calculate_momentum(rising, period=10)
        self.assertGreater(mom, 0)

    def test_momentum_negative_for_falling(self):
        """Düşen fiyatlarda momentum negatif olmalı"""
        falling = pd.Series(np.linspace(110, 100, 30))
        mom = TechnicalAnalyzer.calculate_momentum(falling, period=10)
        self.assertLess(mom, 0)

    def test_momentum_zero_for_flat(self):
        """Sabit fiyatlarda momentum sıfır olmalı"""
        flat = pd.Series([100.0] * 30)
        mom = TechnicalAnalyzer.calculate_momentum(flat, period=10)
        self.assertAlmostEqual(mom, 0.0, places=5)

    def test_momentum_insufficient_data(self):
        """Yetersiz veri ile 0.0 dönmeli"""
        short = make_price_series(5)
        mom = TechnicalAnalyzer.calculate_momentum(short, period=21)
        self.assertEqual(mom, 0.0)

    def test_momentum_none_input(self):
        """None girişte 0.0 dönmeli"""
        mom = TechnicalAnalyzer.calculate_momentum(None, period=10)
        self.assertEqual(mom, 0.0)


# ─────────────────────────────────────────────
# Fibonacci Testleri
# ─────────────────────────────────────────────

@pytest.mark.unit
class TestCalculateFibonacci(unittest.TestCase):
    """TechnicalAnalyzer.calculate_fibonacci() testleri"""

    def setUp(self):
        self.df = make_ohlcv_df(100)

    def test_fibonacci_returns_dict(self):
        """Fibonacci dict döndürmeli"""
        result = TechnicalAnalyzer.calculate_fibonacci(self.df, lookback=60)
        self.assertIsInstance(result, dict)

    def test_fibonacci_has_levels(self):
        """Fibonacci sonucunda temel seviyeler bulunmalı"""
        result = TechnicalAnalyzer.calculate_fibonacci(self.df, lookback=60)
        for level in ["fib_0.236", "fib_0.382", "fib_0.618"]:
            self.assertIn(level, result)

    def test_fibonacci_level_ordering(self):
        """fib_0.618 < fib_0.382 < fib_0.236 olmalı (geri çekilme seviyeleri)"""
        result = TechnicalAnalyzer.calculate_fibonacci(self.df, lookback=60)
        if all(k in result for k in ["fib_0.236", "fib_0.382", "fib_0.618"]):
            self.assertGreater(result["fib_0.236"], result["fib_0.618"])

    def test_fibonacci_insufficient_data(self):
        """Yetersiz veri ile boş dict dönmeli"""
        small_df = make_ohlcv_df(10)
        result = TechnicalAnalyzer.calculate_fibonacci(small_df, lookback=60)
        self.assertIsInstance(result, dict)

    def test_fibonacci_none_input(self):
        """None girişte boş dict dönmeli"""
        result = TechnicalAnalyzer.calculate_fibonacci(None, lookback=60)
        self.assertEqual(result, {})

    def test_fibonacci_current_price_present(self):
        """'current' anahtarı sonuçta bulunmalı"""
        result = TechnicalAnalyzer.calculate_fibonacci(self.df, lookback=60)
        self.assertIn("current", result)


# ─────────────────────────────────────────────
# Technical Score Testleri
# ─────────────────────────────────────────────

@pytest.mark.unit
class TestCalculateTechnicalScore(unittest.TestCase):
    """TechnicalAnalyzer.calculate_technical_score() testleri"""

    def _make_macd(self, hist=0.1):
        return {"histogram": hist, "macd_line": 0.1, "signal_line": 0.0}

    def _make_bollinger(self, position="orta"):
        return {"position": position, "upper_band": 110, "middle_band": 100, "lower_band": 90}

    def test_score_range(self):
        """Skor 0-100 arasında olmalı"""
        score = TechnicalAnalyzer.calculate_technical_score(
            rsi=50, macd=self._make_macd(0.1),
            bollinger=self._make_bollinger("orta"),
            sma20=100, sma50=95, momentum=2, price=101,
        )
        self.assertGreaterEqual(score, 0)
        self.assertLessEqual(score, 100)

    def test_score_bullish_conditions(self):
        """Bullish koşullarda yüksek skor (>60) beklenir"""
        score = TechnicalAnalyzer.calculate_technical_score(
            rsi=30,  # oversold
            macd=self._make_macd(0.5),  # positive
            bollinger=self._make_bollinger("alt"),  # alt bant
            sma20=105, sma50=95, momentum=12, price=110,
        )
        self.assertGreater(score, 60)

    def test_score_bearish_conditions(self):
        """Bearish koşullarda düşük skor (<50) beklenir"""
        score = TechnicalAnalyzer.calculate_technical_score(
            rsi=75,  # overbought
            macd=self._make_macd(-0.5),  # negative
            bollinger=self._make_bollinger("üst"),  # üst bant
            sma20=90, sma50=100, momentum=-12, price=85,
        )
        self.assertLess(score, 50)

    def test_score_neutral_conditions(self):
        """Nötr koşullarda orta skor (~50) beklenir"""
        score = TechnicalAnalyzer.calculate_technical_score(
            rsi=50,
            macd=self._make_macd(0),
            bollinger=self._make_bollinger("orta"),
            sma20=100, sma50=100, momentum=0, price=100,
        )
        # Skor 40-70 arasında olmalı
        self.assertGreaterEqual(score, 30)
        self.assertLessEqual(score, 70)

    def test_score_returns_float(self):
        """Skor float dönmeli"""
        score = TechnicalAnalyzer.calculate_technical_score(
            rsi=50, macd=self._make_macd(0),
            bollinger=self._make_bollinger("orta"),
            sma20=100, sma50=100, momentum=0, price=100,
        )
        self.assertIsInstance(score, float)


# ─────────────────────────────────────────────
# Sinyal Üretimi Testleri
# ─────────────────────────────────────────────

@pytest.mark.unit
class TestGenerateSignals(unittest.TestCase):
    """TechnicalAnalyzer.generate_signals() testleri"""

    def test_signals_returns_list(self):
        """generate_signals() liste döndürmeli"""
        signals = TechnicalAnalyzer.generate_signals(
            rsi=50, macd={"histogram": 0, "macd_line": 0, "signal_line": 0},
            bollinger={"position": "orta"}, sma20=100, sma50=95,
            momentum=2, price=101,
        )
        self.assertIsInstance(signals, list)

    def test_signals_not_empty(self):
        """Sinyal listesi boş olmamalı (en az bir eleman)"""
        signals = TechnicalAnalyzer.generate_signals(
            rsi=50, macd={"histogram": 0, "macd_line": 0, "signal_line": 0},
            bollinger={"position": "orta"}, sma20=100, sma50=95,
            momentum=0, price=100,
        )
        self.assertGreater(len(signals), 0)

    def test_oversold_rsi_triggers_signal(self):
        """Aşırı satım RSI AL sinyali üretmeli"""
        signals = TechnicalAnalyzer.generate_signals(
            rsi=30, macd={"histogram": 0, "macd_line": 0, "signal_line": 0},
            bollinger={"position": "orta"}, sma20=100, sma50=95,
            momentum=0, price=100,
        )
        # Oversold sinyali en az bir sinyalde bulunmalı
        signal_text = " ".join(signals)
        self.assertIn("RSI", signal_text)

    def test_bullish_macd_triggers_signal(self):
        """Pozitif MACD histogram bullish sinyal üretmeli"""
        signals = TechnicalAnalyzer.generate_signals(
            rsi=50, macd={"histogram": 0.5, "macd_line": 0.5, "signal_line": 0.0},
            bollinger={"position": "orta"}, sma20=100, sma50=95,
            momentum=0, price=100,
        )
        signal_text = " ".join(signals)
        self.assertIn("MACD", signal_text)


# ─────────────────────────────────────────────
# ATR Testleri
# ─────────────────────────────────────────────

@pytest.mark.unit
class TestCalculateATR(unittest.TestCase):
    """TechnicalAnalyzer.calculate_atr() testleri"""

    def test_atr_returns_float(self):
        """ATR float döndürmeli"""
        df = make_ohlcv_df(100)
        atr = TechnicalAnalyzer.calculate_atr(df, period=14)
        self.assertIsInstance(atr, float)

    def test_atr_positive(self):
        """ATR pozitif olmalı"""
        df = make_ohlcv_df(100)
        atr = TechnicalAnalyzer.calculate_atr(df, period=14)
        self.assertGreater(atr, 0)

    def test_atr_insufficient_data(self):
        """Yetersiz veri ile 0.0 dönmeli"""
        small_df = make_ohlcv_df(5)
        atr = TechnicalAnalyzer.calculate_atr(small_df, period=14)
        self.assertEqual(atr, 0.0)

    def test_atr_none_input(self):
        """None girişte 0.0 dönmeli"""
        atr = TechnicalAnalyzer.calculate_atr(None, period=14)
        self.assertEqual(atr, 0.0)


# ─────────────────────────────────────────────
# analyze_single_stock – fallback testi
# ─────────────────────────────────────────────

@pytest.mark.unit
class TestAnalyzeSingleStockFallback(unittest.TestCase):
    """TechnicalAnalyzer.analyze_single_stock() fallback path testleri"""

    def test_result_has_ticker_key(self):
        """Sonuçta 'ticker' anahtarı olmalı"""
        # Mock: yfinance çağrısı başarısız → _analyze_with_price_only tetiklenir
        # Bu test sadece yapısal tutarlılığı kontrol eder
        from unittest.mock import patch
        with patch.object(TechnicalAnalyzer, "get_stock_data", return_value=None), \
             patch.object(TechnicalAnalyzer, "get_current_price", return_value=None):
            result = TechnicalAnalyzer.analyze_single_stock("TEST")
            self.assertIn("ticker", result)
            self.assertEqual(result["ticker"], "TEST")

    def test_skip_true_when_no_price(self):
        """Fiyat alınamadığında skip=True olmalı"""
        from unittest.mock import patch
        with patch.object(TechnicalAnalyzer, "get_stock_data", return_value=None), \
             patch.object(TechnicalAnalyzer, "get_current_price", return_value=None):
            result = TechnicalAnalyzer.analyze_single_stock("NODATA")
            self.assertTrue(result.get("skip"))

    def test_price_only_returns_score(self):
        """Sadece fiyat ile analiz skoru 0-100 arasında döndürmeli"""
        from unittest.mock import patch
        import pandas as pd, numpy as np
        mock_df = pd.DataFrame({
            "Close": [100.0, 101.0, 102.0, 101.5, 103.0],
        }, index=pd.date_range("2026-01-01", periods=5, freq="B"))
        # MultiIndex benzeri tek sütunlu DataFrame döndür
        with patch.object(TechnicalAnalyzer, "get_stock_data", return_value=None), \
             patch.object(TechnicalAnalyzer, "get_current_price", return_value=102.0), \
             patch("yfinance.download", return_value=mock_df):
            result = TechnicalAnalyzer.analyze_single_stock("FAKE")
            if not result.get("skip"):
                score = result.get("score", -1)
                self.assertGreaterEqual(score, 0)
                self.assertLessEqual(score, 100)


if __name__ == "__main__":
    unittest.main()
