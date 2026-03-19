#!/usr/bin/env python3
"""
Fetch high-res book covers from multiple sources.

Usage:
  # Use the built-in book list:
  python3 fetch-covers.py

  # Use a JSON file (e.g. output from an LLM):
  python3 fetch-covers.py books.json

  # Force re-download (ignore cache):
  python3 fetch-covers.py --force

  # Both:
  python3 fetch-covers.py books.json --force

JSON format:
[
  {
    "title": "Zero to One",
    "author": "Peter Thiel & Blake Masters",
    "slug": "zero-to-one",
    "initials": "ZO",
    "isbn": "9780804139298",
    "cover_url": "https://covers.openlibrary.org/b/isbn/9780804139298-L.jpg"
  }
]

Fields:
  - title, author, slug: required
  - isbn: optional (null for essays/talks)
  - initials: optional (auto-generated from title if missing)
  - cover_url: optional (if provided, tried first before other sources)
"""

import json
import os
import re
import sys
import urllib.request
import urllib.parse
import time

COVERS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "covers")

DEFAULT_BOOKS = [
    {"title": "Distinction", "author": "Pierre Bourdieu", "isbn": "9780674212770", "slug": "distinction"},
    {"title": "The Work of Art in the Age of Mechanical Reproduction", "author": "Walter Benjamin", "isbn": "9780141036571", "slug": "work-of-art"},
    {"title": "Skin in the Game", "author": "Nassim Nicholas Taleb", "isbn": "9780425284629", "slug": "skin-in-the-game"},
    {"title": "The Art of Doing Science and Engineering", "author": "Richard Hamming", "isbn": "9781732265110", "slug": "art-of-science"},
    {"title": "The Power Broker", "author": "Robert A. Caro", "isbn": "9780394720241", "slug": "power-broker"},
    {"title": "Why Smart People Have Bad Ideas", "author": "Paul Graham", "isbn": None, "slug": "smart-people-bad-ideas"},
    {"title": "Man's Search for Meaning", "author": "Viktor Frankl", "isbn": "9780807014295", "slug": "mans-search"},
    {"title": "On Power", "author": "Bertrand de Jouvenel", "isbn": "9780865971134", "slug": "on-power"},
    {"title": "The Managerial Revolution", "author": "James Burnham", "isbn": "9780837168098", "slug": "managerial-revolution"},
    {"title": "Authority", "author": "Richard Sennett", "isbn": "9780393318272", "slug": "authority"},
    {"title": "The True Believer", "author": "Eric Hoffer", "isbn": "9780060505912", "slug": "true-believer"},
    {"title": "The Revolt of the Public", "author": "Martin Gurri", "isbn": "9781732265141", "slug": "revolt-of-public"},
    {"title": "Code and Other Laws of Cyberspace", "author": "Lawrence Lessig", "isbn": "9780465039135", "slug": "code-cyberspace"},
    {"title": "Institutions, Institutional Change and Economic Performance", "author": "Douglass North", "isbn": "9780521397346", "slug": "institutions"},
    {"title": "The Making of the Atomic Bomb", "author": "Richard Rhodes", "isbn": "9781451677614", "slug": "atomic-bomb"},
    {"title": "Surely You're Joking, Mr. Feynman", "author": "Richard P. Feynman", "isbn": "9780393316049", "slug": "feynman"},
    {"title": "The Innovators", "author": "Walter Isaacson", "isbn": "9781476708706", "slug": "innovators"},
    {"title": "Founders at Work", "author": "Jessica Livingston", "isbn": "9781590597149", "slug": "founders-at-work"},
    {"title": "Zero to One", "author": "Peter Thiel", "isbn": "9780804139298", "slug": "zero-to-one"},
    {"title": "The Innovator's Dilemma", "author": "Clayton Christensen", "isbn": "9780062060242", "slug": "innovators-dilemma"},
    {"title": "The Hard Thing About Hard Things", "author": "Ben Horowitz", "isbn": "9780062273208", "slug": "hard-thing"},
    {"title": "High Output Management", "author": "Andrew S. Grove", "isbn": "9780679762881", "slug": "high-output"},
    {"title": "Finite and Infinite Games", "author": "James P. Carse", "isbn": "9781476797090", "slug": "finite-infinite"},
    {"title": "Zen and the Art of Motorcycle Maintenance", "author": "Robert M. Pirsig", "isbn": "9780060839871", "slug": "zen-motorcycle"},
    {"title": "The Fountainhead", "author": "Ayn Rand", "isbn": "9780452286757", "slug": "fountainhead"},
    {"title": "Seeing Like a State", "author": "James C. Scott", "isbn": "9780300078152", "slug": "seeing-like-state"},
    {"title": "Silicon Valley's Ultimate Exit", "author": "Balaji Srinivasan", "isbn": None, "slug": "ultimate-exit"},
    {"title": "The Vulnerable World Hypothesis", "author": "Nick Bostrom", "isbn": None, "slug": "vulnerable-world"},
    {"title": "The Singularity Is Near", "author": "Ray Kurzweil", "isbn": "9780143037880", "slug": "singularity"},
    {"title": "The Black Swan", "author": "Nassim Nicholas Taleb", "isbn": "9780812973815", "slug": "black-swan"},
]

