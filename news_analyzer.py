# ============================================================
# news_analyzer.py — Haber Analizi Engine (v4 - KOMPLE & HATASIZ)
# ============================================================
# API Limit Optimizasyonu:
# - NewsAPI: Max 100 req/24h (ücretsiz)
# - Sadece önemli sektörleri analiz et
# - Cache kullan (tekrar çağrıyı azalt)
# ============================================================

import requests
from datetime import datetime, timedelta
from collections import defaultdict
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


class NewsAnalyzer:
    """Haber Analizi ve Sentiment (OPTIMIZED)"""
    
    # ÖNEMLİ SEKTÖRLER (API çağrı sayısını azaltmak için)
    PRIMARY_SECTORS = {
        "finans": ["bank", "financial", "stock", "investment", "trading", "forex", "crypto"],
        "teknoloji": ["tech", "software", "ai", "artificial intelligence", "chip", "semiconductor", "gpu"],
        "enerji": ["energy", "oil", "gas", "renewable", "solar", "wind", "petrol"],
        "sağlık": ["health", "pharma", "medical", "covid", "vaccine", "biotech", "hospital"],
    }
    
    # İKİNCİ SEVİYE SEKTÖRLER (Gerekirse)
    SECONDARY_SECTORS = {
        "perakende": ["retail", "shopping", "consumer", "e-commerce", "amazon", "walmart"],
        "gıda": ["food", "agriculture", "beverage", "restaurant", "nestle"],
        "telekom": ["telecom", "communication", "network", "5g", "vodafone"],
        "otomotiv": ["automotive", "car", "tesla", "electric vehicle", "ev"],
        "sigortalar": ["insurance", "underwriting", "axa", "allianz"],
        "turizm": ["tourism", "travel", "hotel", "airline", "booking"],
        "savunma": ["defense", "military", "weapons", "lockheed"],
        "inşaat_gayrimenkul": ["real estate", "construction", "building", "property"],
    }
    
    # Haber kaynakları (güvenilir)
    TRUSTED_SOURCES = [
        "Reuters", "Bloomberg", "CNBC", "AP News", "BBC News",
        "Financial Times", "Wall Street Journal", "MarketWatch",
        "Yahoo Finance", "Seeking Alpha"
    ]
    
    # Cache (API çağrı sayısını azaltmak için)
    _cache = {}
    _cache_time = {}
    CACHE_DURATION = 3600  # 1 saat
    
    @staticmethod
    def get_news(keyword: str, days_back: int = 1) -> list:
        """NewsAPI'den haber çek (CACHE İLE)"""
        try:
            api_key = config.NEWS_API_KEY
            
            if not api_key or api_key == "YOUR_NEWS_API_KEY_HERE":
                print("⚠️  NewsAPI anahtarı tanımlanmamış")
                return []
            
            # Cache kontrolü
            cache_key = f"{keyword}_{days_back}"
            if cache_key in NewsAnalyzer._cache:
                if (datetime.now() - NewsAnalyzer._cache_time.get(cache_key, datetime.now())).total_seconds() < NewsAnalyzer.CACHE_DURATION:
                    print(f"   📦 {keyword}: Cache'den alındı")
                    return NewsAnalyzer._cache[cache_key]
            
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
                "pageSize": 5  # Sayı azalt (API limit)
            }
            
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            if data.get("status") == "ok":
                articles = data.get("articles", [])
                # Cache'e kaydet
                NewsAnalyzer._cache[cache_key] = articles
                NewsAnalyzer._cache_time[cache_key] = datetime.now()
                return articles
            else:
                error_msg = data.get("message", "Unknown error")
                if "too many requests" in error_msg.lower():
                    print(f"   ⚠️  API LIMIT AŞILDI: {error_msg[:50]}")
                    return []
                else:
                    print(f"   ⚠️  NewsAPI hatası: {error_msg[:50]}")
                    return []
        
        except Exception as e:
            print(f"   ⚠️  Haber çekme hatası: {str(e)[:50]}")
            return []
    
    @staticmethod
    def analyze_sentiment(text: str) -> float:
        """Metin sentiment analizi (VADER)"""
        try:
            if not text or len(text) < 5:
                return 0.0
            
            sia = SentimentIntensityAnalyzer()
            scores = sia.polarity_scores(text)
            
            # Compound score: -1 (negatif) ile +1 (pozitif) arasında
            compound = float(scores['compound'])
            return round(compound, 3)
        
        except Exception as e:
            return 0.0
    
    @staticmethod
    def is_trusted_source(source_name: str) -> bool:
        """Kaynağın güvenilir olup olmadığını kontrol et"""
        if not source_name:
            return False
        
        return any(trusted in source_name for trusted in NewsAnalyzer.TRUSTED_SOURCES)
    
    @staticmethod
    def filter_articles(articles: list) -> list:
        """Kaliteli haberleri filtrele"""
        filtered = []
        
        for article in articles:
            # Boş haber atla
            if not article.get("title") or not article.get("description"):
                continue
            
            # Çok eski haberi atla
            try:
                pub_date = datetime.fromisoformat(article.get("publishedAt", "").replace('Z', '+00:00'))
                if (datetime.now(pub_date.tzinfo) - pub_date).days > 30:
                    continue
            except:
                pass
            
            filtered.append(article)
        
        return filtered[:10]  # Max 10 haber
    
    @staticmethod
    def analyze_sector_news(sector: str, days_back: int = 1) -> dict:
        """Belirli bir sektör için haber analizi"""
        try:
            print(f"   📰 {sector.upper()} analiz ediliyor...")
            
            # API çağrısı yap
            articles = NewsAnalyzer.get_news(sector, days_back)
            
            if not articles:
                return {
                    "sector": sector,
                    "articles_count": 0,
                    "sentiment_score": 0.0,
                    "sentiment": "neutral",
                    "articles": [],
                    "status": "no_data"
                }
            
            # Haberleri filtrele
            articles = NewsAnalyzer.filter_articles(articles)
            
            if not articles:
                return {
                    "sector": sector,
                    "articles_count": 0,
                    "sentiment_score": 0.0,
                    "sentiment": "neutral",
                    "articles": [],
                    "status": "no_quality_data"
                }
            
            sentiments = []
            processed_articles = []
            
            for article in articles:
                title = article.get("title", "")
                description = article.get("description", "")
                
                # Sentiment analiz
                text = f"{title} {description}"
                sentiment = NewsAnalyzer.analyze_sentiment(text)
                sentiments.append(sentiment)
                
                # Makaleyi işle
                processed_articles.append({
                    "title": title[:100],
                    "description": description[:150] if description else "",
                    "source": article.get("source", {}).get("name", "Unknown"),
                    "url": article.get("url", ""),
                    "published_at": article.get("publishedAt", ""),
                    "sentiment": sentiment,
                    "is_trusted": NewsAnalyzer.is_trusted_source(article.get("source", {}).get("name", ""))
                })
            
            # Ortalama sentiment
            avg_sentiment = sum(sentiments) / len(sentiments) if sentiments else 0.0
            avg_sentiment = round(avg_sentiment, 3)
            
            # Sentiment label
            if avg_sentiment > 0.2:
                sentiment_label = "bullish"
                emoji = "🟢"
            elif avg_sentiment < -0.2:
                sentiment_label = "bearish"
                emoji = "🔴"
            else:
                sentiment_label = "neutral"
                emoji = "🟡"
            
            print(f"   {emoji} {sector.upper()}: {sentiment_label} ({avg_sentiment:+.3f})")
            
            return {
                "sector": sector,
                "articles_count": len(articles),
                "sentiment_score": avg_sentiment,
                "sentiment": sentiment_label,
                "articles": processed_articles[:3],  # Top 3
                "status": "success"
            }
        
        except Exception as e:
            print(f"   ❌ {sector.upper()}: {str(e)[:50]}")
            return {
                "sector": sector,
                "articles_count": 0,
                "sentiment_score": 0.0,
                "sentiment": "neutral",
                "articles": [],
                "status": "error"
            }


