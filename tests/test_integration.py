# ============================================================
# tests/test_integration.py — Entegrasyon Testleri
# ============================================================
# Kapsam: Full pipeline, Data flow, Module interactions
# ============================================================

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
from unittest.mock import patch, MagicMock
import pandas as pd
import numpy as np
import pytest

from technical_analyzer import TechnicalAnalyzer
from news_analyzer import NewsAnalyzer, GlobalSectorAnalyzer, analyze_news
from scorer import (
    ScoreCalculator,
    select_top_stocks,
    generate_recommendation_text,
    determine_rating,
)
from tests.conftest import make_price_series, make_ohlcv_df


# ─────────────────────────────────────────────
# Teknik Analiz → Skor Pipeline
# ─────────────────────────────────────────────

@pytest.mark.integration
class TestTechnicalToScorePipeline(unittest.TestCase):
    """Teknik analiz sonuçları scorer'a doğru aktarılmalı"""

    def _make_tech_result(self, ticker, tech_score):
        return {
            "ticker": ticker,
            "score": tech_score,
            "skip": False,
            "current_price": 100.0,
            "rsi": 50.0,
            "macd_histogram": 0.1,
            "macd_line": 0.2,
            "signal_line": 0.1,
            "bollinger_position": "orta",
            "bollinger_upper": 110.0,
            "bollinger_middle": 100.0,
            "bollinger_lower": 90.0,
            "sma_short": 100.0,
            "sma_long": 95.0,
            "momentum_pct": 2.0,
            "atr": 1.5,
            "trend": "Yukarı",
            "trend_strength": "Güçlü",
            "signals": ["RSI_BUY"],
            "fibonacci": {"fib_0.236": 108.0, "fib_0.618": 93.0},
            "breakout": {},
            "dataframe": None,
        }

    def test_technical_to_composite_score(self):
        """Teknik skor composite skora doğru entegre olmalı"""
        tech_score = 70.0
        sector_sentiment = 0.5
        composite = ScoreCalculator.calculate_composite_score(tech_score, sector_sentiment)
        self.assertGreater(composite, 0)
        self.assertLessEqual(composite, 100)

    def test_pipeline_produces_sorted_results(self):
        """Pipeline sonuçları skora göre sıralı olmalı"""
        results = [
            self._make_tech_result("A", 80),
            self._make_tech_result("B", 40),
            self._make_tech_result("C", 65),
        ]
        sector_scores = {"teknoloji": 0.5, "finans": 0.3}
        selected = select_top_stocks(results, sector_scores, max_count=5)
        if len(selected) >= 2:
            scores = [s["score"] for s in selected]
            self.assertEqual(scores, sorted(scores, reverse=True))

    def test_pipeline_excludes_skipped(self):
        """Skip=True olan hisseler pipeline sonucunda yer almamalı"""
        results = [
            self._make_tech_result("GOOD", 70),
            {"ticker": "BAD", "score": 95, "skip": True},
        ]
        selected = select_top_stocks(results, {}, max_count=5)
        tickers = [s["ticker"] for s in selected]
        self.assertNotIn("BAD", tickers)

    def test_full_pipeline_fields_present(self):
        """Tam pipeline sonucunda gerekli alanlar bulunmalı"""
        results = [self._make_tech_result("AAPL", 70)]
        selected = select_top_stocks(results, {"teknoloji": 0.7}, max_count=5)
        self.assertEqual(len(selected), 1)
        stock = selected[0]
        for field in ["ticker", "score", "current_price", "sector",
                      "support", "resistance", "reward_pct", "risk_pct"]:
            self.assertIn(field, stock, f"'{field}' alanı eksik")

    def test_recommendation_generated_from_selection(self):
        """Seçim sonuçlarından öneri metni oluşturulabilmeli"""
        results = [self._make_tech_result("MSFT", 72)]
        selected = select_top_stocks(results, {"teknoloji": 0.6}, max_count=5)
        rec_data = generate_recommendation_text(selected, {"teknoloji": 0.6})
        self.assertIn("recommendations", rec_data)
        self.assertIn("market_summary", rec_data)


# ─────────────────────────────────────────────
# Haber Analizi → Skor Entegrasyonu
# ─────────────────────────────────────────────

