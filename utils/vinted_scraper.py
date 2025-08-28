# utils/vinted_scraper.py
from playwright.async_api import async_playwright
from models.ad import Ad
import asyncio

async def search_vinted(keyword, max_items=50):
    """
    Scrape les annonces Vinted via Playwright.
    Retourne une liste d'objets Ad.
    """
    ads = []
    url = f"https://www.vinted.fr/catalog?search_text={keyword}"

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(url)
        await page.wait_for_selector("div.feed-grid__item-content")

        product_divs = await page.query_selector_all("div.feed-grid__item-content")

        for div in product_divs[:max_items]:
            try:
                link_elem = await div.query_selector("a")
                link = await link_elem.get_attribute("href")

                title_elem = await div.query_selector("div.web_ui__Cell__content")
                title = (await title_elem.inner_text()).strip()

                price_elem = await div.query_selector("xpath=.//div[contains(text(),'€')]")
                price_text = await price_elem.inner_text()
                price = float(price_text.replace("€","").replace(",","").strip())

                # Image
                img_elem = await div.query_selector("div.new-item-box__image img")
                if img_elem:
                    photo_url = await img_elem.get_attribute("src")
                else:
                    img_elem = await div.query_selector("div.new-item-box__image")
                    style = await img_elem.get_attribute("style")
                    photo_url = style.split('url("')[1].split('")')[0] if 'url("' in style else ""

                # Seller
                seller_elem = await div.query_selector("div.feed-grid__user-info")
                if seller_elem:
                    seller_name = (await seller_elem.inner_text()).strip()
                    seller_reviews = 1
                else:
                    seller_name = "Inconnu"
                    seller_reviews = 0

                ad = Ad(title, price, photo_url, seller_name, seller_reviews, link)
                ads.append(ad)
            except Exception as e:
                print(f"[DEBUG] Erreur sur une annonce : {e}")
                continue

        await browser.close()
    return ads

async def get_market_price(keyword):
    ads = await search_vinted(keyword)
    if not ads:
        return 0
    prices = [ad.price for ad in ads]
    return sum(prices) / len(prices)
