import csv
import sqlite3
from pathlib import Path
from typing import Optional


# Returns only the default DB file path; it does not create folders/files.
# In this project, this resolves to: <project_root>/data/blood_bowl.sqlite3
def get_default_db_path() -> Path:
    project_root = Path(__file__).resolve().parents[1]
    return project_root / "data" / "blood_bowl.sqlite3"


# Opens an existing SQLite file at resolved_path, or creates it there if missing.
# resolved_path.parent is the directory containing the DB file (e.g. .../Blood-Bowl/data).
# mkdir(parents=True, exist_ok=True) ensures that directory exists before connecting.
# row_factory=sqlite3.Row lets us access columns by name (row["id"], row["name"]) instead
# of only tuple indexes (row[0], row[1]).
def connect(db_path: Optional[str] = None) -> sqlite3.Connection:
    resolved_path = Path(db_path) if db_path else get_default_db_path()
    resolved_path.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(resolved_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(conn: sqlite3.Connection) -> None:
    conn.executescript(
        """
        -- id is the primary key for targets: each target row gets a unique identifier.
        CREATE TABLE IF NOT EXISTS targets (
            id INTEGER PRIMARY KEY,
            product_name TEXT NOT NULL,
            source TEXT NOT NULL,
            retailer TEXT NOT NULL,
            retailer_url TEXT NOT NULL,
            active INTEGER NOT NULL DEFAULT 1,
            UNIQUE(product_name, source, retailer)
        );

        -- target_id is the relationship key that links each prices row to targets.id.
        CREATE TABLE IF NOT EXISTS prices (
            id INTEGER PRIMARY KEY,
            target_id INTEGER NOT NULL,
            source TEXT NOT NULL,
            price_text TEXT,
            scraped_at TEXT NOT NULL DEFAULT (date('now')),
            FOREIGN KEY(target_id) REFERENCES targets(id)
        );

        -- Speeds up filtering targets by active status.
        CREATE INDEX IF NOT EXISTS idx_targets_active
            ON targets(active);

        -- Speeds up price-history lookups by target and newest date first.
        CREATE INDEX IF NOT EXISTS idx_prices_target_time
            ON prices(target_id, scraped_at DESC);
        """
    )
    conn.commit()


def upsert_target(
    conn: sqlite3.Connection,
    product_name: str,
    source: str,
    retailer: str,
    retailer_url: str,
    active: int = 1,
) -> int:
    # Upsert = insert a new (product_name, source, retailer) target, or update retailer_url/active if it exists.
    # UNIQUE(product_name, source, retailer) prevents duplicates for the same product-source-retailer row.
    # Returns the target id so callers can link related rows (e.g., prices.target_id).
    conn.execute(
        """
        INSERT INTO targets (product_name, source, retailer, retailer_url, active)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(product_name, source, retailer)
        DO UPDATE SET retailer_url=excluded.retailer_url, active=excluded.active
        """,
        (product_name, source, retailer, retailer_url, active),
    )
    row = conn.execute(
        "SELECT id FROM targets WHERE product_name = ? AND source = ? AND retailer = ?",
        (product_name, source, retailer),
    ).fetchone()
    conn.commit()
    return int(row["id"])


def add_price(
    conn: sqlite3.Connection,
    target_id: int,
    source: str,
    price_text: Optional[str],
) -> None:
    # Appends one price snapshot row for a target (does not update old rows).
    # scraped_at is auto-filled by the table default date('now') if not provided.
    conn.execute(
        """
        INSERT INTO prices (target_id, source, price_text)
        VALUES (?, ?, ?)
        """,
        (target_id, source, price_text),
    )
    conn.commit()


def import_targets_from_csv(conn: sqlite3.Connection, csv_path: str) -> int:
    path = Path(csv_path)
    if not path.exists():
        print(f"CSV file not found: {csv_path}")
        return 0

    # 1. Fetch current active targets to avoid redundant writes
    existing = conn.execute(
        "SELECT product_name, source, retailer, retailer_url FROM targets"
    ).fetchall()
    
    # Create a lookup map: {(name, source, retailer): url}
    existing_map = {
        (row["product_name"], row["source"], row["retailer"]): row["retailer_url"]
        for row in existing
    }

    changes_made = 0
    with open(path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Map CSV fields ("Product", "Source", etc.) to DB variables
            product_name = row.get("Product", "").strip()
            source = row.get("Source", "").strip()
            retailer = row.get("Retailer", "").strip()
            retailer_url = row.get("Retailer_URL", "").strip()

            if not all([product_name, source, retailer, retailer_url]):
                continue

            # 2. Only upsert if the record is new OR the URL has changed
            key = (product_name, source, retailer)
            if key in existing_map and existing_map[key] == retailer_url:
                continue

            upsert_target(
                conn=conn,
                product_name=product_name,
                source=source,
                retailer=retailer,
                retailer_url=retailer_url,
                active=1,
            )
            changes_made += 1
    
    return changes_made


# fetchall() returns all rows from the SELECT result set.
# Because connect() sets row_factory=sqlite3.Row, each row can be converted with dict(row),
# producing a JSON-like Python structure: one dict per table row.
def get_targets(conn: sqlite3.Connection, csv_path: Optional[str] = None) -> list[dict]:
    if csv_path:
        count = import_targets_from_csv(conn, csv_path)
        if count > 0:
            print(f"Imported/Updated {count} target(s) from {csv_path}")

    rows = conn.execute(
        """
        SELECT id, product_name, source, retailer, retailer_url
        FROM targets
        WHERE active = 1
        ORDER BY product_name, source, retailer
        """
    ).fetchall()
    return [dict(row) for row in rows]