@pytest.mark.integration
class TestNewsToScoreIntegration(unittest.TestCase):
    """Haber sentiment'i skor hesaplamaya doğru entegre olmalı"""

    def test_sector_scores_affect_composite(self):
        """Yüksek sektör sentiment'i composite skoru artırmalı"""
        tech_score = 60.0
        high_sentiment = 0.9
        low_sentiment = -0.5

        high_composite = ScoreCalculator.calculate_composite_score(tech_score, high_sentiment)
        low_composite = ScoreCalculator.calculate_composite_score(tech_score, low_sentiment)

        self.assertGreater(high_composite, low_composite)

    def test_analyze_news_returns_dict(self):
        """analyze_news() dict döndürmeli"""
        with patch.object(NewsAnalyzer, "analyze_sector_news") as mock_analyze:
            mock_analyze.return_value = {
                "sector": "teknoloji",
                "sentiment_score": 0.7,
                "status": "success",
                "articles_count": 3,
            }
            result = analyze_news(days_back=1)
            self.assertIsInstance(result, dict)

    def test_analyze_news_contains_genel(self):
        """analyze_news() sonucunda 'genel' skoru bulunmalı"""
        with patch.object(NewsAnalyzer, "analyze_sector_news") as mock_analyze:
            mock_analyze.return_value = {
                "sector": "test",
                "sentiment_score": 0.0,
                "status": "no_data",
                "articles_count": 0,
            }
            result = analyze_news(days_back=1)
            self.assertIn("genel", result)

    def test_global_sector_analyzer_moods_are_floats(self):
        """GlobalSectorAnalyzer.get_all_moods() float değerler döndürmeli"""
        moods = GlobalSectorAnalyzer.get_all_moods()
        self.assertIsInstance(moods, dict)
        for sector, mood in moods.items():
            self.assertIsInstance(mood, float, f"{sector} için mood float değil")

    def test_sector_score_default_when_missing(self):
        """Eksik sektör için 0.0 fallback uygulanmalı"""
        tech_score = 65.0
        # Boş sector_scores ile composite hesapla
        composite = ScoreCalculator.calculate_composite_score(tech_score, 0.0)
        # Beklenen: (65 * 0.6) + (50 * 0.4) = 39 + 20 = 59
        self.assertAlmostEqual(composite, 59.0, delta=1.0)


# ─────────────────────────────────────────────
# Skor Hesaplama – Uçtan Uca Data Flow
# ─────────────────────────────────────────────

@pytest.mark.integration
class TestScoringDataFlow(unittest.TestCase):
    """Skor hesaplama data flow testleri"""

    def test_composite_score_formula(self):
        """Composite skor = (teknik * 0.6) + (news * 0.4) formülü"""
        tech = 70.0
        # Sentiment 0.5 → normalized_sentiment = (0.5+1)/2*100 = 75
        # Composite = 70*0.6 + 75*0.4 = 42 + 30 = 72
        composite = ScoreCalculator.calculate_composite_score(tech, 0.5)
        self.assertAlmostEqual(composite, 72.0, delta=0.1)

    def test_select_top_stocks_limits_count(self):
        """select_top_stocks max_count'u aşmamalı"""
        results = [
            {"ticker": f"T{i}", "score": float(80 - i), "skip": False,
             "current_price": 100.0, "rsi": 50.0, "macd_histogram": 0.1,
             "macd_line": 0.2, "signal_line": 0.1,
             "bollinger_position": "orta", "bollinger_upper": 110.0,
             "bollinger_middle": 100.0, "bollinger_lower": 90.0,
             "sma_short": 100.0, "sma_long": 95.0, "momentum_pct": 1.0,
             "atr": 1.5, "trend": "Yukarı", "trend_strength": "Güçlü",
             "signals": [], "fibonacci": {}, "breakout": {}, "dataframe": None}
            for i in range(10)
        ]
        selected = select_top_stocks(results, {}, max_count=3)
        self.assertLessEqual(len(selected), 3)

    def test_rating_matches_score_bucket(self):
        """Rating, skor aralığına göre doğru atanmalı"""
        self.assertIn("GÜÇLÜ AL", determine_rating(85))
        self.assertIn("AL", determine_rating(70))
        self.assertIn("TUT", determine_rating(55))
        self.assertIn("DİKKATLİ", determine_rating(40))
        self.assertIn("SAT", determine_rating(20))

    def test_recommendation_text_complete_pipeline(self):
        """Öneri metin üretimi tüm alanları içermeli"""
        stock = {
            "ticker": "NVDA", "score": 78.0,
            "current_price": 200.0, "sector": "Teknoloji",
            "support": 185.0, "resistance": 215.0,
            "reward_pct": 7.5, "risk_pct": 7.5, "reward_risk_ratio": 1.0,
            "rsi": 55.0, "macd_histogram": 0.3,
            "macd_line": 0.4, "signal_line": 0.1,
            "bollinger_position": "orta",
            "bollinger_upper": 220.0, "bollinger_middle": 200.0,
            "bollinger_lower": 180.0,
            "sma_short": 195.0, "sma_long": 185.0,
            "momentum_pct": 5.0, "atr": 3.0,
            "trend": "Yukarı", "trend_strength": "Güçlü",
            "signals": ["MACD_BUY"],
            "fibonacci": {"fib_0.236": 210.0, "fib_0.618": 190.0},
            "breakout": {}, "source_pool": "",
        }
        result = generate_recommendation_text([stock], {})
        rec = result["recommendations"][0]
        self.assertEqual(rec["ticker"], "NVDA")
        self.assertIn("confidence", rec)
        self.assertIn("rating", rec)
        self.assertIn("target_price", rec)
        self.assertIn("stop_loss", rec)

    def test_reward_risk_integrated_in_selection(self):
        """select_top_stocks sonucunda reward_risk_ratio mevcut olmalı"""
        result = {
            "ticker": "JPM", "score": 65.0, "skip": False,
            "current_price": 100.0, "rsi": 50.0, "macd_histogram": 0.1,
            "macd_line": 0.2, "signal_line": 0.1,
            "bollinger_position": "orta", "bollinger_upper": 110.0,
            "bollinger_middle": 100.0, "bollinger_lower": 90.0,
            "sma_short": 100.0, "sma_long": 95.0, "momentum_pct": 2.0,
            "atr": 1.5, "trend": "Yukarı", "trend_strength": "Güçlü",
            "signals": [], "fibonacci": {"fib_0.236": 108.0, "fib_0.618": 93.0},
            "breakout": {}, "dataframe": None,
        }
        selected = select_top_stocks([result], {"finans": 0.5}, max_count=5)
        if selected:
            self.assertIn("reward_risk_ratio", selected[0])


