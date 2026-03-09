# ============================================================
# tests/test_e2e.py — Uçtan Uca (E2E) Testleri
# ============================================================
# Kapsam: Tam iş akışı simülasyonu (ağ çağrısı yok)
# ============================================================

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
from unittest.mock import patch, MagicMock
import pandas as pd
import numpy as np
import pytest

from technical_analyzer import TechnicalAnalyzer, analyze_all_stocks
from news_analyzer import NewsAnalyzer, GlobalSectorAnalyzer, analyze_news
from scorer import (
    ScoreCalculator,
    select_top_stocks,
    generate_recommendation_text,
    determine_rating,
)
from tests.conftest import make_price_series, make_ohlcv_df


# ─────────────────────────────────────────────
# Yardımcı Mock Fabrikaları
# ─────────────────────────────────────────────

def _make_mock_stock_data(ticker: str, n: int = 100) -> dict:
    """Mock teknik analiz sonucu üret."""
    df = make_ohlcv_df(n, seed=hash(ticker) % 1000)
    prices = df["close"]
    rsi = TechnicalAnalyzer.calculate_rsi(pd.Series(prices), period=14)
    macd = TechnicalAnalyzer.calculate_macd(pd.Series(prices))
    bollinger = TechnicalAnalyzer.calculate_bollinger_bands(pd.Series(prices), period=20)
    sma_short = TechnicalAnalyzer.calculate_sma(pd.Series(prices), period=10)
    sma_long = TechnicalAnalyzer.calculate_sma(pd.Series(prices), period=50)
    momentum = TechnicalAnalyzer.calculate_momentum(pd.Series(prices), period=10)
    score = TechnicalAnalyzer.calculate_technical_score(
        rsi, macd, bollinger, sma_short, sma_long, momentum, float(prices.iloc[-1])
    )
    fib = TechnicalAnalyzer.calculate_fibonacci(df, lookback=60)
    return {
        "ticker": ticker,
        "skip": False,
        "source": "historical",
        "current_price": round(float(prices.iloc[-1]), 2),
        "score": score,
        "rsi": rsi,
        "macd_histogram": macd.get("histogram"),
        "macd_line": macd.get("macd_line"),
        "signal_line": macd.get("signal_line"),
        "bollinger_position": bollinger.get("position"),
        "bollinger_upper": bollinger.get("upper_band"),
        "bollinger_middle": bollinger.get("middle_band"),
        "bollinger_lower": bollinger.get("lower_band"),
        "sma_short": sma_short,
        "sma_long": sma_long,
        "momentum_pct": momentum,
        "atr": 1.5,
        "trend": "Yukarı",
        "trend_strength": "Güçlü",
        "signals": ["RSI_BUY"],
        "fibonacci": fib,
        "breakout": {},
        "dataframe": df,
        "source_pool": "e2e_test",
    }


# ─────────────────────────────────────────────
# E2E Test 1: Tam analiz pipeline
# ─────────────────────────────────────────────

@pytest.mark.e2e
class TestFullAnalysisPipeline(unittest.TestCase):
    """Tam analiz pipeline'ı (teknik → skor → öneri)"""

    def setUp(self):
        self.tickers = ["AAPL", "MSFT", "GOOGL", "GARAN.IS", "AKBNK.IS"]
        self.tech_results = [_make_mock_stock_data(t) for t in self.tickers]
        self.sector_scores = {
            "teknoloji": 0.7,
            "finans": 0.5,
            "enerji": 0.3,
            "sağlık": 0.4,
            "perakende": 0.2,
        }

    def test_pipeline_produces_results(self):
        """Pipeline en az bir sonuç üretmeli"""
        selected = select_top_stocks(self.tech_results, self.sector_scores, max_count=3)
        self.assertGreater(len(selected), 0)

    def test_pipeline_max_count_respected(self):
        """Pipeline max_count parametresine uymalı"""
        selected = select_top_stocks(self.tech_results, self.sector_scores, max_count=2)
        self.assertLessEqual(len(selected), 2)

    def test_recommendation_text_generated(self):
        """Pipeline sonunda öneri metni oluşturulabilmeli"""
        selected = select_top_stocks(self.tech_results, self.sector_scores, max_count=3)
        rec_data = generate_recommendation_text(selected, self.sector_scores, self.tech_results)
        self.assertIn("recommendations", rec_data)
        self.assertIn("market_summary", rec_data)
        self.assertGreater(len(rec_data["recommendations"]), 0)

    def test_each_recommendation_has_required_fields(self):
        """Her öneri gerekli alanları içermeli"""
        selected = select_top_stocks(self.tech_results, self.sector_scores, max_count=3)
        rec_data = generate_recommendation_text(selected, self.sector_scores)
        for rec in rec_data["recommendations"]:
            for field in ["ticker", "score", "rating", "confidence",
                          "target_price", "stop_loss", "timeframe",
                          "rsi", "macd_histogram", "signals"]:
                self.assertIn(field, rec, f"'{field}' alanı öneri dict'inde eksik")

    def test_market_summary_totals_correct(self):
        """Market summary toplamları doğru olmalı"""
        selected = select_top_stocks(self.tech_results, self.sector_scores, max_count=5)
        rec_data = generate_recommendation_text(selected, self.sector_scores)
        ms = rec_data["market_summary"]
        total = ms["bullish_count"] + ms["bearish_count"] + ms["neutral_count"]
        self.assertEqual(total, len(rec_data["recommendations"]))


