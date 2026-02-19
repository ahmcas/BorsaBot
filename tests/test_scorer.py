# ============================================================
# tests/test_scorer.py — Skor Hesaplama Testleri
# ============================================================

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
from scorer import ScoreCalculator, select_top_stocks, generate_recommendation_text, determine_rating


class TestScoreCalculator(unittest.TestCase):
    """ScoreCalculator sınıfı testleri"""

    def test_composite_score_range(self):
        """Composite skor 0-100 arasında olmalı"""
        score = ScoreCalculator.calculate_composite_score(75.0, 0.5)
        self.assertGreaterEqual(score, 0)
        self.assertLessEqual(score, 100)

    def test_composite_score_neutral_sentiment(self):
        """Sıfır sentiment ile teknik skor baskın olmalı"""
        score = ScoreCalculator.calculate_composite_score(70.0, 0.0)
        # Beklenti: (70 * 0.6) + (50 * 0.4) = 42 + 20 = 62
        self.assertAlmostEqual(score, 62.0, places=1)

    def test_composite_score_none_inputs(self):
        """None girişlerde çökmemeli"""
        score = ScoreCalculator.calculate_composite_score(None, None)
        self.assertIsNotNone(score)
        self.assertGreaterEqual(score, 0)
        self.assertLessEqual(score, 100)

    def test_confidence_levels(self):
        """Güven seviyeleri doğru atanmalı"""
        self.assertEqual(ScoreCalculator.calculate_confidence(85), "Çok Yüksek")
        self.assertEqual(ScoreCalculator.calculate_confidence(75), "Yüksek")
        self.assertEqual(ScoreCalculator.calculate_confidence(65), "İyi")
        self.assertEqual(ScoreCalculator.calculate_confidence(55), "Orta")
        self.assertEqual(ScoreCalculator.calculate_confidence(45), "Düşük")
        self.assertEqual(ScoreCalculator.calculate_confidence(30), "Çok Düşük")

    def test_reward_risk_calculation(self):
        """Reward/Risk hesabı doğru olmalı"""
        rr = ScoreCalculator.calculate_reward_risk(100, 90, 115)
        self.assertAlmostEqual(rr["reward_pct"], 15.0, places=1)
        self.assertAlmostEqual(rr["risk_pct"], 10.0, places=1)
        self.assertAlmostEqual(rr["ratio"], 1.5, places=1)

    def test_reward_risk_zero_price(self):
        """Sıfır fiyatta çökmemeli"""
        rr = ScoreCalculator.calculate_reward_risk(0, 0, 0)
        self.assertEqual(rr["ratio"], 0)


class TestSelectTopStocks(unittest.TestCase):
    """select_top_stocks() fonksiyon testleri"""

    def _make_result(self, ticker, score=60.0):
        return {
            "ticker": ticker,
            "score": score,
            "skip": False,
            "current_price": 100.0,
            "rsi": 50.0,
            "macd_histogram": 0.1,
            "bollinger_position": 0.5,
            "sma_short": 100.0,
            "sma_long": 95.0,
            "momentum_pct": 2.0,
            "trend": "Yukarı",
            "signals": [],
            "fibonacci": {},
            "dataframe": None,
        }

    def test_returns_list(self):
        """Fonksiyon liste döndürmeli"""
        results = [self._make_result("AAPL", 70), self._make_result("MSFT", 65)]
        selected = select_top_stocks(results, {}, max_count=5)
        self.assertIsInstance(selected, list)

    def test_max_count_respected(self):
        """max_count parametresi aşılmamalı"""
        results = [self._make_result(f"TICK{i}", 60) for i in range(10)]
        selected = select_top_stocks(results, {}, max_count=3)
        self.assertLessEqual(len(selected), 3)

    def test_skipped_excluded(self):
        """skip=True olan hisseler dahil edilmemeli"""
        results = [
            self._make_result("AAPL", 80),
            {"ticker": "SKIP", "score": 90, "skip": True},
        ]
        selected = select_top_stocks(results, {}, max_count=5)
        tickers = [s["ticker"] for s in selected]
        self.assertNotIn("SKIP", tickers)

    def test_sorted_by_score(self):
        """Seçilen hisseler skora göre azalan sıralanmalı"""
        results = [
            self._make_result("LOW", 50),
            self._make_result("HIGH", 80),
            self._make_result("MID", 65),
        ]
        selected = select_top_stocks(results, {}, max_count=3)
        scores = [s["score"] for s in selected]
        self.assertEqual(scores, sorted(scores, reverse=True))

    def test_sector_mapping_used(self):
        """BIST hisseleri için sektör doğru atanmalı"""
        results = [self._make_result("GARAN.IS", 70)]
        selected = select_top_stocks(results, {}, max_count=5)
        if selected:
            self.assertEqual(selected[0]["sector"], "finans")

    def test_empty_input(self):
        """Boş girişte boş liste döndürmeli"""
        selected = select_top_stocks([], {}, max_count=5)
        self.assertEqual(selected, [])


class TestDetermineRating(unittest.TestCase):
    """determine_rating() fonksiyon testleri"""

    def test_high_score_rating(self):
        self.assertIn("KAUFEN", determine_rating(85))

    def test_low_score_rating(self):
        self.assertIn("VERKAUFEN", determine_rating(20))

    def test_mid_score_rating(self):
        self.assertIn("HALTEN", determine_rating(65))


if __name__ == "__main__":
    unittest.main()
