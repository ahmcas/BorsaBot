# ============================================================
# tests/test_scorer.py — Skor Hesaplama Testleri
# ============================================================

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
from scorer import ScoreCalculator, select_top_stocks, generate_recommendation_text, determine_rating, find_strongest_level


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
            "macd_line": 0.2,
            "signal_line": 0.1,
            "bollinger_position": 0.5,
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

    def test_technical_fields_passed_through(self):
        """Teknik gösterge alanları candidate dict'ine aktarılmalı"""
        results = [self._make_result("AAPL", 70)]
        selected = select_top_stocks(results, {}, max_count=5)
        self.assertEqual(len(selected), 1)
        stock = selected[0]
        self.assertIn("rsi", stock)
        self.assertIn("macd_histogram", stock)
        self.assertIn("sma_short", stock)
        self.assertIn("fibonacci", stock)
        self.assertIn("trend", stock)
        self.assertIn("signals", stock)
        self.assertIn("current_price", stock)
        self.assertEqual(stock["rsi"], 50.0)
        self.assertEqual(stock["current_price"], 100.0)
        self.assertEqual(stock["signals"], ["RSI_BUY"])


class TestGenerateRecommendationText(unittest.TestCase):
    """generate_recommendation_text() fonksiyon testleri"""

    def _make_stock(self, ticker, score=65.0):
        return {
            "ticker": ticker,
            "score": score,
            "current_price": 100.0,
            "sector": "Teknoloji",
            "support": 93.0,
            "resistance": 108.0,
            "reward_pct": 8.0,
            "risk_pct": 7.0,
            "reward_risk_ratio": 1.14,
            "rsi": 52.0,
            "macd_histogram": 0.1,
            "macd_line": 0.2,
            "signal_line": 0.1,
            "bollinger_position": 0.5,
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
            "fibonacci": {"fib_0.236": 108.0},
            "breakout": {},
            "source_pool": "",
        }

    def test_rec_fields_present(self):
        """rec dict'inde teknik gösterge ve ek alanlar mevcut olmalı"""
        stocks = [self._make_stock("AAPL", 65)]
        result = generate_recommendation_text(stocks, {})
        rec = result["recommendations"][0]
        for field in ["rsi", "macd_histogram", "sma_short", "fibonacci", "trend", "signals",
                      "confidence", "target_price", "stop_loss", "timeframe",
                      "reward_pct", "risk_pct", "expected_gain_pct", "max_risk_pct"]:
            self.assertIn(field, rec, msg=f"'{field}' alanı rec dict'inde eksik")

    def test_market_summary_present(self):
        """market_summary döndürülmeli ve doğru alanları içermeli"""
        stocks = [self._make_stock("AAPL", 70), self._make_stock("MSFT", 35)]
        result = generate_recommendation_text(stocks, {})
        self.assertIn("market_summary", result)
        ms = result["market_summary"]
        for key in ["bullish_count", "bearish_count", "neutral_count", "avg_score", "total_analyzed"]:
            self.assertIn(key, ms, msg=f"'{key}' market_summary'de eksik")

    def test_market_summary_counts(self):
        """bullish/bearish/neutral sayıları doğru hesaplanmalı"""
        stocks = [
            self._make_stock("A", 70),  # bullish (>=60)
            self._make_stock("B", 55),  # neutral (40-60)
            self._make_stock("C", 30),  # bearish (<40)
        ]
        result = generate_recommendation_text(stocks, {})
        ms = result["market_summary"]
        self.assertEqual(ms["bullish_count"], 1)
        self.assertEqual(ms["neutral_count"], 1)
        self.assertEqual(ms["bearish_count"], 1)

    def test_total_analyzed_uses_candidates(self):
        """candidates verilmişse total_analyzed onun uzunluğu olmalı"""
        stocks = [self._make_stock("AAPL", 65)]
        candidates = [self._make_stock(f"T{i}", 60) for i in range(10)]
        result = generate_recommendation_text(stocks, {}, candidates=candidates)
        self.assertEqual(result["market_summary"]["total_analyzed"], 10)

    def test_confidence_field(self):
        """confidence alanı doğru hesaplanmalı"""
        stocks = [self._make_stock("AAPL", 75)]
        result = generate_recommendation_text(stocks, {})
        rec = result["recommendations"][0]
        self.assertEqual(rec["confidence"], "Yüksek")


