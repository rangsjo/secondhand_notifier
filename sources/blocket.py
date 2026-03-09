import requests
from bs4 import BeautifulSoup
import uuid
from urllib.parse import urljoin

BASE_URL = "https://www.blocket.se/recommerce/forsale/search"

def fetch_blocket(query):
    url = f"{BASE_URL}?q={query}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept-Language": "sv-SE,sv;q=0.9",
        "Referer": "https://www.blocket.se/recommerce/forsale/search"
    }
    
    try:
        r = requests.get(url, headers=headers, timeout=10)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        
        # Updated selectors for current Blocket structure
        items = soup.select('div[data-qa="SearchItem"]')
        
        if not items:
            print("Warning: No items found with data-qa selector. Trying fallback selectors.")
            items = soup.select('article[data-testid*="item"]')
        
        listings = []
        
        for item in items:
            try:
                # Extract title
                title_el = item.select_one('h2, [data-qa="SearchItemTitle"]')
                if not title_el:
                    continue
                
                title = title_el.get_text(strip=True)
                
                # Extract price - try multiple selectors
                price_el = item.select_one('[data-qa="SearchItemPrice"], .price, span[data-qa*="price"]')
                price = 0
                
                if price_el:
                    price_text = price_el.get_text(strip=True)
                    # Remove currency and spaces, handle both formats
                    price_clean = price_text.replace("kr", "").replace("SEK", "").replace(" ", "").replace(",", ".")
                    try:
                        price = float(price_clean)
                    except ValueError:
                        price = 0
                
                # Extract URL - handle relative URLs
                url_el = item.select_one('a[href]')
                if not url_el:
                    continue
                
                item_url = url_el.get("href", "")
                # Convert relative URLs to absolute
                if item_url and not item_url.startswith("http"):
                    item_url = urljoin("https://www.blocket.se", item_url)
                
                # Extract item ID
                item_id = item.get("data-item-id", item.get("id", str(uuid.uuid4())))
                
                listings.append({
                    "id": item_id,
                    "title": title,
                    "description": "",
                    "price": price,
                    "url": item_url,
                    "source": "blocket"
                })
            
            except Exception as item_error:
                print(f"Error parsing individual item: {item_error}")
                continue
        
        return listings
    
    except requests.exceptions.RequestException as e:
        print(f"Blocket request error: {e}")
        return []
    except Exception as e:
        print(f"Blocket scraping error: {e}")
        return []