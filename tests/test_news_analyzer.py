# ============================================================
# tests/test_news_analyzer.py — Haber Analizi Testleri
# ============================================================
# Kapsam: Sentiment, Filter, RateLimiter, Cache
# ============================================================

import sys
import os
import time
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
import pytest

from news_analyzer import RateLimiter, CacheManager, NewsAnalyzer


# ─────────────────────────────────────────────
# RateLimiter Testleri
# ─────────────────────────────────────────────

@pytest.mark.unit
class TestRateLimiter(unittest.TestCase):
    """RateLimiter sınıfı testleri"""

    def test_initial_state_allows_request(self):
        """Yeni RateLimiter ilk istekle izin vermeli"""
        rl = RateLimiter(max_requests=10, period_hours=1)
        self.assertTrue(rl.can_request())

    def test_requests_remaining_full(self):
        """Yeni limiter tam kota ile başlamalı"""
        rl = RateLimiter(max_requests=10, period_hours=1)
        self.assertEqual(rl.requests_remaining(), 10)

    def test_add_request_decreases_remaining(self):
        """İstek eklenmesi kalan sayıyı azaltmalı"""
        rl = RateLimiter(max_requests=10, period_hours=1)
        rl.add_request()
        self.assertEqual(rl.requests_remaining(), 9)

    def test_exceeding_limit_blocks_requests(self):
        """Limiti aşan istek sayısında can_request False dönmeli"""
        rl = RateLimiter(max_requests=3, period_hours=1)
        for _ in range(3):
            rl.add_request()
        self.assertFalse(rl.can_request())

    def test_block_until_prevents_requests(self):
        """block_until() sonrası can_request False dönmeli"""
        rl = RateLimiter(max_requests=100, period_hours=1)
        rl.block_until(seconds=3600)
        self.assertFalse(rl.can_request())

    def test_requests_remaining_never_negative(self):
        """Kalan istek sayısı negatif olmamalı"""
        rl = RateLimiter(max_requests=2, period_hours=1)
        for _ in range(5):
            rl.add_request()
        self.assertGreaterEqual(rl.requests_remaining(), 0)

    def test_multiple_add_requests(self):
        """Birden fazla istek eklenmesi doğru sayılmalı"""
        rl = RateLimiter(max_requests=10, period_hours=1)
        for _ in range(5):
            rl.add_request()
        self.assertEqual(rl.requests_remaining(), 5)


# ─────────────────────────────────────────────
# CacheManager Testleri
# ─────────────────────────────────────────────

@pytest.mark.unit
class TestCacheManager(unittest.TestCase):
    """CacheManager sınıfı testleri"""

    def setUp(self):
        import tempfile
        self.tmp_dir = tempfile.mkdtemp()
        self.cache = CacheManager(cache_dir=self.tmp_dir, ttl_hours=1)

    def test_get_returns_none_on_miss(self):
        """Cache miss → None döndürmeli"""
        result = self.cache.get("nonexistent_key")
        self.assertIsNone(result)

    def test_set_and_get(self):
        """Cache'e kaydet ve geri al"""
        self.cache.set("test_key", {"value": 42})
        result = self.cache.get("test_key")
        self.assertIsNotNone(result)
        self.assertEqual(result["value"], 42)

    def test_cache_stores_list(self):
        """Liste verisi cache'lenebilmeli"""
        data = [1, 2, 3, "text"]
        self.cache.set("list_key", data)
        result = self.cache.get("list_key")
        self.assertEqual(result, data)

    def test_cache_stores_string(self):
        """String verisi cache'lenebilmeli"""
        self.cache.set("str_key", "hello world")
        result = self.cache.get("str_key")
        self.assertEqual(result, "hello world")

    def test_memory_cache_hit_fast(self):
        """Bellek cache'i disk cache'den daha hızlı olmalı"""
        data = {"big": "data" * 100}
        self.cache.set("speed_key", data)
        result = self.cache.get("speed_key")
        self.assertIsNotNone(result)

    def test_expired_cache_returns_none(self):
        """TTL geçen cache girişi None döndürmeli"""
        # TTL = 0 saat olan cache oluştur
        expired_cache = CacheManager(cache_dir=self.tmp_dir, ttl_hours=0)
        expired_cache.set("exp_key", "data")
        # Biraz bekle ve kontrol et
        time.sleep(0.1)
        result = expired_cache.get("exp_key")
        self.assertIsNone(result)

    def test_cache_key_is_hashed(self):
        """Cache anahtarı MD5 ile hash'lenmeli"""
        key = "test_key_for_hashing"
        cache_key = self.cache._get_cache_key(key)
        self.assertEqual(len(cache_key), 32)  # MD5 hex = 32 karakter

    def test_different_keys_different_hashes(self):
        """Farklı anahtarlar farklı hash'ler üretmeli"""
        h1 = self.cache._get_cache_key("key1")
        h2 = self.cache._get_cache_key("key2")
        self.assertNotEqual(h1, h2)

    def test_cache_overwrites_existing(self):
        """Aynı anahtara yeni veri kaydedilebilmeli"""
        self.cache.set("overwrite_key", "old_value")
        self.cache.set("overwrite_key", "new_value")
        result = self.cache.get("overwrite_key")
        self.assertEqual(result, "new_value")

    def test_memory_usage_returns_dict(self):
        """get_memory_usage() dict döndürmeli"""
        self.cache.set("key", "data")
        usage = self.cache.get_memory_usage()
        self.assertIsInstance(usage, dict)
        self.assertIn("cached_items", usage)
        self.assertIn("estimated_size_mb", usage)


