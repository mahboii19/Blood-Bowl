import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Connection": "keep-alive"
}

def fetch_ebay_price(query: str):
    url = f"https://www.ebay.com/sch/i.html?_nkw={query}"
    r = requests.get(url, headers=HEADERS, timeout=10)
    soup = BeautifulSoup(r.text, "html.parser")

    # eBay uses this class for Buy It Now prices
    price_el = soup.select_one(".s-item__price")

    return price_el.get_text(strip=True) if price_el else None
