#!/usr/bin/env python3
"""
Quote Collection Script
Fetches quotes from multiple free APIs and organizes them by tags
Appends/merges unique quotes to existing database
"""

import json
import requests
import time
import random
from pathlib import Path
from typing import Dict, List
import urllib3

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Get the script's directory and navigate to project root
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
DATA_DIR = PROJECT_ROOT / "data"
TAGS_DIR = DATA_DIR / "tags"
OUTPUT_FILE = DATA_DIR / "quotes.json"

# Ensure directories exist
DATA_DIR.mkdir(exist_ok=True)
TAGS_DIR.mkdir(exist_ok=True)

# Tag mappings - maps our tags to API categories/keywords
TAG_KEYWORDS = {
    "motivation": ["motivational", "inspire", "achieve"],
    "inspiration": ["inspirational", "dream", "aspire"],
    "life": ["life", "living", "existence"],
    "wisdom": ["wisdom", "knowledge", "understanding"],
    "love": ["love", "compassion", "heart"],
    "success": ["success", "achievement", "accomplish"],
    "leadership": ["leadership", "leader", "guide"],
    "happiness": ["happiness", "joy", "cheerful"],
    "change": ["change", "transform", "grow"],
    "perseverance": ["perseverance", "persistence", "endure"],
    "mindfulness": ["mindfulness", "awareness", "present"],
    "growth": ["growth", "develop", "improve"],
    "courage": ["courage", "brave", "fearless"],
    "gratitude": ["gratitude", "thankful", "appreciate"],
    "resilience": ["resilience", "strength", "overcome"],
    "friendship": ["friendship", "friend", "companion"],
    "creativity": ["creativity", "imagination", "create"],
    "humility": ["humility", "humble", "modest"],
    "forgiveness": ["forgiveness", "forgive", "mercy"],
    "patience": ["patience", "patient", "wait"],
    "integrity": ["integrity", "honest", "principle"],
    "self-reflection": ["reflection", "introspection", "self"],
    "empathy": ["empathy", "compassion", "understanding"],
    "purpose": ["purpose", "meaning", "direction"],
    "justice": ["justice", "fair", "right"],
    "harmony": ["harmony", "peace", "balance"],
    "knowledge": ["knowledge", "learning", "wisdom"],
    "hope": ["hope", "optimism", "faith"],
    "anger": ["anger", "frustration", "emotion"],
    "fear": ["fear", "anxiety", "worry"],
    "general": ["life", "wisdom", "philosophy"]
}