class GlobalSectorAnalyzer:
    """Küresel sektör analizi (NewsAPI olmadan)"""
    
    @staticmethod
    def get_sector_mood(sector: str) -> float:
        """Sektörün genel duygusunu tahmin et (manual)"""
        
        # 2026 için tahminler
        sector_moods = {
            "teknoloji": 0.7,      # AI boom
            "enerji": 0.3,         # Normal
            "finans": 0.5,         # Faiz kararlarına bağlı
            "sağlık": 0.4,         # Stabil
            "perakende": 0.2,      # Talep düşüşü
            "gıda": 0.3,           # Enflasyon baskısı
            "telekom": 0.2,        # Düşük büyüme
            "otomotiv": 0.1,       # EV geçişi zorlayıcı
            "sigortalar": 0.4,     # Normal
            "turizm": 0.3,         # Mevsimsel
            "savunma": 0.6,        # NATO artışı
            "inşaat_gayrimenkul": 0.1,  # Faiz yüksek
        }
        
        return sector_moods.get(sector, 0.0)


def analyze_news(days_back: int = 1) -> dict:
    """Tüm sektörlerin haber sentiment skorunu hesapla (OPTIMIZED)"""
    print(f"\n📰 Haber analizi başlıyor ({days_back} gün, API limit cautious)...")
    
    sector_scores = {}
    
    # SADECE PRIMARY SECTORS (API limit)
    print("\n   🎯 Birincil Sektörler:")
    for sector in NewsAnalyzer.PRIMARY_SECTORS.keys():
        try:
            result = NewsAnalyzer.analyze_sector_news(sector, days_back)
            
            if result["status"] == "success" and result["articles_count"] > 0:
                sector_scores[sector] = result["sentiment_score"]
            else:
                # Manual mood kullan
                sector_scores[sector] = GlobalSectorAnalyzer.get_sector_mood(sector)
        
        except Exception as e:
            print(f"   ⚠️  {sector.upper()}: {str(e)[:40]}")
            sector_scores[sector] = GlobalSectorAnalyzer.get_sector_mood(sector)
    
    # Secondary sectors'ü manual mood ile doldur (API çağrı yapma)
    print("\n   📊 İkincil Sektörler (Manual Mood):")
    for sector in NewsAnalyzer.SECONDARY_SECTORS.keys():
        mood = GlobalSectorAnalyzer.get_sector_mood(sector)
        sector_scores[sector] = mood
        emoji = "🟢" if mood > 0.3 else "🔴" if mood < -0.2 else "🟡"
        print(f"   {emoji} {sector.upper()}: {mood:+.3f}")
    
    # Genel skor
    if sector_scores:
        general_score = sum(sector_scores.values()) / len(sector_scores) if sector_scores else 0.0
        sector_scores["genel"] = round(general_score, 3)
    else:
        sector_scores["genel"] = 0.0
    
    print(f"\n✅ {len(sector_scores)-1} sektör analiz edildi")
    return sector_scores


