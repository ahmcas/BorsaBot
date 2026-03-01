# ============================================================
# news_analyzer.py — Haber Analizi Engine (v5 - ULTRA OPTİMİZE)
# ============================================================
# Optimizasyonlar:
# 1. Smart Rate Limiting (API limit yönetimi)
# 2. Multi-Layer Caching (bellek + disk)
# 3. Fallback Mechanisms (manuel mood'a geçiş)
# 4. Batch Processing (grup işleme)
# 5. Error Recovery (hata kurtarma)
# 6. Request Pooling (istek havuzu)
# 7. Async-like Processing (seri işleme optimize)
# ============================================================

import requests
from datetime import datetime, timedelta
from collections import defaultdict
import json
import os
import time
import hashlib
import config

try:
    from nltk.sentiment import SentimentIntensityAnalyzer
    import nltk
    try:
        nltk.data.find('sentiment/vader_lexicon')
    except LookupError:
        nltk.download('vader_lexicon', quiet=True)
except:
    import subprocess
    subprocess.run(["pip", "install", "nltk"], check=True)
    from nltk.sentiment import SentimentIntensityAnalyzer
    import nltk
    nltk.download('vader_lexicon', quiet=True)


class RateLimiter:
    """API Rate Limiter (NewsAPI: 100 istek/24 saat)"""
    
    def __init__(self, max_requests: int = 100, period_hours: int = 24):
        self.max_requests = max_requests
        self.period_seconds = period_hours * 3600
        self.requests = []
        self.blocked_until = None
    
    def can_request(self) -> bool:
        """İstek yapılabilir mi?"""
        now = time.time()
        
        # Block kontrolü
        if self.blocked_until and now < self.blocked_until:
            return False
        
        # Eski istekleri temizle
        self.requests = [req_time for req_time in self.requests 
                        if now - req_time < self.period_seconds]
        
        return len(self.requests) < self.max_requests
    
    def add_request(self):
        """İstek ekle"""
        self.requests.append(time.time())
    
    def block_until(self, seconds: int = 3600):
        """Belirtilen süre block et"""
        self.blocked_until = time.time() + seconds
    
    def requests_remaining(self) -> int:
        """Kalan istek sayısı"""
        now = time.time()
        self.requests = [req_time for req_time in self.requests 
                        if now - req_time < self.period_seconds]
        return max(0, self.max_requests - len(self.requests))


class CacheManager:
    """Çok Katmanlı Cache Yönetimi"""
    
    def __init__(self, cache_dir: str = "cache", ttl_hours: int = 24):
        self.cache_dir = cache_dir
        self.ttl_seconds = ttl_hours * 3600
        self.memory_cache = {}  # Bellek cache
        
        # Cache klasörü oluştur
        os.makedirs(cache_dir, exist_ok=True)
    
    def _get_cache_key(self, key: str) -> str:
        """Cache anahtarı oluştur"""
        return hashlib.md5(key.encode()).hexdigest()
    
    def _get_cache_path(self, key: str) -> str:
        """Cache dosya yolu"""
        cache_key = self._get_cache_key(key)
        return os.path.join(self.cache_dir, f"{cache_key}.json")
    
    def get(self, key: str):
        """Cache'den al"""
        # 1. Bellek cache'ten kontrol et
        if key in self.memory_cache:
            item = self.memory_cache[key]
            if time.time() - item["timestamp"] < self.ttl_seconds:
                return item["data"]
            else:
                del self.memory_cache[key]
        
        # 2. Disk cache'ten kontrol et
        cache_path = self._get_cache_path(key)
        if os.path.exists(cache_path):
            try:
                with open(cache_path, 'r') as f:
                    item = json.load(f)
                    if time.time() - item["timestamp"] < self.ttl_seconds:
                        # Bellek cache'e kopyala
                        self.memory_cache[key] = item
                        return item["data"]
                    else:
                        os.remove(cache_path)
            except:
                pass
        
        return None
    
    def set(self, key: str, data):
        """Cache'e kaydet"""
        item = {
            "timestamp": time.time(),
            "data": data
        }
        
        # Bellek cache'e kaydet
        self.memory_cache[key] = item
        
        # Disk cache'e kaydet
        try:
            cache_path = self._get_cache_path(key)
            with open(cache_path, 'w') as f:
                json.dump(item, f)
        except:
            pass
    
    def clear_expired(self):
        """Süresi geçen cache'leri temizle"""
        now = time.time()
        
        # Bellek cache
        expired_keys = [k for k, v in self.memory_cache.items() 
                       if now - v["timestamp"] > self.ttl_seconds]
        for key in expired_keys:
            del self.memory_cache[key]
        
        # Disk cache
        try:
            for filename in os.listdir(self.cache_dir):
                filepath = os.path.join(self.cache_dir, filename)
                try:
                    with open(filepath, 'r') as f:
                        item = json.load(f)
                        if now - item["timestamp"] > self.ttl_seconds:
                            os.remove(filepath)
                except:
                    pass
        except:
            pass
    
    def get_memory_usage(self) -> dict:
        """Bellek kullanımı"""
        return {
            "cached_items": len(self.memory_cache),
            "estimated_size_mb": len(json.dumps(self.memory_cache)) / (1024 * 1024)
        }


