import requests
import json
from datetime import datetime, timedelta
import os

class NewsManager:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://newsapi.org/v2"
        self.saved_articles = []
        self.filename = "saved_articles.json"
        self.load_saved_articles()
    
    def load_saved_articles(self):
        """Kaydedilmiş makaleleri dosyadan yükler"""
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r', encoding='utf-8') as file:
                    self.saved_articles = json.load(file)
            except:
                self.saved_articles = []
    
    def save_to_file(self):
        """Makaleleri dosyaya kaydeder"""
        with open(self.filename, 'w', encoding='utf-8') as file:
            json.dump(self.saved_articles, file, ensure_ascii=False, indent=4)
    
    # CREATE - Makale kaydetme
    def save_article(self, article):
        """Yeni bir makale kaydeder"""
        article_id = len(self.saved_articles) + 1
        article['id'] = article_id
        article['saved_date'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.saved_articles.append(article)
        self.save_to_file()
        return article_id
    
    # READ - Makaleleri getirme fonksiyonları
    def get_top_headlines(self, country="tr", category=None):
        """Günün öne çıkan haberlerini getirir"""
        url = f"{self.base_url}/top-headlines"
        params = {
            "apiKey": self.api_key,
            "country": country
        }
        if category:
            params["category"] = category
        
        response = requests.get(url, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Hata: {response.status_code}")
            return None
    
    def search_articles(self, query, from_date=None, to_date=None, sort_by="publishedAt"):
        """Anahtar kelimeye göre makale arama"""
        url = f"{self.base_url}/everything"
        params = {
            "apiKey": self.api_key,
            "q": query,
            "sortBy": sort_by
        }
        
        if from_date:
            params["from"] = from_date
        if to_date:
            params["to"] = to_date
        
        response = requests.get(url, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Hata: {response.status_code}")
            return None
    
    def get_daily_news(self, query=None, country="tr"):
        """Günlük haberleri getirir"""
        today = datetime.now().strftime("%Y-%m-%d")
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        
        if query:
            return self.search_articles(query, from_date=yesterday, to_date=today)
        else:
            return self.get_top_headlines(country=country)
    
    def get_weekly_news(self, query):
        """Haftalık haberleri getirir"""
        today = datetime.now().strftime("%Y-%m-%d")
        week_ago = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
        return self.search_articles(query, from_date=week_ago, to_date=today)
    
    def get_monthly_news(self, query):
        """Aylık haberleri getirir"""
        today = datetime.now().strftime("%Y-%m-%d")
        month_ago = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        return self.search_articles(query, from_date=month_ago, to_date=today)
    
    # Kaydedilmiş makaleleri okuma
    def get_saved_article(self, article_id):
        """ID'ye göre kaydedilmiş makaleyi getirir"""
        for article in self.saved_articles:
            if article['id'] == article_id:
                return article
        return None
    
    def get_all_saved_articles(self):
        """Tüm kaydedilmiş makaleleri getirir"""
        return self.saved_articles
    
    # UPDATE - Makale güncelleme
    def update_article(self, article_id, updated_data):
        """Kaydedilmiş makaleyi günceller"""
        for i, article in enumerate(self.saved_articles):
            if article['id'] == article_id:
                for key, value in updated_data.items():
                    if key != 'id' and key != 'saved_date':  # ID ve kayıt tarihi değiştirilemez
                        self.saved_articles[i][key] = value
                self.saved_articles[i]['updated_date'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self.save_to_file()
                return True
        return False
    
    # DELETE - Makale silme
    def delete_article(self, article_id):
        """Kaydedilmiş makaleyi siler"""
        for i, article in enumerate(self.saved_articles):
            if article['id'] == article_id:
                del self.saved_articles[i]
                self.save_to_file()
                return True
        return False


# Uygulamanın kullanımı
def main():
    # API anahtarınızı buraya girin
    API_KEY = "your_api_key_here"
    
    news_manager = NewsManager(API_KEY)
    
    # ÖRNEK KULLANIMLAR
    
    # Günlük haberleri getirme
    print("Günün öne çıkan haberleri:")
    top_headlines = news_manager.get_top_headlines(country="tr", category="technology")
    if top_headlines and top_headlines.get('articles'):
        for i, article in enumerate(top_headlines['articles'][:3]):
            print(f"{i+1}. {article['title']}")
            print(f"   Kaynak: {article['source']['name']}")
            print(f"   Tarih: {article['publishedAt']}")
            print(f"   URL: {article['url']}")
            print("")
    
    # Anahtar kelimeye göre arama
    print("\nTeknoloji konusunda son haberler:")
    tech_news = news_manager.search_articles("yapay zeka", sort_by="publishedAt")
    if tech_news and tech_news.get('articles'):
        # İlk makaleyi kaydet
        first_article = tech_news['articles'][0]
        article_id = news_manager.save_article({
            'title': first_article['title'],
            'url': first_article['url'],
            'source': first_article['source']['name'],
            'publishedAt': first_article['publishedAt'],
            'description': first_article['description']
        })
        print(f"Makale kaydedildi. ID: {article_id}")
    
    # Haftalık haberleri getirme
    print("\nSon bir haftanın ekonomi haberleri:")
    weekly_news = news_manager.get_weekly_news("ekonomi")
    if weekly_news and weekly_news.get('articles'):
        print(f"Toplam {len(weekly_news['articles'])} haber bulundu.")
    
    # Kaydedilmiş makaleleri listeleme
    print("\nKaydedilmiş makaleler:")
    saved_articles = news_manager.get_all_saved_articles()
    for article in saved_articles:
        print(f"ID: {article['id']} - {article['title']}")
    
    # Makale güncelleme örneği
    if saved_articles:
        article_id = saved_articles[0]['id']
        news_manager.update_article(article_id, {
            'notes': 'Bu makale çok ilginç!'
        })
        print(f"\n{article_id} ID'li makale güncellendi.")
    
    # Makale silme örneği (Yorum satırı olarak bırakıldı)
    # if saved_articles:
    #     article_id = saved_articles[0]['id']
    #     news_manager.delete_article(article_id)
    #     print(f"\n{article_id} ID'li makale silindi.")


if __name__ == "__main__":
    main()