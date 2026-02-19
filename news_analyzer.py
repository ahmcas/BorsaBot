# ============================================================
# news_analyzer.py — Haber Analizi Engine (v3 - HIZLI)
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
    """Haber Analizi ve Sentiment (HIZLI VERSIYON)"""
    
    # Sektör anahtar kelimeleri
    SECTOR_KEYWORDS = {
        "finans": ["bank", "financial", "stock", "investment", "trading", "forex"],
        "teknoloji": ["tech", "software", "ai", "artificial intelligence", "chip", "semiconductor"],
        "enerji": ["energy", "oil", "gas", "renewable", "solar", "wind"],
        "sağlık": ["health", "pharma", "medical", "covid", "vaccine", "biotech"],
        "perakende": ["retail", "shopping", "consumer", "e-commerce"],
        "gıda": ["food", "agriculture", "beverage", "restaurant"],
        "telekom": ["telecom", "communication", "network", "5g"],
        "otomotiv": ["automotive", "car", "tesla", "electric vehicle"],
        "inşaat_gayrimenkul": ["real estate", "construction", "building", "property"],
        "sigortalar": ["insurance", "underwriting"],
        "turizm": ["tourism", "travel", "hotel", "airline"],
        "savunma": ["defense", "military", "weapons"],
        "tekstil": ["textile", "fashion", "apparel"],
        "kimya": ["chemical", "petrochemical"],
        "orman": ["forest", "timber", "paper"],
        "medya": ["media", "entertainment", "netflix", "streaming"]
    }
    
    @staticmethod
    def get_news(keyword: str, days_back: int = 7) -> list:
        """NewsAPI'den haber çek"""
        try:
            api_key = config.NEWS_API_KEY
            
            if not api_key or api_key == "YOUR_NEWS_API_KEY_HERE":
                print("⚠️  NewsAPI anahtarı tanımlanmamış")
                return []
            
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
                "pageSize": 10
            }
            
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            if data.get("status") == "ok":
                return data.get("articles", [])
            else:
                print(f"⚠️  NewsAPI hatası: {data.get('message', 'Unknown')}")
                return []
        
        except Exception as e:
            print(f"[ERROR] Haber çekme hatası: {e}")
            return []
    
    @staticmethod
    def analyze_sentiment(text: str) -> float:
        """Metin sentiment analizi (VADER - Hızlı)"""
        try:
            if not text:
                return 0.0
            
            sia = SentimentIntensityAnalyzer()
            scores = sia.polarity_scores(text)
            
            # Compound score: -1 (negatif) ile +1 (pozitif) arasında
            return float(scores['compound'])
        
        except Exception as e:
            print(f"[ERROR] Sentiment analizi hatası: {e}")
            return 0.0
    
    @staticmethod
    def categorize_news(text: str) -> list:
        """Haberi sektörlere göre kategorize et"""
        sectors = []
        text_lower = text.lower()
        
        for sector, keywords in NewsAnalyzer.SECTOR_KEYWORDS.items():
            if any(keyword in text_lower for keyword in keywords):
                sectors.append(sector)
        
        if not sectors:
            sectors = ["genel"]
        
        return sectors
    
    @staticmethod
    def analyze_sector_news(sector: str, days_back: int = 7) -> dict:
        """Belirli bir sektör için haber analizi"""
        try:
            articles = NewsAnalyzer.get_news(sector, days_back)
            
            if not articles:
                return {
                    "sector": sector,
                    "articles_count": 0,
                    "sentiment_score": 0.0,
                    "sentiment": "neutral",
                    "articles": []
                }
            
            sentiments = []
            processed_articles = []
            
            for article in articles:
                title = article.get("title", "")
                description = article.get("description", "")
                
                text = f"{title} {description}"
                sentiment = NewsAnalyzer.analyze_sentiment(text)
                sentiments.append(sentiment)
                
                processed_articles.append({
                    "title": title,
                    "description": description[:150],
                    "source": article.get("source", {}).get("name", "Unknown"),
                    "url": article.get("url", ""),
                    "published_at": article.get("publishedAt", ""),
                    "sentiment": sentiment
                })
            
            avg_sentiment = sum(sentiments) / len(sentiments) if sentiments else 0.0
            
            if avg_sentiment > 0.3:
                sentiment_label = "bullish"
            elif avg_sentiment < -0.3:
                sentiment_label = "bearish"
            else:
                sentiment_label = "neutral"
            
            return {
                "sector": sector,
                "articles_count": len(articles),
                "sentiment_score": round(avg_sentiment, 3),
                "sentiment": sentiment_label,
                "articles": processed_articles[:5]
            }
        
        except Exception as e:
            print(f"[ERROR] Sektör haber analizi hatası ({sector}): {e}")
            return {
                "sector": sector,
                "articles_count": 0,
                "sentiment_score": 0.0,
                "sentiment": "neutral",
                "articles": []
            }


def analyze_news(days_back: int = 7) -> dict:
    """Tüm sektörlerin haber sentiment skorunu hesapla"""
    print(f"\n📰 Haber analizi başlıyor ({days_back} gün)...")
    
    sector_scores = {}
    sectors = list(NewsAnalyzer.SECTOR_KEYWORDS.keys())
    
    for sector in sectors:
        try:
            result = NewsAnalyzer.analyze_sector_news(sector, days_back)
            
            if result["articles_count"] > 0:
                sentiment_score = result["sentiment_score"]
                sector_scores[sector] = sentiment_score
                
                print(f"✅ {sector.upper():20s} - Skor: {sentiment_score:+.3f} ({result['sentiment'].upper()})")
            else:
                sector_scores[sector] = 0.0
                print(f"⚠️  {sector.upper():20s} - Haber bulunamadı")
        
        except Exception as e:
            print(f"❌ {sector.upper():20s} - Hata: {e}")
            sector_scores[sector] = 0.0
    
    if sector_scores:
        general_score = sum(sector_scores.values()) / len(sector_scores)
        sector_scores["genel"] = general_score
    else:
        sector_scores["genel"] = 0.0
    
    return sector_scores


if __name__ == "__main__":
    print("🧪 News Analyzer Testi")
    print("=" * 50)
    
    scores = analyze_news(days_back=3)
    
    print("\n📊 Sonuçlar:")
    print("=" * 50)
    for sector, score in sorted(scores.items(), key=lambda x: x[1], reverse=True):
        trend = "📈" if score > 0.2 else "📉" if score < -0.2 else "➡️"
        print(f"{sector:20s} | {trend} {score:+.3f}")