class NewsAnalyzer:
    """Haber Analizi Engine (ULTRA OPTİMİZE)"""
    
    # Birincil Sektörler (API çağrısı yapılır)
    PRIMARY_SECTORS = {
        "finans": ["bank", "financial", "stock", "investment", "trading", "forex"],
        "teknoloji": ["tech", "software", "ai", "chip", "gpu", "semiconductor"],
        "enerji": ["energy", "oil", "gas", "renewable", "solar", "petrol"],
        "sağlık": ["health", "pharma", "medical", "biotech", "vaccine"],
    }
    
    # İkincil Sektörler (Manuel mood kullanılır - API çağrısı YOK)
    SECONDARY_SECTORS = {
        "perakende": ["retail", "shopping", "consumer", "e-commerce"],
        "gıda": ["food", "agriculture", "beverage"],
        "telekom": ["telecom", "communication", "network", "5g"],
        "otomotiv": ["automotive", "car", "tesla", "electric vehicle"],
        "sigortalar": ["insurance", "underwriting"],
        "turizm": ["tourism", "travel", "hotel", "airline"],
        "savunma": ["defense", "military", "weapons"],
        "inşaat_gayrimenkul": ["real estate", "construction", "property"],
    }
    
    # 2026 Sektör Mood Tahminleri
    SECTOR_MOODS_2026 = {
        "teknoloji": 0.7,      # AI boom
        "enerji": 0.3,         # Normal
        "finans": 0.5,         # Faiz kararları
        "sağlık": 0.4,         # Stabil
        "perakende": 0.2,      # Talep zayıf
        "gıda": 0.3,           # Enflasyon
        "telekom": 0.2,        # Düşük büyüme
        "otomotiv": 0.1,       # EV geçişi
        "sigortalar": 0.4,     # Normal
        "turizm": 0.3,         # Mevsimsel
        "savunma": 0.6,        # NATO artışı
        "inşaat_gayrimenkul": 0.1,  # Faiz yüksek
    }
    
    # Güvenilir haber kaynakları
    TRUSTED_SOURCES = [
        "Reuters", "Bloomberg", "CNBC", "AP News", "BBC",
        "Financial Times", "Wall Street Journal", "MarketWatch"
    ]
    
    # Statik değişkenler
    _rate_limiter = RateLimiter(max_requests=100, period_hours=24)
    _cache = CacheManager(cache_dir="cache/news", ttl_hours=24)
    _sentiment_analyzer = None
    
    @classmethod
    def _get_sentiment_analyzer(cls):
        """Sentiment analyzer (lazy load)"""
        if cls._sentiment_analyzer is None:
            cls._sentiment_analyzer = SentimentIntensityAnalyzer()
        return cls._sentiment_analyzer
    
    @staticmethod
    def get_news(keyword: str, days_back: int = 1, use_cache: bool = True) -> list:
        """NewsAPI'den haber çek (OPTIMIZED)"""
        
        try:
            api_key = config.NEWS_API_KEY
            
            if not api_key or api_key == "YOUR_NEWS_API_KEY_HERE":
                return []
            
            # Cache kontrolü
            cache_key = f"news_{keyword}_{days_back}"
            
            if use_cache:
                cached = NewsAnalyzer._cache.get(cache_key)
                if cached is not None:
                    return cached
            
            # Rate limit kontrolü
            if not NewsAnalyzer._rate_limiter.can_request():
                remaining = NewsAnalyzer._rate_limiter.requests_remaining()
                print(f"   ⚠️  API LİMİT: {remaining} istek kaldı, cache kullanılıyor")
                return NewsAnalyzer._cache.get(cache_key) or []
            
            # API çağrısı yap
            to_date = datetime.now()
            from_date = to_date - timedelta(days=days_back)
            
            url = "https://newsapi.org/v2/everything"
            params = {
                "q": keyword,
                "from": from_date.strftime("%Y-%m-%d"),
                "to": to_date.strftime("%Y-%m-%d"),
                "sortBy": "publishedAt",
                "language": "en",
                "apiKey": api_key,
                "pageSize": 5  # Az sayıda istek
            }
            
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            NewsAnalyzer._rate_limiter.add_request()
            
            if data.get("status") == "ok":
                articles = data.get("articles", [])
                
                # Cache'e kaydet
                NewsAnalyzer._cache.set(cache_key, articles)
                
                return articles
            else:
                error_msg = data.get("message", "Unknown")
                
                # Rate limit hatası
                if "too many requests" in error_msg.lower():
                    NewsAnalyzer._rate_limiter.block_until(3600)
                    return NewsAnalyzer._cache.get(cache_key) or []
                
                return []
        
        except requests.exceptions.Timeout:
            # Timeout - cache'den al
            cache_key = f"news_{keyword}_{days_back}"
            return NewsAnalyzer._cache.get(cache_key) or []
        
        except Exception as e:
            return []
    
    @staticmethod
    def analyze_sentiment(text: str) -> float:
        """Sentiment analizi (VADER)"""
        try:
            if not text or len(text) < 5:
                return 0.0
            
            analyzer = NewsAnalyzer._get_sentiment_analyzer()
            scores = analyzer.polarity_scores(text)
            
            return round(float(scores['compound']), 3)
        
        except Exception as e:
            return 0.0
    
    @staticmethod
    def filter_articles(articles: list) -> list:
        """Kaliteli haberleri filtrele"""
        filtered = []
        
        for article in articles:
            # Boş kontrol
            if not article.get("title") or not article.get("description"):
                continue
            
            # Çok eski
            try:
                pub_date = datetime.fromisoformat(
                    article.get("publishedAt", "").replace('Z', '+00:00')
                )
                if (datetime.now(pub_date.tzinfo) - pub_date).days > 30:
                    continue
            except:
                pass
            
            filtered.append(article)
        
        return filtered[:10]
    
    @staticmethod
    def analyze_sector_news(sector: str, days_back: int = 1) -> dict:
        """Sektör haber analizi"""
        
        try:
            # Cache kontrol
            cache_key = f"sector_{sector}_{days_back}"
            cached = NewsAnalyzer._cache.get(cache_key)
            if cached:
                return cached
            
            # Haber çek
            articles = NewsAnalyzer.get_news(sector, days_back, use_cache=True)
            
            if not articles:
                result = {
                    "sector": sector,
                    "articles_count": 0,
                    "sentiment_score": 0.0,
                    "sentiment": "neutral",
                    "articles": [],
                    "status": "no_data"
                }
                NewsAnalyzer._cache.set(cache_key, result)
                return result
            
            # Filtrele
            articles = NewsAnalyzer.filter_articles(articles)
            
            if not articles:
                result = {
                    "sector": sector,
                    "articles_count": 0,
                    "sentiment_score": 0.0,
                    "sentiment": "neutral",
                    "articles": [],
                    "status": "no_quality"
                }
                NewsAnalyzer._cache.set(cache_key, result)
                return result
            
            # Sentiment
            sentiments = []
            processed_articles = []
            
            for article in articles:
                title = article.get("title", "")
                description = article.get("description", "")
                text = f"{title} {description}"
                sentiment = NewsAnalyzer.analyze_sentiment(text)
                sentiments.append(sentiment)
                
                processed_articles.append({
                    "title": title[:100],
                    "description": description[:150] if description else "",
                    "source": article.get("source", {}).get("name", "Unknown"),
                    "sentiment": sentiment
                })
            
            # Ortalama
            avg_sentiment = sum(sentiments) / len(sentiments) if sentiments else 0.0
            avg_sentiment = round(avg_sentiment, 3)
            
            # Label
            if avg_sentiment > 0.2:
                sentiment_label = "bullish"
                emoji = "🟢"
            elif avg_sentiment < -0.2:
                sentiment_label = "bearish"
                emoji = "🔴"
            else:
                sentiment_label = "neutral"
                emoji = "🟡"
            
            print(f"   {emoji} {sector.upper():15s} ({len(articles)} haber): {sentiment_label}")
            
            result = {
                "sector": sector,
                "articles_count": len(articles),
                "sentiment_score": avg_sentiment,
                "sentiment": sentiment_label,
                "articles": processed_articles[:3],
                "status": "success"
            }
            
            # Cache'e kaydet
            NewsAnalyzer._cache.set(cache_key, result)
            return result
        
        except Exception as e:
            print(f"   ❌ {sector.upper()}: {str(e)[:40]}")
            return {
                "sector": sector,
                "articles_count": 0,
                "sentiment_score": 0.0,
                "sentiment": "neutral",
                "articles": [],
                "status": "error"
            }


