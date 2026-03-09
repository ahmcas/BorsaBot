# ============================================================
# tests/conftest.py — Reusable Fixtures & Mocks
# ============================================================

import sys
import os
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
import pandas as pd
import numpy as np


# ─────────────────────────────────────────────
# Yardımcı veri üreticiler
# ─────────────────────────────────────────────

def make_price_series(n: int = 100, start: float = 100.0, seed: int = 42) -> pd.Series:
    """Tekrarlanabilir fiyat serisi üret."""
    rng = np.random.default_rng(seed)
    returns = rng.normal(0.001, 0.015, n)
    prices = start * np.cumprod(1 + returns)
    index = pd.date_range(end="2026-01-01", periods=n, freq="B")
    return pd.Series(prices, index=index, name="close")


def make_ohlcv_df(n: int = 100, start: float = 100.0, seed: int = 42) -> pd.DataFrame:
    """OHLCV DataFrame üret."""
    close = make_price_series(n, start, seed)
    rng = np.random.default_rng(seed + 1)
    high = close * (1 + rng.uniform(0.001, 0.02, n))
    low = close * (1 - rng.uniform(0.001, 0.02, n))
    volume = rng.integers(100_000, 1_000_000, n).astype(float)
    return pd.DataFrame({
        "close": close.values,
        "high": high,
        "low": low,
        "volume": volume,
    }, index=close.index)


# ─────────────────────────────────────────────
# Teknik Analiz Fixture'ları
# ─────────────────────────────────────────────

@pytest.fixture
def price_series():
    """100 günlük fiyat serisi."""
    return make_price_series(100)


@pytest.fixture
def long_price_series():
    """250 günlük fiyat serisi (RSI/MACD/SMA için yeterli)."""
    return make_price_series(250)


@pytest.fixture
def ohlcv_df():
    """100 günlük OHLCV DataFrame."""
    return make_ohlcv_df(100)


@pytest.fixture
def long_ohlcv_df():
    """250 günlük OHLCV DataFrame."""
    return make_ohlcv_df(250)


# ─────────────────────────────────────────────
# Scorer Fixture'ları
# ─────────────────────────────────────────────

@pytest.fixture
def base_technical_result():
    """Tek bir teknik analiz sonucu."""
    return {
        "ticker": "AAPL",
        "score": 65.0,
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


@pytest.fixture
def multi_stock_results():
    """Birden fazla teknik analiz sonucu."""
    def _make(ticker, score, skip=False):
        return {
            "ticker": ticker,
            "score": score,
            "skip": skip,
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
            "signals": [],
            "fibonacci": {"fib_0.236": 108.0, "fib_0.618": 93.0},
            "breakout": {},
            "dataframe": None,
        }

    return [
        _make("AAPL", 80.0),
        _make("MSFT", 70.0),
        _make("GOOGL", 60.0),
        _make("GARAN.IS", 55.0),
        _make("SKIP_ME", 90.0, skip=True),
    ]


@pytest.fixture
def sector_scores():
    """Örnek sektör sentiment skorları."""
    return {
        "teknoloji": 0.7,
        "finans": 0.5,
        "enerji": 0.3,
        "sağlık": 0.4,
        "perakende": 0.2,
    }


# ─────────────────────────────────────────────
# Haber Analizi Fixture'ları
# ─────────────────────────────────────────────

@pytest.fixture
def sample_articles():
    """Örnek haber makaleleri."""
    return [
        {
            "title": "Tech stocks surge as AI boom continues",
            "description": "Technology stocks rallied sharply on strong earnings.",
            "publishedAt": "2026-01-01T10:00:00Z",
            "source": {"name": "Reuters"},
        },
        {
            "title": "Market falls amid recession fears",
            "description": "Stocks declined as economic data disappointed investors.",
            "publishedAt": "2026-01-01T09:00:00Z",
            "source": {"name": "Bloomberg"},
        },
        {
            "title": "Central bank holds rates steady",
            "description": "The central bank kept interest rates unchanged at its meeting.",
            "publishedAt": "2026-01-01T08:00:00Z",
            "source": {"name": "AP News"},
        },
    ]


@pytest.fixture
def empty_articles():
    """Boş makale listesi."""
    return []


# ─────────────────────────────────────────────
# Cache / Rate Limiter Fixture'ları
# ─────────────────────────────────────────────

@pytest.fixture
def fresh_rate_limiter():
    """Sıfırdan RateLimiter örneği."""
    from news_analyzer import RateLimiter
    return RateLimiter(max_requests=10, period_hours=1)


@pytest.fixture
def fresh_cache(tmp_path):
    """Geçici dizinde CacheManager örneği."""
    from news_analyzer import CacheManager
    return CacheManager(cache_dir=str(tmp_path / "cache"), ttl_hours=1)