def analyze_news_detailed(sector: str, days_back: int = 1) -> dict:
    """Spesifik sektör için detaylı analiz"""
    return NewsAnalyzer.analyze_sector_news(sector, days_back)


def get_top_sectors(sector_scores: dict, top_n: int = 5) -> list:
    """En iyi sektörleri al"""
    sorted_sectors = sorted(
        [(s, score) for s, score in sector_scores.items() if s != "genel"],
        key=lambda x: x[1],
        reverse=True
    )
    return sorted_sectors[:top_n]


def get_worst_sectors(sector_scores: dict, top_n: int = 5) -> list:
    """En kötü sektörleri al"""
    sorted_sectors = sorted(
        [(s, score) for s, score in sector_scores.items() if s != "genel"],
        key=lambda x: x[1]
    )
    return sorted_sectors[:top_n]


if __name__ == "__main__":
    print("🧪 News Analyzer Testi")
    print("=" * 70)
    
    # Test et
    scores = analyze_news(days_back=1)
    
    print("\n📊 Sektör Skorları:")
    print("=" * 70)
    for sector, score in sorted(scores.items(), key=lambda x: x[1], reverse=True):
        if sector != "genel":
            emoji = "🟢" if score > 0.2 else "🔴" if score < -0.2 else "🟡"
            print(f"{emoji} {sector:20s} | {score:+.3f}")
    
    print(f"\n📈 Genel Mood: {scores.get('genel', 0):+.3f}")
