import json
from pathlib import Path
from .amazon import fetch_amazon_price
from .ebay import fetch_ebay_price

def load_targets():
    config_path = Path("config/targets.json")
    with config_path.open() as f:
        return json.load(f)["targets"]

def run_all():
    targets = load_targets()
    results = []

    for item in targets:
        name = item["name"]
        amazon_url = item.get("amazon_url")
        ebay_query = item.get("ebay_query")

        amazon_price = fetch_amazon_price(amazon_url) if amazon_url else None
        ebay_price = fetch_ebay_price(ebay_query) if ebay_query else None

        results.append({
            "name": name,
            "amazon_price": amazon_price,
            "ebay_price": ebay_price
        })

    return results