MIN_FILE_SIZE = 1000  # bytes — anything smaller is a placeholder


def fetch_url(url):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.read()
    except Exception:
        return None


def try_direct_url(url):
    if not url:
        return None
    data = fetch_url(url)
    if data and len(data) > MIN_FILE_SIZE:
        return data
    return None


def try_open_library(isbn):
    if not isbn:
        return None
    url = f"https://covers.openlibrary.org/b/isbn/{isbn}-L.jpg"
    data = fetch_url(url)
    if data and len(data) > MIN_FILE_SIZE:
        return data
    return None


def try_google_books(title, author, isbn=None):
    if isbn:
        query = urllib.parse.quote(f"isbn:{isbn}")
    else:
        query = urllib.parse.quote(f"{title} {author}")
    url = f"https://www.googleapis.com/books/v1/volumes?q={query}&maxResults=1"
    data = fetch_url(url)
    if not data:
        return None
    try:
        result = json.loads(data)
        items = result.get("items", [])
        if not items:
            return None
        links = items[0].get("volumeInfo", {}).get("imageLinks", {})
        for key in ["extraLarge", "large", "medium", "small", "thumbnail"]:
            if key in links:
                cover_url = links[key]
                cover_url = re.sub(r"&edge=curl", "", cover_url)
                cover_url = re.sub(r"zoom=\d", "zoom=3", cover_url)
                img_data = fetch_url(cover_url)
                if img_data and len(img_data) > MIN_FILE_SIZE:
                    return img_data
    except (json.JSONDecodeError, KeyError):
        pass
    return None


def download_cover(book, force=False):
    slug = book["slug"]
    out_path = os.path.join(COVERS_DIR, f"{slug}.jpg")

    if not force and os.path.exists(out_path) and os.path.getsize(out_path) > MIN_FILE_SIZE:
        print(f"  ✓ {slug} (cached)")
        return True

    # 1. Try provided cover_url first
    cover_url = book.get("cover_url")
    if cover_url:
        print(f"  → {slug}: trying provided URL...")
        data = try_direct_url(cover_url)
        if data:
            with open(out_path, "wb") as f:
                f.write(data)
            print(f"  ✓ {slug} (direct URL, {len(data)//1024}kb)")
            return True

    # 2. Try Google Books by ISBN, then by title
    isbn = book.get("isbn")
    if isbn:
        print(f"  → {slug}: trying Google Books (ISBN)...")
        data = try_google_books(book["title"], book["author"], isbn)
        if data:
            with open(out_path, "wb") as f:
                f.write(data)
            print(f"  ✓ {slug} (Google Books, {len(data)//1024}kb)")
            return True

    print(f"  → {slug}: trying Google Books (title search)...")
    data = try_google_books(book["title"], book["author"])
    if data:
        with open(out_path, "wb") as f:
            f.write(data)
        print(f"  ✓ {slug} (Google Books, {len(data)//1024}kb)")
        return True

    # 3. Try Open Library
    if isbn:
        print(f"  → {slug}: trying Open Library...")
        data = try_open_library(isbn)
        if data:
            with open(out_path, "wb") as f:
                f.write(data)
            print(f"  ✓ {slug} (Open Library, {len(data)//1024}kb)")
            return True

    print(f"  ✗ {slug}: no cover found")
    return False


def load_books(json_path):
    with open(json_path) as f:
        books = json.load(f)
    # Validate
    for b in books:
        if "slug" not in b:
            # Auto-generate slug from title
            b["slug"] = re.sub(r"[^a-z0-9]+", "-", b["title"].lower()).strip("-")
        if "initials" not in b:
            words = b["title"].split()
            b["initials"] = "".join(w[0] for w in words[:2]).upper()
    return books


def main():
    force = "--force" in sys.argv
    json_file = None
    for arg in sys.argv[1:]:
        if arg != "--force" and arg.endswith(".json"):
            json_file = arg

    if json_file:
        print(f"Loading books from {json_file}...")
        books = load_books(json_file)
    else:
        books = DEFAULT_BOOKS

    os.makedirs(COVERS_DIR, exist_ok=True)
    print(f"Fetching covers for {len(books)} books...\n")

    found = 0
    missing = []
    for book in books:
        if download_cover(book, force=force):
            found += 1
        else:
            missing.append(book)
        time.sleep(0.5)

    print(f"\nDone: {found}/{len(books)} covers downloaded to {COVERS_DIR}/")
    if missing:
        print("\nMissing:")
        for b in missing:
            print(f"  - {b['title']} ({b['slug']})")
        print(f"\nTo generate HTML for these, use initials fallback:")
        for b in missing:
            initials = b.get("initials", b["title"][:2].upper())
            print(f'  <span class="book-cover-fallback">{initials}</span>')


if __name__ == "__main__":
    main()
