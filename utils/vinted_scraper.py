# utils/vinted_scraper.py
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from models.ad import Ad
import time

def search_vinted(keyword, max_items=50):
    """
    Scrape les annonces Vinted via Selenium.
    Retourne une liste d'objets Ad.
    """
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    url = f"https://www.vinted.fr/catalog?search_text={keyword}"
    driver.get(url)
    
    wait = WebDriverWait(driver, 10)
    try:
        wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.feed-grid__item-content")))
    except:
        print(f"❌ Impossible de charger les annonces pour {keyword}")
        driver.quit()
        return []

    ads = []
    product_divs = driver.find_elements(By.CSS_SELECTOR, "div.feed-grid__item-content")
    
    for div in product_divs[:max_items]:
        try:
            link_elem = div.find_element(By.CSS_SELECTOR, "a")
            link = link_elem.get_attribute("href")

            title_elem = div.find_element(By.CSS_SELECTOR, "div.web_ui__Cell__content")
            title = title_elem.text.strip()

            price_elem = div.find_element(By.XPATH, ".//div[contains(text(),'€')]")
            price = float(price_elem.text.replace("€","").replace(",","").strip())

            try:
                img_elem = div.find_element(By.CSS_SELECTOR, "div.new-item-box__image img")
                photo_url = img_elem.get_attribute("src")
            except:
                img_elem = div.find_element(By.CSS_SELECTOR, "div.new-item-box__image")
                style = img_elem.get_attribute("style")
                photo_url = style.split('url("')[1].split('")')[0] if 'url("' in style else ""

            try:
                seller_elem = div.find_element(By.CSS_SELECTOR, "div.feed-grid__user-info")
                seller_name = seller_elem.text.strip()
                seller_reviews = 1  # On ne récupère pas exactement le nombre d'avis, mais minimum 1
            except:
                seller_name = "Inconnu"
                seller_reviews = 0

            ad = Ad(title, price, photo_url, seller_name, seller_reviews, link)
            ads.append(ad)
        except Exception as e:
            print(f"[DEBUG] Erreur sur une annonce : {e}")
            continue

    driver.quit()
    return ads

def get_market_price(keyword):
    ads = search_vinted(keyword)
    if not ads:
        return 0
    prices = [ad.price for ad in ads]
    return sum(prices) / len(prices)
