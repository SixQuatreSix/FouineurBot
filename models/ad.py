# models/ad.py
class Ad:
    def __init__(self, title, price, photo_url, seller, seller_reviews, link):
        self.title = title
        self.price = price
        self.photo_url = photo_url
        self.seller = seller
        self.seller_reviews = seller_reviews
        self.link = link