def load_existing_quotes() -> Dict:
    """Load existing quotes database if it exists"""
    if OUTPUT_FILE.exists():
        try:
            with open(OUTPUT_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Warning: Could not load existing quotes: {e}")
            return {}
    return {}


def fetch_from_quotable(tag: str, limit: int = 50) -> List[Dict]:
    """
    Fetch quotes from api.quotable.io
    """
    quotes = []
    keywords = TAG_KEYWORDS.get(tag, ["life"])

    for keyword in keywords[:2]:  # Try first 2 keywords
        try:
            url = f"https://api.quotable.io/quotes/random?tags={keyword}&limit={limit}"
            response = requests.get(url, timeout=10, verify=False)

            if response.status_code == 200:
                data = response.json()
                for item in data:
                    quotes.append({
                        "text": item.get("content", ""),
                        "author": item.get("author", "Unknown"),
                        "source": "quotable.io"
                    })
                print(f"  ✓ Fetched {len(data)} quotes for '{tag}' (keyword: {keyword}) from quotable.io")
                time.sleep(0.5)  # Rate limiting
        except Exception as e:
            print(f"  ✗ Error fetching from quotable.io for '{tag}' (keyword: {keyword}): {e}")

    return quotes


def fetch_from_zenquotes(tag: str) -> List[Dict]:
    """
    Fetch quotes from zenquotes.io
    Note: This API returns a random set each time
    """
    quotes = []
    try:
        url = "https://zenquotes.io/api/quotes"
        response = requests.get(url, timeout=10, verify=False)

        if response.status_code == 200:
            data = response.json()
            keywords = TAG_KEYWORDS.get(tag, ["life"])

            # Filter quotes by keyword matching
            for item in data:
                quote_text = item.get("q", "").lower()
                if any(keyword.lower() in quote_text for keyword in keywords):
                    quotes.append({
                        "text": item.get("q", ""),
                        "author": item.get("a", "Unknown"),
                        "source": "zenquotes.io"
                    })

            if quotes:
                print(f"  ✓ Fetched {len(quotes)} quotes for '{tag}' from zenquotes.io")

        time.sleep(1)  # Rate limiting
    except Exception as e:
        print(f"  ✗ Error fetching from zenquotes.io for '{tag}': {e}")

    return quotes


def fetch_from_quotable_search(tag: str, limit: int = 30) -> List[Dict]:
    """
    Fetch quotes using quotable.io search endpoint
    """
    quotes = []
    keywords = TAG_KEYWORDS.get(tag, ["life"])

    for keyword in keywords[:2]:  # Try first 2 keywords
        try:
            url = f"https://api.quotable.io/search/quotes?query={keyword}&limit={limit}"
            response = requests.get(url, timeout=10, verify=False)

            if response.status_code == 200:
                data = response.json()
                results = data.get("results", [])

                for item in results:
                    quotes.append({
                        "text": item.get("content", ""),
                        "author": item.get("author", "Unknown"),
                        "source": "quotable.io"
                    })

                if results:
                    print(f"  ✓ Fetched {len(results)} quotes for '{tag}' (keyword: {keyword}) from quotable.io search")

            time.sleep(0.5)  # Rate limiting
        except Exception as e:
            print(f"  ✗ Error fetching from quotable.io search for '{tag}' (keyword: {keyword}): {e}")

    return quotes


def fetch_from_quotable_by_author(tag: str, limit: int = 20) -> List[Dict]:
    """
    Fetch quotes from famous authors related to the tag
    """
    quotes = []
    # Map tags to famous authors
    author_map = {
        "motivation": ["Tony Robbins", "Zig Ziglar", "Dale Carnegie"],
        "inspiration": ["Maya Angelou", "Helen Keller", "Walt Disney"],
        "wisdom": ["Confucius", "Socrates", "Aristotle"],
        "leadership": ["John C. Maxwell", "Peter Drucker", "Simon Sinek"],
        "success": ["Napoleon Hill", "Stephen Covey", "Jim Rohn"],
    }

    authors = author_map.get(tag, [])

    for author in authors[:1]:  # Try first author
        try:
            url = f"https://api.quotable.io/quotes?author={author}&limit={limit}"
            response = requests.get(url, timeout=10, verify=False)

            if response.status_code == 200:
                data = response.json()
                results = data.get("results", [])

                for item in results:
                    quotes.append({
                        "text": item.get("content", ""),
                        "author": item.get("author", "Unknown"),
                        "source": "quotable.io"
                    })

                if results:
                    print(f"  ✓ Fetched {len(results)} quotes for '{tag}' from author '{author}'")

            time.sleep(0.5)
        except Exception as e:
            print(f"  ✗ Error fetching from author '{author}': {e}")

    return quotes


def merge_quotes(existing: List[Dict], new: List[Dict]) -> List[Dict]:
    """
    Merge new quotes with existing ones, removing duplicates based on text
    """
    # Create a set of existing quote texts (normalized)
    existing_texts = {quote["text"].strip().lower() for quote in existing}

    # Add new quotes that don't exist
    merged = existing.copy()
    added = 0

    for quote in new:
        text = quote["text"].strip()
        if text and text.lower() not in existing_texts:
            merged.append(quote)
            existing_texts.add(text.lower())
            added += 1

    return merged, added


def generate_quotes_database():
    """
    Generate a comprehensive quotes database organized by tags
    Merges with existing database
    """
    print("=" * 60)
    print("Quote Database Generator (Append/Merge Mode)")
    print("=" * 60)
    print()

    # Load existing quotes
    print("Loading existing quotes database...")
    quotes_db = load_existing_quotes()

    if quotes_db:
        total_existing = sum(len(quotes) for quotes in quotes_db.values())
        print(f"✓ Loaded {total_existing} existing quotes across {len(quotes_db)} tags")
    else:
        print("No existing database found. Creating new one.")
    print()

    # Randomize tag order
    all_tags = list(TAG_KEYWORDS.keys())
    random.shuffle(all_tags)
    print(f"Processing tags in randomized order...")
    print()

    stats = {
        "tags_processed": 0,
        "quotes_added": 0,
        "quotes_skipped": 0
    }

    for tag in all_tags:
        print(f"Fetching quotes for tag: '{tag}'")
        new_quotes = []

        # Fetch from multiple sources with higher limits
        new_quotes.extend(fetch_from_quotable(tag, limit=50))
        new_quotes.extend(fetch_from_quotable_search(tag, limit=30))
        new_quotes.extend(fetch_from_quotable_by_author(tag, limit=20))
        new_quotes.extend(fetch_from_zenquotes(tag))

        # Get existing quotes for this tag
        existing_quotes = quotes_db.get(tag, [])

        # Merge and remove duplicates
        merged_quotes, added = merge_quotes(existing_quotes, new_quotes)
        quotes_db[tag] = merged_quotes

        stats["tags_processed"] += 1
        stats["quotes_added"] += added
        stats["quotes_skipped"] += len(new_quotes) - added

        print(
            f"  → Existing: {len(existing_quotes)}, New: {len(new_quotes)}, Added: {added}, Total: {len(merged_quotes)}")

        # Save after each tag to avoid losing data
        print(f"  💾 Saving progress...")
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump(quotes_db, f, indent=2, ensure_ascii=False)

        print()
        time.sleep(1)  # Be nice to the APIs

    print(f"\n✓ All changes saved to: {OUTPUT_FILE.absolute()}")

    # Save individual tag files
    print(f"\nSaving individual tag files to: {TAGS_DIR.absolute()}")
    for tag, quotes in quotes_db.items():
        tag_file = TAGS_DIR / f"{tag}.json"
        tag_data = {
            "tag": tag,
            "count": len(quotes),
            "quotes": quotes
        }
        with open(tag_file, 'w', encoding='utf-8') as f:
            json.dump(tag_data, f, indent=2, ensure_ascii=False)
        print(f"  ✓ Saved {tag}.json ({len(quotes)} quotes)")

    print(f"\n✓ Successfully saved {len(quotes_db)} tag files")

    # Print summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    total_quotes = sum(len(quotes) for quotes in quotes_db.values())
    print(f"Tags processed: {stats['tags_processed']}")
    print(f"New quotes added: {stats['quotes_added']}")
    print(f"Duplicates skipped: {stats['quotes_skipped']}")
    print(f"Total quotes in database: {total_quotes}")
    print(f"Average quotes per tag: {total_quotes / len(quotes_db):.1f}")

    # Show tags with most/fewest quotes
    print("\nTags with most quotes:")
    sorted_tags = sorted(quotes_db.items(), key=lambda x: len(x[1]), reverse=True)[:5]
    for tag, quotes in sorted_tags:
        print(f"  {tag}: {len(quotes)} quotes")

    print("\nTags with fewest quotes:")
    sorted_tags = sorted(quotes_db.items(), key=lambda x: len(x[1]))[:5]
    for tag, quotes in sorted_tags:
        print(f"  {tag}: {len(quotes)} quotes")


if __name__ == "__main__":
    generate_quotes_database()