# ─────────────────────────────────────────────
# NewsAnalyzer.analyze_sentiment() Testleri
# ─────────────────────────────────────────────

@pytest.mark.unit
class TestAnalyzeSentiment(unittest.TestCase):
    """NewsAnalyzer.analyze_sentiment() testleri"""

    def test_sentiment_range(self):
        """Sentiment -1.0 ile +1.0 arasında olmalı"""
        score = NewsAnalyzer.analyze_sentiment("The market is great today!")
        self.assertGreaterEqual(score, -1.0)
        self.assertLessEqual(score, 1.0)

    def test_positive_text_positive_score(self):
        """Pozitif metin pozitif sentiment üretmeli"""
        score = NewsAnalyzer.analyze_sentiment(
            "Excellent earnings! Strong growth! Amazing profits!"
        )
        self.assertGreater(score, 0)

    def test_negative_text_negative_score(self):
        """Negatif metin negatif sentiment üretmeli"""
        score = NewsAnalyzer.analyze_sentiment(
            "Terrible losses. Worst crash. Catastrophic failure."
        )
        self.assertLess(score, 0)

    def test_neutral_text_near_zero(self):
        """Nötr metin sıfıra yakın sentiment üretmeli"""
        score = NewsAnalyzer.analyze_sentiment("The meeting was held today.")
        self.assertAlmostEqual(score, 0.0, delta=0.4)

    def test_empty_text_returns_zero(self):
        """Boş metin 0.0 döndürmeli"""
        score = NewsAnalyzer.analyze_sentiment("")
        self.assertEqual(score, 0.0)

    def test_none_returns_zero(self):
        """None girişte 0.0 dönmeli"""
        score = NewsAnalyzer.analyze_sentiment(None)
        self.assertEqual(score, 0.0)

    def test_very_short_text_returns_zero(self):
        """Çok kısa metin (< 5 karakter) 0.0 dönmeli"""
        score = NewsAnalyzer.analyze_sentiment("Hi")
        self.assertEqual(score, 0.0)

    def test_sentiment_returns_float(self):
        """Sentiment float döndürmeli"""
        score = NewsAnalyzer.analyze_sentiment("Market rally continues.")
        self.assertIsInstance(score, float)

    def test_repeated_positive_words(self):
        """Tekrarlanan pozitif kelimeler yüksek skor üretmeli"""
        score = NewsAnalyzer.analyze_sentiment(
            "great great great excellent outstanding superb brilliant"
        )
        self.assertGreater(score, 0.5)


# ─────────────────────────────────────────────
# NewsAnalyzer.filter_articles() Testleri
# ─────────────────────────────────────────────