class TestDetermineRating(unittest.TestCase):
    """determine_rating() fonksiyon testleri"""

    def test_high_score_rating(self):
        self.assertIn("GÜÇLÜ AL", determine_rating(85))

    def test_low_score_rating(self):
        self.assertIn("SAT", determine_rating(20))

    def test_mid_score_rating(self):
        self.assertIn("TUT", determine_rating(65))


class TestFindStrongestLevel(unittest.TestCase):
    """find_strongest_level() fonksiyon testleri"""

    def test_returns_none_when_no_candidates(self):
        """Uygun seviye yoksa None döndürmeli"""
        # Tüm seviyeler fiyatın üstünde → destek yok
        levels = [{"price": 110.0, "source": "A"}, {"price": 120.0, "source": "B"}]
        result = find_strongest_level(levels, 100.0, direction="support")
        self.assertIsNone(result)

    def test_returns_none_for_empty_levels(self):
        """Boş levels listesinde None döndürmeli"""
        result = find_strongest_level([], 100.0, direction="support")
        self.assertIsNone(result)

    def test_single_support_returned(self):
        """Tek destekte o seviye dönmeli"""
        levels = [{"price": 90.0, "source": "Fibonacci fib_0.618"}]
        result = find_strongest_level(levels, 100.0, direction="support")
        self.assertIsNotNone(result)
        self.assertAlmostEqual(result["price"], 90.0, places=1)
        self.assertEqual(result["strength"], 1)

    def test_single_resistance_returned(self):
        """Tek dirençte o seviye dönmeli"""
        levels = [{"price": 110.0, "source": "Fibonacci fib_0.236"}]
        result = find_strongest_level(levels, 100.0, direction="resistance")
        self.assertIsNotNone(result)
        self.assertAlmostEqual(result["price"], 110.0, places=1)

    def test_confluence_cluster_chosen_over_single(self):
        """Birden fazla gösterge buluşan küme, tek göstergeli kümeden önce gelmeli"""
        # 93 ve 94 → aynı küme (±%2 içinde), 98 → tek başına
        levels = [
            {"price": 93.0, "source": "Fibonacci fib_0.618"},
            {"price": 94.0, "source": "Bollinger Alt"},
            {"price": 98.0, "source": "SMA Kısa"},
        ]
        result = find_strongest_level(levels, 100.0, direction="support")
        self.assertIsNotNone(result)
        self.assertEqual(result["strength"], 2)
        # Ortalama fiyat ~93.5
        self.assertAlmostEqual(result["price"], 93.5, places=1)

    def test_closer_cluster_chosen_when_equal_strength(self):
        """Aynı güçte iki küme varsa fiyata daha yakın olan seçilmeli"""
        levels = [
            {"price": 96.0, "source": "A"},  # closer
            {"price": 90.0, "source": "B"},  # farther
        ]
        result = find_strongest_level(levels, 100.0, direction="support")
        self.assertIsNotNone(result)
        self.assertAlmostEqual(result["price"], 96.0, places=1)

    def test_direction_resistance_filters_above_price(self):
        """Direnç seçiminde yalnızca fiyat üstündeki seviyeler değerlendirilmeli"""
        levels = [
            {"price": 90.0, "source": "Destek"},
            {"price": 108.0, "source": "Direnç"},
        ]
        result = find_strongest_level(levels, 100.0, direction="resistance")
        self.assertIsNotNone(result)
        self.assertAlmostEqual(result["price"], 108.0, places=1)

    def test_result_has_required_keys(self):
        """Sonuç dict'inde price, strength, sources, distance anahtarları olmalı"""
        levels = [{"price": 93.0, "source": "Fibonacci fib_0.618"}]
        result = find_strongest_level(levels, 100.0, direction="support")
        for key in ["price", "strength", "sources", "distance"]:
            self.assertIn(key, result)

    def test_tolerance_grouping(self):
        """±%2 tolerans içindeki seviyeler aynı kümede toplanmalı"""
        # 100 * 0.02 = 2 → 93 ile 94.8 arası (%2 içinde)
        levels = [
            {"price": 93.0, "source": "Fibonacci fib_0.618"},
            {"price": 94.5, "source": "SMA Uzun"},   # 93 * 1.02 = 94.86 → içinde
            {"price": 96.0, "source": "Bollinger Alt"},  # 93 * 1.02 = 94.86 → dışında
        ]
        result = find_strongest_level(levels, 100.0, direction="support")
        # En güçlü küme 93+94.5 (strength=2) olmalı
        self.assertEqual(result["strength"], 2)


if __name__ == "__main__":
    unittest.main()
