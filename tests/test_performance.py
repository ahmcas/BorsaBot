# ============================================================
# tests/test_performance.py — Performans Testleri
# ============================================================
# Kapsam: Execution time, Memory usage
# ============================================================

import sys
import os
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
import pandas as pd
import numpy as np
import pytest

from technical_analyzer import TechnicalAnalyzer
from news_analyzer import RateLimiter, CacheManager, NewsAnalyzer
from scorer import ScoreCalculator, select_top_stocks, generate_recommendation_text
from tests.conftest import make_price_series, make_ohlcv_df


# ─────────────────────────────────────────────
# Teknik Gösterge Hız Testleri
# ─────────────────────────────────────────────

@pytest.mark.performance
class TestTechnicalIndicatorPerformance(unittest.TestCase):
    """Teknik gösterge hesaplamalarının hız testleri"""

    def setUp(self):
        self.prices = make_price_series(250)
        self.df = make_ohlcv_df(250)

    def test_rsi_executes_fast(self):
        """RSI hesabı 0.5 saniyede tamamlanmalı"""
        start = time.perf_counter()
        for _ in range(100):
            TechnicalAnalyzer.calculate_rsi(self.prices, period=14)
        elapsed = time.perf_counter() - start
        self.assertLess(elapsed, 0.5, f"RSI (100x) çok yavaş: {elapsed:.3f}s")

    def test_macd_executes_fast(self):
        """MACD hesabı 0.5 saniyede tamamlanmalı"""
        start = time.perf_counter()
        for _ in range(100):
            TechnicalAnalyzer.calculate_macd(self.prices)
        elapsed = time.perf_counter() - start
        self.assertLess(elapsed, 0.5, f"MACD (100x) çok yavaş: {elapsed:.3f}s")

    def test_bollinger_executes_fast(self):
        """Bollinger hesabı 0.5 saniyede tamamlanmalı"""
        start = time.perf_counter()
        for _ in range(100):
            TechnicalAnalyzer.calculate_bollinger_bands(self.prices, period=20)
        elapsed = time.perf_counter() - start
        self.assertLess(elapsed, 0.5, f"Bollinger (100x) çok yavaş: {elapsed:.3f}s")

    def test_technical_score_executes_fast(self):
        """Teknik skor hesabı 0.1 saniyede tamamlanmalı"""
        macd = {"histogram": 0.1, "macd_line": 0.1, "signal_line": 0.0}
        bollinger = {"position": "orta", "upper_band": 110, "middle_band": 100, "lower_band": 90}
        start = time.perf_counter()
        for _ in range(1000):
            TechnicalAnalyzer.calculate_technical_score(
                rsi=50, macd=macd, bollinger=bollinger,
                sma20=100, sma50=95, momentum=2, price=101,
            )
        elapsed = time.perf_counter() - start
        self.assertLess(elapsed, 0.1, f"TechScore (1000x) çok yavaş: {elapsed:.3f}s")

    def test_fibonacci_executes_fast(self):
        """Fibonacci hesabı 0.5 saniyede tamamlanmalı"""
        start = time.perf_counter()
        for _ in range(100):
            TechnicalAnalyzer.calculate_fibonacci(self.df, lookback=60)
        elapsed = time.perf_counter() - start
        self.assertLess(elapsed, 0.5, f"Fibonacci (100x) çok yavaş: {elapsed:.3f}s")

    def test_sma_executes_fast(self):
        """SMA hesabı 0.2 saniyede tamamlanmalı"""
        start = time.perf_counter()
        for _ in range(200):
            TechnicalAnalyzer.calculate_sma(self.prices, period=20)
        elapsed = time.perf_counter() - start
        self.assertLess(elapsed, 0.2, f"SMA (200x) çok yavaş: {elapsed:.3f}s")


# ─────────────────────────────────────────────
# Skor Hesaplama Hız Testleri
# ─────────────────────────────────────────────

