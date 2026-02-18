# ============================================================
# news_analyzer.py — Haber Analizi Engine (v2 - KOMPLE)
# ============================================================

import requests
from datetime import datetime, timedelta
from collections import defaultdict
import config

try:
    from textblob import TextBlob
except:
    import subprocess
    subprocess.run(["pip", "install", "textblob"], check=True)
    from textblob import TextBlob


class NewsAnalyzer:
    """Haber Analizi ve Sentiment"""
    
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
    
    # Sentiment anahtar kelimeleri
    POSITIVE_KEYWORDS = [
        "gain", "surge", "jump", "boom", "rally", "bullish", "beat",
        "growth", "profit", "success", "positive", "strong", "rise",
        "record", "high", "up", "increase", "bull", "optimistic",
        "upgrade", "target raised", "buy", "outperform", "momentum"
    ]
    
    NEGATIVE_KEYWORDS = [
        "loss", "crash", "plunge", "bearish", "miss", "decline",
        "drop", "fall", "down", "decrease", "bear", "pessimistic",
        "downgrade", "target lowered", "sell", "underperform",
        "warning", "concern", "risk", "weak", "slump", "tumble"
    ]
    
    @staticmethod
    def get_news(keyword: str, days_back: int = 7) -> list:
        """NewsAPI'den haber çek"""
        try:
            api_key = config.NEWS_API_KEY
            
            if not api_key or api_key == "YOUR_NEWS_API_KEY_HERE":
                print("⚠️  NewsAPI anahtarı tanımlanmamış")
                return []
            
            # Tarih aralığı
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
        """Metin sentiment analizi (-1 negatif, +1 pozitif)"""
        try:
            if not text:
                return 0.0
            
            # TextBlob sentiment analizi
            blob = TextBlob(str(text).lower())
            polarity = blob.sentiment.polarity
            
            # Anahtar kelimelere göre boost et
            text_lower = text.lower()
            
            positive_count = sum(1 for word in NewsAnalyzer.POSITIVE_KEYWORDS if word in text_lower)
            negative_count = sum(1 for word in NewsAnalyzer.NEGATIVE_KEYWORDS if word in text_lower)
            
            keyword_sentiment = (positive_count - negative_count) * 0.1
            
            # Sentimenti birleştir
            final_sentiment = polarity * 0.7 + keyword_sentiment * 0.3
            
            # -1 ile +1 arasında sınırla
            return max(-1.0, min(1.0, final_sentiment))
        
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
        
        # Eğer hiçbir sektör yoksa "genel"
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
                
                # Sentiment analizi
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
            
            # Ortalama sentiment
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
    """
    Tüm sektörlerin haber sentiment skorunu hesapla
    Döndürür: {"sektör": sentiment_score}
    """
    print(f"\n📰 Haber analizi başlıyor ({days_back} gün)...")
    
    sector_scores = {}
    
    # Tüm sektörler
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
    
    # Genel skor (tümünün ortalaması)
    if sector_scores:
        general_score = sum(sector_scores.values()) / len(sector_scores)
        sector_scores["genel"] = general_score
    else:
        sector_scores["genel"] = 0.0
    
    return sector_scores


def get_top_sector_news(top_n: int = 5) -> dict:
    """En olumlu ve olumsuz sektörlerin haberini getir"""
    try:
        sector_scores = analyze_news()
        
        # Sıralama
        sorted_sectors = sorted(
            sector_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        top_positive = sorted_sectors[:top_n]
        top_negative = sorted_sectors[-top_n:]
        
        return {
            "top_positive": top_positive,
            "top_negative": top_negative,
            "all_scores": sector_scores
        }
    
    except Exception as e:
        print(f"[ERROR] Top sektör analizi hatası: {e}")
        return {"top_positive": [], "top_negative": [], "all_scores": {}}


if __name__ == "__main__":
    # Test
    print("🧪 News Analyzer Testi Başlıyor...\n")
    
    scores = analyze_news(days_back=3)
    
    print("\n📊 Sonuçlar:")
    print("=" * 50)
    for sector, score in sorted(scores.items(), key=lambda x: x[1], reverse=True):
        trend = "📈" if score > 0.2 else "📉" if score < -0.2 else "➡️"
        print(f"{sector:20s} | {trend} {score:+.3f}")
