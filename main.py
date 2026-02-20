from scraper.runner import run_all


def main():
    results = run_all()
    for r in results:
        print(f"{r['Product']} [{r['Source']} - {r['Retailer']}]: {r['Price']}")
        print()


if __name__ == "__main__":
    main()
