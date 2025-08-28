# utils/vinted_scraper.py
import requests
from models.ad import Ad

BASE_URL = "https://www.vinted.fr/api/v2/catalog/items"

def search_vinted(keyword):
    """
    Scrape les annonces via l'API JSON interne.
    Retourne une liste d'objets Ad pour les vendeurs avec au moins 1 avis.
    """
    params = {"search_text": keyword, "per_page": 50, "page": 1}
    headers = {"User-Agent": "Mozilla/5.0"}
    
    response = requests.get(BASE_URL, params=params, headers=headers)
    data = response.json()
    
    ads = []
    for item in data.get("items", []):
        try:
            seller_reviews = item["user"]["feedback_count"]
            if seller_reviews < 1:
                continue
            
            title = item["title"]
            price = float(item["price"])
            photo_url = item["photos"][0]["url"] if item.get("photos") else ""
            seller = item["user"]["login"]
            link = "https://www.vinted.fr" + item["url"]
            
            ads.append(Ad(title, price, photo_url, seller, seller_reviews, link))
        except Exception:
            continue
    return ads

def get_market_price(keyword):
    ads = search_vinted(keyword)
    if not ads:
        return 0
    prices = [ad.price for ad in ads]
    return sum(prices) / len(prices)