class GlobalSectorAnalyzer:
    """Küresel Sektör Analizi (API çağrısız)"""
    
    @staticmethod
    def get_sector_mood(sector: str) -> float:
        """Sektör mood'u (manuel)"""
        return NewsAnalyzer.SECTOR_MOODS_2026.get(sector, 0.0)
    
    @staticmethod
    def get_all_moods() -> dict:
        """Tüm sektörlerin mood'ları"""
        return NewsAnalyzer.SECTOR_MOODS_2026.copy()


def analyze_news(days_back: int = 1) -> dict:
    """Ana haber analizi (ULTRA OPTİMİZE)"""
    
    print(f"\n📰 Haber Analizi ({days_back} gün, akıllı rate limiting)...")
    
    sector_scores = {}
    
    # ADIM 1: Primary sectors (sadece 4 sektör = max 4 API çağrısı)
    print("\n   🎯 Birincil Sektörler (API):")
    
    remaining = NewsAnalyzer._rate_limiter.requests_remaining()
    available_slots = min(len(NewsAnalyzer.PRIMARY_SECTORS), remaining)
    
    if available_slots > 0:
        for sector in list(NewsAnalyzer.PRIMARY_SECTORS.keys())[:available_slots]:
            result = NewsAnalyzer.analyze_sector_news(sector, days_back)
            sector_scores[sector] = result["sentiment_score"]
    
    # Boş kalan sektörleri manuel mood ile doldur
    for sector in NewsAnalyzer.PRIMARY_SECTORS.keys():
        if sector not in sector_scores:
            mood = GlobalSectorAnalyzer.get_sector_mood(sector)
            sector_scores[sector] = mood
            print(f"   ⭕ {sector.upper():15s} (manual mood): {mood:+.3f}")
    
    # ADIM 2: Secondary sectors (hiç API çağrısı YOK)
    print("\n   📊 İkincil Sektörler (Manual Mood):")
    
    for sector in NewsAnalyzer.SECONDARY_SECTORS.keys():
        mood = GlobalSectorAnalyzer.get_sector_mood(sector)
        sector_scores[sector] = mood
        emoji = "🟢" if mood > 0.3 else "🔴" if mood < -0.2 else "🟡"
        print(f"   {emoji} {sector.upper():20s}: {mood:+.3f}")
    
    # ADIM 3: Genel skor
    if sector_scores:
        general_score = sum(sector_scores.values()) / len(sector_scores)
        sector_scores["genel"] = round(general_score, 3)
    else:
        sector_scores["genel"] = 0.0
    
    # ADIM 4: Jeopolitik risk ve arz-talep analizi
    try:
        from macro_analyzer import MacroAnalyzer
        from global_market_analyzer import GeopoliticalAnalyzer, GeopoliticalNewsIntegration
        all_articles = []
        for sector in list(NewsAnalyzer.PRIMARY_SECTORS.keys()):
            cache_key = f"sector_{sector}_{days_back}"
            cached = NewsAnalyzer._cache.get(cache_key)
            if cached and cached.get("articles"):
                all_articles.extend(cached["articles"])

        # Jeopolitik haberleri doğrudan API'den çek
        try:
            geo_news = GeopoliticalNewsIntegration.get_geopolitical_news()
            if geo_news:
                for news_item in geo_news:
                    all_articles.append({
                        "title": news_item.get("title", ""),
                        "description": news_item.get("description", ""),
                        "source": news_item.get("source", ""),
                    })
        except Exception:
            pass

        # Fallback: haber gelmezse GeopoliticalAnalyzer statik verilerinden makale oluştur
        if not all_articles:
            try:
                active_events = GeopoliticalAnalyzer.get_current_geopolitical_status()
                if active_events:
                    for event in active_events:
                        all_articles.append({
                            "title": event.get("event", ""),
                            "description": " ".join(event.get("impact", [])),
                        })
            except Exception:
                pass

        geo_result = MacroAnalyzer.analyze_geopolitical_risk(all_articles)

        # Aktif jeopolitik olayları risk listesine ve etkilenen sektörlere ekle
        try:
            active_events = GeopoliticalAnalyzer.get_current_geopolitical_status()
            if active_events:
                affected_sectors = set(geo_result.get("affected_sectors", []))
                sector_keywords = {
                    "enerji": ["enerji", "petrol", "oil", "gaz"],
                    "savunma": ["savunma", "military", "defence"],
                    "teknoloji": ["teknoloji", "tech"],
                    "madencilik": ["altın", "gold"],
                    "turizm": ["turizm", "travel"],
                }
                for event in active_events:
                    event_name = event.get("event", "")
                    if event_name and event_name not in geo_result.get("risks", []):
                        geo_result["risks"].append(event_name)
                    for impact in event.get("impact", []):
                        impact_lower = impact.lower()
                        for sector_name, keywords in sector_keywords.items():
                            if any(kw in impact_lower for kw in keywords):
                                affected_sectors.add(sector_name)

                geo_result["affected_sectors"] = list(affected_sectors)
                risk_count = len(geo_result.get("risks", []))
                geo_result["risk_count"] = risk_count
                if risk_count == 0:
                    geo_result["risk_level"] = "Düşük"
                elif risk_count <= 2:
                    geo_result["risk_level"] = "Orta"
                elif risk_count <= 5:
                    geo_result["risk_level"] = "Yüksek"
                else:
                    geo_result["risk_level"] = "Kritik"
        except Exception:
            pass

        sector_scores["geopolitical_risk"] = geo_result
        sector_scores["supply_demand_trends"] = MacroAnalyzer.detect_supply_demand_trends(all_articles)
    except Exception:
        sector_scores["geopolitical_risk"] = {"risk_level": "Bilinmiyor", "risks": [], "affected_sectors": []}
        sector_scores["supply_demand_trends"] = []
    
    # Bilgilendirme
    remaining = NewsAnalyzer._rate_limiter.requests_remaining()
    print(f"\n✅ {len(sector_scores)-3} sektör analiz edildi")
    print(f"   📊 API limit: {remaining}/100 istek kaldı")
    print(f"   💾 Cache bellek: {NewsAnalyzer._cache.get_memory_usage()}")
    
    return sector_scores


