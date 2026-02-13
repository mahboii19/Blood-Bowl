import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Connection": "keep-alive"
}

def fetch_miniature_market_price(url: str):
    """
    Scrapes a specific Miniature Market product URL.
    Returns the price as a string, or None if not found.
    """

    try:
        r = requests.get(url, headers=HEADERS, timeout=15)
        r.raise_for_status()
    except Exception as e:
        print(f"[MM ERROR] Failed to fetch {url}: {e}")
        return None

    soup = BeautifulSoup(r.text, "html.parser")

    # -------------------------
    # PRICE (your exact selector)
    # -------------------------
    price_el = soup.select_one("span.price")

    if not price_el:
        return None

    return price_el.get_text(strip=True)
