import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Connection": "keep-alive"
}

def fetch_NK_price(url: str):
    """
    Scrapes the price from a product page whose HTML contains:
        <span class="price">Our Price $130.95</span>
    Returns the price text, or None if not found.
    """

    try:
        r = requests.get(url, headers=HEADERS, timeout=15)
        r.raise_for_status()
    except Exception as e:
        print(f"[NK ERROR] Failed to fetch {url}: {e}")
        return None

    soup = BeautifulSoup(r.text, "html.parser")

    # The price is encoded as: <span class="price">Our Price $130.95</span>
    price_el = soup.select_one("span.price")

    # If the price element is not found, price_el = None and if not None == True, so we return None
    if not price_el:
        return None

    # returns the actual price element within the tags, which is the text content of the span
    price_element = price_el.get_text(strip=True)

    # Removing the text "Our Price" to so that we only return the actual price
    price = price_element.replace("Our Price", "").strip()
    return price