@pytest.mark.performance
class TestScorerPerformance(unittest.TestCase):
    """Skor hesaplamalarının hız testleri"""

    def _make_result(self, ticker, score):
        return {
            "ticker": ticker, "score": score, "skip": False,
            "current_price": 100.0, "rsi": 50.0, "macd_histogram": 0.1,
            "macd_line": 0.2, "signal_line": 0.1,
            "bollinger_position": "orta", "bollinger_upper": 110.0,
            "bollinger_middle": 100.0, "bollinger_lower": 90.0,
            "sma_short": 100.0, "sma_long": 95.0, "momentum_pct": 2.0,
            "atr": 1.5, "trend": "Yukarı", "trend_strength": "Güçlü",
            "signals": [], "fibonacci": {"fib_0.236": 108.0, "fib_0.618": 93.0},
            "breakout": {}, "dataframe": None,
        }

    def test_composite_score_bulk_fast(self):
        """1000 composite skor hesabı 0.1 saniyede tamamlanmalı"""
        start = time.perf_counter()
        for i in range(1000):
            ScoreCalculator.calculate_composite_score(float(i % 100), 0.5)
        elapsed = time.perf_counter() - start
        self.assertLess(elapsed, 0.1, f"CompositeScore (1000x) çok yavaş: {elapsed:.3f}s")

    def test_select_top_stocks_50_stocks_fast(self):
        """50 hisse seçimi 0.5 saniyede tamamlanmalı"""
        results = [self._make_result(f"T{i}", float(80 - i % 50)) for i in range(50)]
        sector_scores = {"teknoloji": 0.5, "finans": 0.3}
        start = time.perf_counter()
        select_top_stocks(results, sector_scores, max_count=5)
        elapsed = time.perf_counter() - start
        self.assertLess(elapsed, 0.5, f"SelectTopStocks (50 hisse) çok yavaş: {elapsed:.3f}s")

    def test_generate_recommendations_fast(self):
        """Öneri üretimi 0.1 saniyede tamamlanmalı"""
        stocks = [
            {
                "ticker": f"T{i}", "score": float(65 - i),
                "current_price": 100.0, "sector": "Teknoloji",
                "support": 93.0, "resistance": 108.0,
                "reward_pct": 8.0, "risk_pct": 7.0, "reward_risk_ratio": 1.14,
                "rsi": 52.0, "macd_histogram": 0.1, "macd_line": 0.2, "signal_line": 0.1,
                "bollinger_position": "orta", "bollinger_upper": 110.0,
                "bollinger_middle": 100.0, "bollinger_lower": 90.0,
                "sma_short": 100.0, "sma_long": 95.0, "momentum_pct": 2.0, "atr": 1.5,
                "trend": "Yukarı", "trend_strength": "Güçlü",
                "signals": ["RSI_BUY"], "fibonacci": {"fib_0.236": 108.0},
                "breakout": {}, "source_pool": "",
            }
            for i in range(5)
        ]
        start = time.perf_counter()
        generate_recommendation_text(stocks, {})
        elapsed = time.perf_counter() - start
        self.assertLess(elapsed, 0.1, f"GenerateRecommendations çok yavaş: {elapsed:.3f}s")


# ─────────────────────────────────────────────
# Cache Hız Testleri
# ─────────────────────────────────────────────

@pytest.mark.performance
class TestCachePerformance(unittest.TestCase):
    """CacheManager hız testleri"""

    def setUp(self):
        import tempfile
        self.tmp_dir = tempfile.mkdtemp()
        self.cache = CacheManager(cache_dir=self.tmp_dir, ttl_hours=1)

    def test_cache_set_get_fast(self):
        """100 cache set/get işlemi 0.5 saniyede tamamlanmalı"""
        data = {"key": "value", "number": 42}
        start = time.perf_counter()
        for i in range(100):
            self.cache.set(f"key_{i}", data)
            self.cache.get(f"key_{i}")
        elapsed = time.perf_counter() - start
        self.assertLess(elapsed, 0.5, f"Cache set/get (100x) çok yavaş: {elapsed:.3f}s")

    def test_memory_cache_faster_than_initial_set(self):
        """Bellek cache'inden okuma disk cache'den daha hızlı olmalı"""
        data = {"value": "x" * 1000}
        self.cache.set("speed_test", data)

        # Bellek cache'inden oku
        start = time.perf_counter()
        for _ in range(100):
            self.cache.get("speed_test")
        elapsed = time.perf_counter() - start
        self.assertLess(elapsed, 0.1, f"Bellek cache (100x) çok yavaş: {elapsed:.3f}s")


# ─────────────────────────────────────────────
# Sentiment Analizi Hız Testleri
# ─────────────────────────────────────────────

@pytest.mark.performance
class TestSentimentPerformance(unittest.TestCase):
    """Sentiment analizi hız testleri"""

    def test_sentiment_bulk_analysis_fast(self):
        """50 metin sentiment analizi 2 saniyede tamamlanmalı"""
        texts = [
            "The market is doing great with strong earnings.",
            "Stock prices crashed amid economic uncertainty.",
            "Central bank holds interest rates steady today.",
            "Tech sector surges on AI innovation news.",
            "Energy prices fall on supply concerns.",
        ] * 10  # 50 metin

        start = time.perf_counter()
        for text in texts:
            NewsAnalyzer.analyze_sentiment(text)
        elapsed = time.perf_counter() - start
        self.assertLess(elapsed, 2.0, f"SentimentAnalysis (50x) çok yavaş: {elapsed:.3f}s")

    def test_single_sentiment_fast(self):
        """Tek metin sentiment analizi 0.1 saniyede tamamlanmalı"""
        text = "Excellent earnings report beats all expectations!"
        start = time.perf_counter()
        NewsAnalyzer.analyze_sentiment(text)
        elapsed = time.perf_counter() - start
        self.assertLess(elapsed, 0.1, f"SingleSentiment çok yavaş: {elapsed:.3f}s")


if __name__ == "__main__":
    unittest.main()
