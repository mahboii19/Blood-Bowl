from scraper.db import connect, get_default_db_path

def view_data():
    db_path = get_default_db_path()
    
    if not db_path.exists():
        print(f"Database not found at {db_path}")
        return

    # This uses your existing function from scraper/db.py which already sets row_factory
    conn = connect(db_path)
    cursor = conn.cursor()

    print("\n")
    print("--- ACTIVE TARGETS ---")
    targets = cursor.execute("SELECT id, product_name, source, retailer FROM targets WHERE active = 1").fetchall()
    if not targets:
        print("No active targets found in DB.")
    else:
        for t in targets:
            print(f"ID: {t['id']} | {t['product_name']} | {t['source']} | {t['retailer']}")

    print("\n")
    print("--- LATEST SCRAPED PRICES ---")
    prices = cursor.execute("""
        SELECT p.target_id, t.product_name, p.source, p.price_text, p.scraped_at 
        FROM prices p
        INNER JOIN targets t ON p.target_id = t.id
        ORDER BY p.scraped_at DESC, p.id DESC
        LIMIT 20
    """).fetchall()
    
    if not prices:
        print("No prices found in DB.")
    else:
        for p in prices:
            print(f"[{p['scraped_at']}] {p['product_name']} ({p['source']}): {p['price_text']}")

    print("\n")
    print("--- Time Series Data Preview ---")
    time_series = cursor.execute("""
        SELECT t.id, t.source, t.product_name, p.scraped_at, p.price_text
        FROM targets as t
        INNER JOIN prices as p ON t.id = p.target_id
        WHERE t.active = 1 
        """).fetchall()
    
    if not time_series:
        print("No time series data found for active targets.")

    else:
        for ts in time_series[:20]:  # Show only first 20 entries for brevity
            print(f"{ts['scraped_at']} | {ts['price_text']} | Target ID: {ts['id']} | {ts['source']} | {ts['product_name']}")

    # Closing connection when finished reading data
    conn.close()


if __name__ == "__main__":
    view_data()