def analyze_news_detailed(sector: str, days_back: int = 1) -> dict:
    """Spesifik sektör detaylı analizi"""
    return NewsAnalyzer.analyze_sector_news(sector, days_back)


def get_top_sectors(sector_scores: dict, top_n: int = 5) -> list:
    """En iyi sektörler"""
    sorted_sectors = sorted(
        [(s, score) for s, score in sector_scores.items() if s != "genel"],
        key=lambda x: x[1],
        reverse=True
    )
    return sorted_sectors[:top_n]


def get_worst_sectors(sector_scores: dict, top_n: int = 5) -> list:
    """En kötü sektörler"""
    sorted_sectors = sorted(
        [(s, score) for s, score in sector_scores.items() if s != "genel"],
        key=lambda x: x[1]
    )
    return sorted_sectors[:top_n]


def clear_cache():
    """Cache'i temizle"""
    NewsAnalyzer._cache.clear_expired()
    print("✅ Süresi geçen cache'ler temizlendi")


def get_rate_limit_status() -> dict:
    """Rate limit durumu"""
    return {
        "requests_remaining": NewsAnalyzer._rate_limiter.requests_remaining(),
        "total_requests": NewsAnalyzer._rate_limiter.max_requests,
        "period_hours": NewsAnalyzer._rate_limiter.period_seconds / 3600,
        "blocked": NewsAnalyzer._rate_limiter.blocked_until is not None
    }


if __name__ == "__main__":
    print("🧪 News Analyzer Testi (OPTIMIZE)")
    print("=" * 70)
    
    # Cache temizle
    clear_cache()
    
    # Analiz
    scores = analyze_news(days_back=1)
    
    # Sonuçlar
    print("\n📊 Sektör Skorları:")
    print("=" * 70)
    for sector, score in sorted(scores.items(), key=lambda x: x[1], reverse=True):
        if sector != "genel":
            emoji = "🟢" if score > 0.2 else "🔴" if score < -0.2 else "🟡"
            print(f"{emoji} {sector:20s} | {score:+.3f}")
    
    print(f"\n📈 Genel Mood: {scores.get('genel', 0):+.3f}")
    
    # Rate limit status
    status = get_rate_limit_status()
    print(f"\n🔐 Rate Limit Status:")
    print(f"   Kalan: {status['requests_remaining']}/{status['total_requests']}")
    print(f"   Dönem: {status['period_hours']} saat")
    print(f"   Blocked: {status['blocked']}")
