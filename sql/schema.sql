PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS books (
    book_id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    isbn TEXT,
    isbn13 INTEGER,
    language TEXT,
    pages INTEGER CHECK (pages IS NULL OR pages > 0),
    publisher_name TEXT,
    publish_year INTEGER CHECK (publish_year IS NULL OR publish_year BETWEEN 1800 AND 2030),
    num_ratings INTEGER CHECK (num_ratings IS NULL OR num_ratings >= 0),
    rating REAL CHECK (rating IS NULL OR rating BETWEEN 0 AND 5),
    text_reviews_count INTEGER CHECK (text_reviews_count IS NULL OR text_reviews_count >= 0)
);

CREATE TABLE IF NOT EXISTS authors (
    author_id INTEGER PRIMARY KEY AUTOINCREMENT,
    author_name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS book_authors (
    book_id INTEGER NOT NULL,
    author_id INTEGER NOT NULL,
    author_order INTEGER NOT NULL CHECK (author_order >= 1),
    PRIMARY KEY (book_id, author_id),
    UNIQUE (book_id, author_order),
    FOREIGN KEY (book_id) REFERENCES books(book_id) ON DELETE CASCADE,
    FOREIGN KEY (author_id) REFERENCES authors(author_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_books_title ON books(title);
CREATE INDEX IF NOT EXISTS idx_books_publish_year ON books(publish_year);
CREATE INDEX IF NOT EXISTS idx_books_rating ON books(rating);
CREATE INDEX IF NOT EXISTS idx_books_language ON books(language);
CREATE INDEX IF NOT EXISTS idx_books_isbn ON books(isbn);
CREATE INDEX IF NOT EXISTS idx_books_publisher ON books(publisher_name);
CREATE INDEX IF NOT EXISTS idx_book_authors_author_id ON book_authors(author_id);
