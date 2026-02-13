from scraper.runner import run_all

def main():
    results = run_all()
    for r in results:
        print(f"{r['name']}:")
        print(f"  Amazon: {r['amazon_price']}")
        print(f"  eBay:   {r['ebay_price']}")
        print()

if __name__ == "__main__":
    main()
