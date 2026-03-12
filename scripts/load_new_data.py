#!/usr/bin/env python3
"""Clean new_archive books.csv and load into normalized SQLite schema.

Usage:
    python scripts/load_new_data.py
"""

import csv
import re
import sqlite3
from pathlib import Path
from typing import Dict, List, Optional

ROOT = Path(__file__).resolve().parents[1]
INPUT_CSV = ROOT / "data" / "books.csv"
SCHEMA_SQL = ROOT / "sql" / "schema.sql"
DB_PATH = ROOT / "database" / "books.db"
CLEAN_CSV = ROOT / "processed" / "books_clean.csv"

# ISO 639 language code → readable name
LANG_MAP = {
    "eng": "English", "en-US": "English", "en-GB": "English", "en-CA": "English",
    "enm": "English", "spa": "Spanish", "fre": "French", "ger": "German",
    "jpn": "Japanese", "zho": "Chinese", "por": "Portuguese", "ita": "Italian",
    "rus": "Russian", "ara": "Arabic", "nl": "Dutch", "swe": "Swedish",
    "lat": "Latin", "grc": "Greek", "nor": "Norwegian", "tur": "Turkish",
    "srp": "Serbian", "msa": "Malay", "glg": "Galician", "wel": "Welsh",
    "gla": "Scottish Gaelic", "ale": "Aleut", "mul": "Multiple",
}


def clean_text(value: Optional[str]) -> str:
    if value is None:
        return ""
    return re.sub(r"\s+", " ", value).strip()


def to_int(value: str) -> Optional[int]:
    v = clean_text(value)
    if not v:
        return None
    try:
        return int(v)
    except ValueError:
        return None


def to_float(value: str) -> Optional[float]:
    v = clean_text(value)
    if not v:
        return None
    try:
        return float(v)
    except ValueError:
        return None


def parse_year(date_str: str) -> Optional[int]:
    """Extract year from M/D/YYYY date string."""
    date_str = clean_text(date_str)
    if not date_str:
        return None
    parts = date_str.split("/")
    if len(parts) == 3:
        y = to_int(parts[2])
        if y and 1800 <= y <= 2030:
            return y
    return None


def parse_authors(authors_str: str) -> List[str]:
    """Split 'Author1/Author2' into list of author names."""
    text = clean_text(authors_str)
    if not text:
        return []
    parts = [clean_text(a) for a in text.split("/")]
    seen = set()
    result = []
    for name in parts:
        if not name:
            continue
        key = name.lower()
        if key in seen:
            continue
        seen.add(key)
        result.append(name)
    return result


def normalize_language(code: str) -> Optional[str]:
    code = clean_text(code)
    if not code:
        return None
    return LANG_MAP.get(code, code)


def ensure_author_id(conn: sqlite3.Connection, cache: Dict[str, int], name: str) -> int:
    key = name.lower()
    if key in cache:
        return cache[key]
    conn.execute("INSERT OR IGNORE INTO authors(author_name) VALUES (?)", (name,))
    author_id = conn.execute(
        "SELECT author_id FROM authors WHERE author_name = ?", (name,)
    ).fetchone()[0]
    cache[key] = author_id
    return author_id


def main() -> None:
    if not INPUT_CSV.exists():
        raise FileNotFoundError(f"Input CSV not found: {INPUT_CSV}")
    if not SCHEMA_SQL.exists():
        raise FileNotFoundError(f"Schema not found: {SCHEMA_SQL}")

    # --- Read and clean CSV ---
    print(f"Reading {INPUT_CSV} ...")
    clean_rows = []
    seen_ids = set()

    with INPUT_CSV.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        # Fix column name with leading spaces
        for raw in reader:
            # Normalize keys (strip whitespace)
            row = {k.strip(): v for k, v in raw.items() if k is not None}

            book_id = to_int(row.get("bookID", ""))
            if book_id is None or book_id in seen_ids:
                continue
            seen_ids.add(book_id)

            title = clean_text(row.get("title", ""))
            if not title:
                continue

            rating = to_float(row.get("average_rating", ""))
            if rating is not None and rating == 0.0:
                rating = None  # Treat 0.0 as missing

            pages = to_int(row.get("num_pages", ""))
            if pages is not None and pages <= 0:
                pages = None

            num_ratings = to_int(row.get("ratings_count", ""))
            text_reviews = to_int(row.get("text_reviews_count", ""))
            publish_year = parse_year(row.get("publication_date", ""))
            language = normalize_language(row.get("language_code", ""))
            publisher = clean_text(row.get("publisher", "")) or None
            isbn = clean_text(row.get("isbn", "")) or None
            isbn13 = to_int(row.get("isbn13", ""))
            authors_str = row.get("authors", "")

            # Filter out books with too few ratings (unreliable scores)
            if num_ratings is None or num_ratings <= 100:
                continue

            clean_rows.append({
                "book_id": book_id,
                "title": title,
                "isbn": isbn,
                "isbn13": isbn13,
                "language": language,
                "pages": pages,
                "publisher_name": publisher,
                "publish_year": publish_year,
                "num_ratings": num_ratings,
                "rating": rating,
                "text_reviews_count": text_reviews,
                "authors_raw": authors_str,
            })

    print(f"Cleaned {len(clean_rows)} books (from {len(seen_ids)} unique IDs)")

    # --- Write clean CSV ---
    CLEAN_CSV.parent.mkdir(parents=True, exist_ok=True)
    csv_fields = [
        "book_id", "title", "isbn", "isbn13", "language", "pages",
        "publisher_name", "publish_year", "num_ratings", "rating",
        "text_reviews_count", "authors_raw",
    ]
    with CLEAN_CSV.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=csv_fields)
        writer.writeheader()
        writer.writerows(clean_rows)
    print(f"Wrote {CLEAN_CSV}")

    # --- Load into SQLite ---
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    if DB_PATH.exists():
        DB_PATH.unlink()
        print(f"Removed old {DB_PATH}")

    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.executescript(SCHEMA_SQL.read_text(encoding="utf-8"))
    print("Schema created")

    author_cache: Dict[str, int] = {}

    books_sql = """
    INSERT OR IGNORE INTO books (
        book_id, title, isbn, isbn13, language, pages,
        publisher_name, publish_year, num_ratings, rating, text_reviews_count
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """

    book_count = 0
    with conn:
        for row in clean_rows:
            conn.execute(books_sql, (
                row["book_id"],
                row["title"],
                row["isbn"],
                row["isbn13"],
                row["language"],
                row["pages"],
                row["publisher_name"],
                row["publish_year"],
                row["num_ratings"],
                row["rating"],
                row["text_reviews_count"],
            ))
            book_count += 1

            authors = parse_authors(row["authors_raw"])
            for idx, author_name in enumerate(authors, start=1):
                author_id = ensure_author_id(conn, author_cache, author_name)
                conn.execute(
                    "INSERT OR IGNORE INTO book_authors(book_id, author_id, author_order) VALUES (?, ?, ?)",
                    (row["book_id"], author_id, idx),
                )

    # --- Summary ---
    total_books = conn.execute("SELECT COUNT(*) FROM books").fetchone()[0]
    total_authors = conn.execute("SELECT COUNT(*) FROM authors").fetchone()[0]
    total_links = conn.execute("SELECT COUNT(*) FROM book_authors").fetchone()[0]
    conn.close()

    print(f"\nDone! Database: {DB_PATH}")
    print(f"  Books:   {total_books:,}")
    print(f"  Authors: {total_authors:,}")
    print(f"  Links:   {total_links:,}")


if __name__ == "__main__":
    main()