# ─────────────────────────────────────────────
# E2E Test 2: Haber analizi pipeline
# ─────────────────────────────────────────────

@pytest.mark.e2e
class TestNewsAnalysisPipeline(unittest.TestCase):
    """Haber analizi pipeline (mock API)"""

    def test_analyze_news_fallback_pipeline(self):
        """API başarısız olduğunda fallback pipeline çalışmalı"""
        # Rate limiter'ı sıfırla (API çağrısına izin ver ama mock yap)
        with patch.object(NewsAnalyzer, "analyze_sector_news") as mock_sector:
            mock_sector.return_value = {
                "sector": "teknoloji",
                "sentiment_score": 0.6,
                "status": "success",
                "articles_count": 3,
            }
            result = analyze_news(days_back=1)
            self.assertIsInstance(result, dict)
            self.assertGreater(len(result), 0)

    def test_sector_scores_all_present(self):
        """Tüm sektör skorları pipeline sonucunda mevcut olmalı"""
        with patch.object(NewsAnalyzer, "analyze_sector_news") as mock_sector:
            mock_sector.return_value = {
                "sector": "test",
                "sentiment_score": 0.0,
                "status": "no_data",
                "articles_count": 0,
            }
            result = analyze_news(days_back=1)
            # Primary + secondary sektörler + genel bulunmalı
            for sector in ["teknoloji", "finans", "enerji", "sağlık", "genel"]:
                self.assertIn(sector, result, f"'{sector}' sektörü pipeline sonucunda eksik")

    def test_sentiment_affects_composite_score(self):
        """Farklı sentiment değerleri farklı composite skorlar üretmeli"""
        tech_score = 65.0
        scores = [
            ScoreCalculator.calculate_composite_score(tech_score, sent)
            for sent in [-0.5, 0.0, 0.5, 1.0]
        ]
        # Artan sentiment artan skor üretmeli
        for i in range(len(scores) - 1):
            self.assertLessEqual(scores[i], scores[i + 1])


# ─────────────────────────────────────────────
# E2E Test 3: analyze_all_stocks mock testi
# ─────────────────────────────────────────────

@pytest.mark.e2e
class TestAnalyzeAllStocksE2E(unittest.TestCase):
    """analyze_all_stocks() fonksiyonu mock ile E2E testi"""

    def test_analyze_all_stocks_returns_list(self):
        """analyze_all_stocks() liste döndürmeli"""
        mock_result = _make_mock_stock_data("AAPL")
        with patch.object(TechnicalAnalyzer, "analyze_single_stock", return_value=mock_result):
            results = analyze_all_stocks(["AAPL", "MSFT"])
            self.assertIsInstance(results, list)
            self.assertEqual(len(results), 2)

    def test_analyze_all_stocks_includes_all_tickers(self):
        """Her ticker için bir sonuç döndürmeli"""
        tickers = ["AAPL", "MSFT", "GOOGL"]

        def side_effect(ticker):
            return _make_mock_stock_data(ticker)

        with patch.object(TechnicalAnalyzer, "analyze_single_stock", side_effect=side_effect):
            results = analyze_all_stocks(tickers)
            result_tickers = [r["ticker"] for r in results]
            for t in tickers:
                self.assertIn(t, result_tickers)

    def test_full_e2e_workflow(self):
        """Tam E2E iş akışı: analiz → skor → öneri"""
        tickers = ["AAPL", "MSFT", "NVDA"]

        def side_effect(ticker):
            return _make_mock_stock_data(ticker)

        with patch.object(TechnicalAnalyzer, "analyze_single_stock", side_effect=side_effect):
            # 1. Teknik analiz
            tech_results = analyze_all_stocks(tickers)
            self.assertGreater(len(tech_results), 0)

            # 2. Haber analizi (mock)
            sector_scores = GlobalSectorAnalyzer.get_all_moods()
            self.assertIsInstance(sector_scores, dict)

            # 3. Skor seçimi
            selected = select_top_stocks(tech_results, sector_scores, max_count=3)
            self.assertIsInstance(selected, list)

            # 4. Öneri üretimi
            rec_data = generate_recommendation_text(selected, sector_scores, tech_results)
            self.assertIn("recommendations", rec_data)
            self.assertIn("market_summary", rec_data)


if __name__ == "__main__":
    unittest.main()