@pytest.mark.unit
class TestFilterArticles(unittest.TestCase):
    """NewsAnalyzer.filter_articles() testleri"""

    def _make_article(self, title="Test Title", description="Test Description",
                      published=None):
        from datetime import datetime, timedelta
        if published is None:
            # Son 3 gün içinde yayınlanmış makaleler (filtrelenmesin)
            published = (datetime.now() - timedelta(days=3)).strftime("%Y-%m-%dT%H:%M:%SZ")
        return {
            "title": title,
            "description": description,
            "publishedAt": published,
            "source": {"name": "Reuters"},
        }

    def test_returns_list(self):
        """filter_articles() liste döndürmeli"""
        articles = [self._make_article()]
        result = NewsAnalyzer.filter_articles(articles)
        self.assertIsInstance(result, list)

    def test_empty_input(self):
        """Boş liste girişinde boş liste dönmeli"""
        result = NewsAnalyzer.filter_articles([])
        self.assertEqual(result, [])

    def test_removes_articles_without_title(self):
        """Başlıksız makaleler filtrelenmeli"""
        articles = [
            {"title": None, "description": "desc", "publishedAt": "2026-01-01T10:00:00Z"},
        ]
        result = NewsAnalyzer.filter_articles(articles)
        self.assertEqual(len(result), 0)

    def test_removes_articles_without_description(self):
        """Açıklamasız makaleler filtrelenmeli"""
        articles = [
            {"title": "Title", "description": None, "publishedAt": "2026-01-01T10:00:00Z"},
        ]
        result = NewsAnalyzer.filter_articles(articles)
        self.assertEqual(len(result), 0)

    def test_keeps_valid_articles(self):
        """Geçerli makaleler korunmalı"""
        articles = [self._make_article() for _ in range(3)]
        result = NewsAnalyzer.filter_articles(articles)
        self.assertEqual(len(result), 3)

    def test_max_10_articles_returned(self):
        """Maksimum 10 makale döndürmeli"""
        articles = [self._make_article(title=f"Title {i}") for i in range(20)]
        result = NewsAnalyzer.filter_articles(articles)
        self.assertLessEqual(len(result), 10)

    def test_mixed_valid_invalid(self):
        """Karışık listede sadece geçerliler korunmalı"""
        articles = [
            self._make_article(),
            {"title": None, "description": "no title"},
            self._make_article(title="Second valid"),
        ]
        result = NewsAnalyzer.filter_articles(articles)
        self.assertEqual(len(result), 2)


# ─────────────────────────────────────────────
# GlobalSectorAnalyzer Testleri
# ─────────────────────────────────────────────

@pytest.mark.unit
class TestGlobalSectorAnalyzer(unittest.TestCase):
    """GlobalSectorAnalyzer sınıfı testleri"""

    def test_get_sector_mood_returns_float(self):
        """get_sector_mood() float döndürmeli"""
        from news_analyzer import GlobalSectorAnalyzer
        mood = GlobalSectorAnalyzer.get_sector_mood("teknoloji")
        self.assertIsInstance(mood, float)

    def test_get_sector_mood_range(self):
        """Sektör mood -1 ile +1 arasında olmalı"""
        from news_analyzer import GlobalSectorAnalyzer
        for sector in ["teknoloji", "finans", "enerji", "sağlık"]:
            mood = GlobalSectorAnalyzer.get_sector_mood(sector)
            self.assertGreaterEqual(mood, -1.0)
            self.assertLessEqual(mood, 1.0)

    def test_get_sector_mood_unknown_sector(self):
        """Bilinmeyen sektör için fallback döndürmeli"""
        from news_analyzer import GlobalSectorAnalyzer
        mood = GlobalSectorAnalyzer.get_sector_mood("bilinmeyen_sektor_xyz")
        self.assertIsInstance(mood, float)


# ─────────────────────────────────────────────
# NewsAnalyzer.get_news() – API sıfırlama testi
# ─────────────────────────────────────────────

@pytest.mark.unit
class TestGetNewsNoApiKey(unittest.TestCase):
    """API anahtarı olmadan get_news() boş liste döndürmeli"""

    def test_no_api_key_returns_empty(self):
        """API anahtarı placeholder iken boş liste dönmeli"""
        from unittest.mock import patch
        import config as cfg
        original_key = cfg.NEWS_API_KEY
        try:
            cfg.NEWS_API_KEY = "YOUR_NEWS_API_KEY_HERE"
            result = NewsAnalyzer.get_news("technology", days_back=1, use_cache=False)
            self.assertIsInstance(result, list)
            self.assertEqual(len(result), 0)
        finally:
            cfg.NEWS_API_KEY = original_key


if __name__ == "__main__":
    unittest.main()