# ─────────────────────────────────────────────
# Teknik Gösterge Entegrasyon Testleri
# ─────────────────────────────────────────────

@pytest.mark.integration
class TestTechnicalIndicatorIntegration(unittest.TestCase):
    """Teknik göstergelerin birbirleriyle uyumu"""

    def test_rsi_macd_bollinger_consistent(self):
        """RSI, MACD, Bollinger aynı fiyat serisi için tutarlı çalışmalı"""
        prices = make_price_series(100)
        rsi = TechnicalAnalyzer.calculate_rsi(prices, period=14)
        macd = TechnicalAnalyzer.calculate_macd(prices)
        bollinger = TechnicalAnalyzer.calculate_bollinger_bands(prices, period=20)

        self.assertIsNotNone(rsi)
        self.assertIsNotNone(macd)
        self.assertIsNotNone(bollinger)
        # Hepsi 0'dan farklı değer üretmeli
        self.assertNotEqual(rsi, 0)
        self.assertNotEqual(bollinger.get("middle_band"), 0)

    def test_technical_score_uses_all_indicators(self):
        """Teknik skor hesaplaması tüm göstergeleri kullanmalı"""
        # Extreme bullish: RSI oversold, MACD pozitif, fiyat SMA üstünde
        score_bullish = TechnicalAnalyzer.calculate_technical_score(
            rsi=30, macd={"histogram": 0.5, "macd_line": 0.5, "signal_line": 0.0},
            bollinger={"position": "alt"}, sma20=95, sma50=90,
            momentum=12, price=100,
        )
        # Extreme bearish
        score_bearish = TechnicalAnalyzer.calculate_technical_score(
            rsi=75, macd={"histogram": -0.5, "macd_line": -0.3, "signal_line": 0.2},
            bollinger={"position": "üst"}, sma20=110, sma50=120,
            momentum=-12, price=100,
        )
        self.assertGreater(score_bullish, score_bearish)

    def test_sma_momentum_correlation(self):
        """Yükselen fiyatlarda SMA kısa > SMA uzun ve momentum pozitif olmalı"""
        rising = pd.Series(np.linspace(100, 130, 100))
        sma_short = TechnicalAnalyzer.calculate_sma(rising, period=10)
        sma_long = TechnicalAnalyzer.calculate_sma(rising, period=50)
        momentum = TechnicalAnalyzer.calculate_momentum(rising, period=20)

        self.assertGreater(sma_short, sma_long)
        self.assertGreater(momentum, 0)

    def test_analyze_trend_with_df(self):
        """analyze_trend() OHLCV DataFrame ile tutarlı sonuç döndürmeli"""
        df = make_ohlcv_df(100)
        trend_result = TechnicalAnalyzer.analyze_trend(df)
        self.assertIn("trend", trend_result)
        self.assertIn("strength", trend_result)
        self.assertIsInstance(trend_result["trend"], str)


if __name__ == "__main__":
    unittest.main()
