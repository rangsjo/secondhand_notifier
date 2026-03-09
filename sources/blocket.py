import requests
from bs4 import BeautifulSoup
import uuid

BASE_URL = "https://www.blocket.se/annonser/hela-sverige/verktyg"

def fetch_blocket(query):
    url = f"{BASE_URL}?q={query}"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        r = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")
        items = soup.select("article[data-item-id]")
        listings = []
        for i in items:
            title_el = i.select_one("h2")
            price_el = i.select_one(".price")
            url_el = i.select_one("a[href]")
            if title_el and url_el:
                listings.append({
                    "id": i.get("data-item-id", str(uuid.uuid4())),
                    "title": title_el.get_text(strip=True),
                    "description": "",
                    "price": float(price_el.get_text(strip=True).replace("kr","").replace(" ","")) if price_el else 0,
                    "url": url_el["href"],
                    "source": "blocket"
                })
        return listings
    except Exception as e:
        print("Blocket scraping error:", e)
        return []