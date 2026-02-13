import json
from pathlib import Path
from .amazon import fetch_amazon_price
from .ebay import fetch_ebay_price
from .GW import fetch_GW_price
from .miniature_market import fetch_miniature_market_price
def load_targets():
    config_path = Path("config/Products.json")
    with config_path.open() as f:
        return json.load(f)["targets"]

def safe_call(func, arg):
    """Run a scraper function safely. Return None on failure."""
    if not arg:
        return None
    try:
        return func(arg)
    except Exception as e:
        print(f"[ERROR] {func.__name__} failed for arg={arg}: {e}")
        return None

def run_all():
    targets = load_targets()
    results = []

    for item in targets:
        name = item["name"]

        amazon_price = safe_call(fetch_amazon_price, item.get("amazon_url"))
        ebay_price   = safe_call(fetch_ebay_price,   item.get("ebay_query"))
        GW_price     = safe_call(fetch_GW_price,     item.get("GW_url"))
        MM_price = safe_call(fetch_miniature_market_price, item.get("MM_url"))

        results.append({
            "name": name,
            "amazon_price": amazon_price,
            "ebay_price": ebay_price,
            "GW_price": GW_price,
            "MM_price": MM_price
        })

    return results
