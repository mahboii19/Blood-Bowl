from pathlib import Path
from .amazon import fetch_amazon_price
from .ebay import fetch_ebay_price
from .GW import fetch_GW_price
from .NK import fetch_NK_price
from .miniature_market import fetch_miniature_market_price
from .flipside_gaming import fetch_flipside_gaming_price
from .db import add_price, connect, get_targets, init_db


SCRAPER_MAP = {
    "Amazon": fetch_amazon_price,
    "Games Workshop": fetch_GW_price,
    "Miniature Market": fetch_miniature_market_price,
    "Noble Knight": fetch_NK_price,
    "Flipside Gaming": fetch_flipside_gaming_price,
}

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

    # Resolve the path to config/targets.csv relative to the project root
    project_root = Path(__file__).resolve().parents[1]

    # Initialize the path and database object
    db_path = project_root / "data" / "blood_bowl.sqlite3"
    conn = connect(db_path)

    # Creating DB file, will be set in project_root/data/blood_bowl.sqlite3
    # -- creates file and tables if they don't exist
    init_db(conn)

    # Create csv_path relative to project root, pointing to Data/BB_Products_Tracker.csv
    csv_path = project_root / "Data" / "BB_Products_Tracker.csv"

    targets = get_targets(conn, csv_path=str(csv_path))
    results = []

    if not targets:
        print(f"No active targets found. Please ensure {csv_path} exists and contains data.")
        conn.close()
        return results

    try:
        for item in targets:
            source = item["source"]
            scraper = SCRAPER_MAP.get(source)
            if not scraper:
                continue

            price = safe_call(scraper, item["retailer_url"])
            add_price(
                conn=conn,
                target_id=item["id"],
                source=source,
                price_text=price,
            )

            results.append(
                {
                    "Product": item["product_name"],
                    "Source": source,
                    "Retailer": item["retailer"],
                    "Price": price,
                }
            )
    finally:
        conn.close()

    return results
