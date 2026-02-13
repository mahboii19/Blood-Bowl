import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Connection": "keep-alive"
}

def fetch_GW_price(url: str):
    try:
        r = requests.get(url, headers=HEADERS, timeout=15)
        r.raise_for_status()
        
    except Exception as e:
        print(f"[GW ERROR] Failed to fetch {url}: {e}")
        return None
    
    with open("gw_debug.html", "w", encoding="utf-8") as f: 
        f.write(r.text)

    soup = BeautifulSoup(r.text, "html.parser")

    # Target the price span directly
    price_el = soup.select_one('span.mt-5.pt-5')

    if not price_el:
        return None

    return price_el.get_text(strip=True)

