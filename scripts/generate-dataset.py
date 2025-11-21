#!/usr/bin/env python3
"""
Enhanced Quote Collection Script
Fetches quotes from multiple free APIs
Uses flattened structure with embedded tags
Generates separate tag and author files for filtering
"""

import json
import requests
import time
import random
from pathlib import Path
from typing import Dict, List, Tuple
import urllib3
import re

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Get the script's directory and navigate to project root
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
DATA_DIR = PROJECT_ROOT / "data"
TAGS_DIR = DATA_DIR / "tags"
AUTHORS_DIR = DATA_DIR / "authors"
OUTPUT_FILE = DATA_DIR / "quotes.json"

# Ensure directories exist
DATA_DIR.mkdir(exist_ok=True)
TAGS_DIR.mkdir(exist_ok=True)
AUTHORS_DIR.mkdir(exist_ok=True)

# Enhanced tag mappings with focus on war/military
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
    "general": ["life", "wisdom", "philosophy"],
    "war": ["war", "battle", "military", "strategy", "combat", "warfare", "soldier", "army", "conflict"],
    "strategy": ["strategy", "tactics", "planning", "military strategy"],
    "peace": ["peace", "harmony", "tranquility", "diplomacy"]
}

# Famous military leaders and strategists
MILITARY_AUTHORS = [
    "Sun Tzu", "Carl von Clausewitz", "Napoleon Bonaparte", "Julius Caesar",
    "Alexander the Great", "George Patton", "Dwight Eisenhower", "Winston Churchill",
    "Douglas MacArthur", "Erwin Rommel", "Horatio Nelson", "Genghis Khan",
    "George Washington", "Robert E. Lee", "Ulysses S. Grant", "Che Guevara",
    "Vo Nguyen Giap", "Simo Häyhä", "Audie Murphy", "Leonidas"
]

# Manual war quotes database as fallback
MANUAL_WAR_QUOTES = [
    {
        "text": "The supreme art of war is to subdue the enemy without fighting.",
        "author": "Sun Tzu",
        "source": "The Art of War",
        "tags": ["war", "strategy", "wisdom"]
    },
    {
        "text": "Appear weak when you are strong, and strong when you are weak.",
        "author": "Sun Tzu",
        "source": "The Art of War",
        "tags": ["war", "strategy"]
    },
    {
        "text": "If you know the enemy and know yourself, you need not fear the result of a hundred battles.",
        "author": "Sun Tzu",
        "source": "The Art of War",
        "tags": ["war", "strategy", "knowledge"]
    },
    {
        "text": "War is the continuation of politics by other means.",
        "author": "Carl von Clausewitz",
        "source": "On War",
        "tags": ["war", "philosophy"]
    },
    {
        "text": "In war, the moral is to the physical as three is to one.",
        "author": "Napoleon Bonaparte",
        "source": "Military Maxims",
        "tags": ["war", "leadership"]
    },
    {
        "text": "I came, I saw, I conquered.",
        "author": "Julius Caesar",
        "source": "Latin Quote",
        "tags": ["war", "leadership"]
    },
    {
        "text": "There is no instance of a nation benefiting from prolonged warfare.",
        "author": "Sun Tzu",
        "source": "The Art of War",
        "tags": ["war", "strategy", "wisdom"]
    },
    {
        "text": "The object of war is not to die for your country but to make the other bastard die for his.",
        "author": "George Patton",
        "source": "Speech to troops",
        "tags": ["war", "strategy"]
    },
    {
        "text": "Never interrupt your enemy when he is making a mistake.",
        "author": "Napoleon Bonaparte",
        "source": "Military Maxims",
        "tags": ["war", "strategy", "wisdom"]
    }
]


def slugify(text: str) -> str:
    """Convert text to URL-friendly slug"""
    text = text.lower()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[-\s]+', '-', text)
    return text.strip('-')


def load_existing_quotes() -> List[Dict]:
    """Load existing quotes database (flat structure)"""
    if OUTPUT_FILE.exists():
        try:
            with open(OUTPUT_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Handle both old nested and new flat structure
                if isinstance(data, dict):
                    if "quotes" in data:
                        return data["quotes"]
                    else:
                        # Convert old nested structure to flat
                        print("  Converting old nested structure to flat...")
                        all_quotes = []
                        for tag, quotes in data.items():
                            for quote in quotes:
                                if "tags" not in quote:
                                    quote["tags"] = [tag]
                                all_quotes.append(quote)
                        return all_quotes
                elif isinstance(data, list):
                    return data
        except Exception as e:
            print(f"Warning: Could not load existing quotes: {e}")
            return []
    return []


def fetch_from_quotable(tag: str, limit: int = 50) -> List[Dict]:
    """Fetch quotes from api.quotable.io"""
    quotes = []
    keywords = TAG_KEYWORDS.get(tag, ["life"])

    for keyword in keywords[:3]:
        try:
            url = f"https://api.quotable.io/quotes/random?tags={keyword}&limit={limit}"
            response = requests.get(url, timeout=10, verify=False)

            if response.status_code == 200:
                data = response.json()
                for item in data:
                    quotes.append({
                        "text": item.get("content", ""),
                        "author": item.get("author", "Unknown"),
                        "source": "quotable.io",
                        "tags": [tag]
                    })
                print(f"  ✓ Fetched {len(data)} quotes for '{tag}' (keyword: {keyword}) from quotable.io")
                time.sleep(0.5)
        except Exception as e:
            print(f"  ✗ Error fetching from quotable.io for '{tag}' (keyword: {keyword}): {e}")

    return quotes


def fetch_from_zenquotes(tag: str) -> List[Dict]:
    """Fetch quotes from zenquotes.io"""
    quotes = []
    try:
        url = "https://zenquotes.io/api/quotes"
        response = requests.get(url, timeout=10, verify=False)

        if response.status_code == 200:
            data = response.json()
            keywords = TAG_KEYWORDS.get(tag, ["life"])

            for item in data:
                quote_text = item.get("q", "").lower()
                if any(keyword.lower() in quote_text for keyword in keywords):
                    quotes.append({
                        "text": item.get("q", ""),
                        "author": item.get("a", "Unknown"),
                        "source": "zenquotes.io",
                        "tags": [tag]
                    })

            if quotes:
                print(f"  ✓ Fetched {len(quotes)} quotes for '{tag}' from zenquotes.io")

        time.sleep(1)
    except Exception as e:
        print(f"  ✗ Error fetching from zenquotes.io for '{tag}': {e}")

    return quotes


def fetch_from_quotable_search(tag: str, limit: int = 30) -> List[Dict]:
    """Fetch quotes using quotable.io search endpoint"""
    quotes = []
    keywords = TAG_KEYWORDS.get(tag, ["life"])

    for keyword in keywords[:3]:
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
                        "source": "quotable.io",
                        "tags": [tag]
                    })

                if results:
                    print(f"  ✓ Fetched {len(results)} quotes for '{tag}' (keyword: {keyword}) from quotable.io search")

            time.sleep(0.5)
        except Exception as e:
            print(f"  ✗ Error fetching from quotable.io search for '{tag}' (keyword: {keyword}): {e}")

    return quotes


def fetch_military_quotes() -> List[Dict]:
    """Specialized function to fetch war and military quotes"""
    print("  🎯 Fetching military/war quotes from specialized sources...")
    military_quotes = []

    military_quotes.extend(fetch_quotes_by_military_authors())
    military_quotes.extend(MANUAL_WAR_QUOTES)

    war_keywords = ["war", "battle", "military", "strategy", "soldier", "army", "victory", "defeat"]

    for keyword in war_keywords[:4]:
        try:
            url = f"https://api.quotable.io/search/quotes?query={keyword}&limit=20"
            response = requests.get(url, timeout=10, verify=False)

            if response.status_code == 200:
                data = response.json()
                for item in data.get("results", []):
                    quote_text = item.get("content", "").lower()
                    if any(war_word in quote_text for war_word in war_keywords):
                        military_quotes.append({
                            "text": item.get("content", ""),
                            "author": item.get("author", "Unknown"),
                            "source": "quotable.io",
                            "tags": ["war", "military"]
                        })
        except Exception as e:
            print(f"  ✗ Error fetching war quotes for keyword '{keyword}': {e}")

        time.sleep(0.3)

    unique_quotes = []
    seen_texts = set()

    for quote in military_quotes:
        text = quote["text"].strip().lower()
        if text and text not in seen_texts:
            unique_quotes.append(quote)
            seen_texts.add(text)

    print(f"  ✓ Collected {len(unique_quotes)} unique military/war quotes")
    return unique_quotes


def fetch_quotes_by_military_authors() -> List[Dict]:
    """Fetch quotes specifically from famous military leaders and strategists"""
    quotes = []

    for author in MILITARY_AUTHORS[:8]:
        try:
            encoded_author = requests.utils.quote(author)
            url = f"https://api.quotable.io/quotes?author={encoded_author}&limit=15"
            response = requests.get(url, timeout=10, verify=False)

            if response.status_code == 200:
                data = response.json()
                results = data.get("results", [])

                for item in results:
                    quotes.append({
                        "text": item.get("content", ""),
                        "author": item.get("author", "Unknown"),
                        "source": "quotable.io",
                        "tags": ["war", "military", "strategy"]
                    })

                if results:
                    print(f"    ✓ Found {len(results)} quotes by {author}")

            time.sleep(0.5)

        except Exception as e:
            print(f"    ✗ Error fetching quotes for {author}: {e}")

    return quotes


def fetch_from_quotable_by_author(tag: str, limit: int = 20) -> List[Dict]:
    """Fetch quotes from famous authors related to the tag"""
    quotes = []
    author_map = {
        "motivation": ["Tony Robbins", "Zig Ziglar", "Dale Carnegie"],
        "inspiration": ["Maya Angelou", "Helen Keller", "Walt Disney"],
        "wisdom": ["Confucius", "Socrates", "Aristotle"],
        "leadership": ["John C. Maxwell", "Peter Drucker", "Simon Sinek"],
        "success": ["Napoleon Hill", "Stephen Covey", "Jim Rohn"],
        "war": MILITARY_AUTHORS[:3],
        "strategy": ["Sun Tzu", "Carl von Clausewitz", "Niccolò Machiavelli"]
    }

    authors = author_map.get(tag, [])

    for author in authors[:2]:
        try:
            encoded_author = requests.utils.quote(author)
            url = f"https://api.quotable.io/quotes?author={encoded_author}&limit={limit}"
            response = requests.get(url, timeout=10, verify=False)

            if response.status_code == 200:
                data = response.json()
                results = data.get("results", [])

                for item in results:
                    quotes.append({
                        "text": item.get("content", ""),
                        "author": item.get("author", "Unknown"),
                        "source": "quotable.io",
                        "tags": [tag]
                    })

                if results:
                    print(f"  ✓ Fetched {len(results)} quotes for '{tag}' from author '{author}'")

            time.sleep(0.5)
        except Exception as e:
            print(f"  ✗ Error fetching from author '{author}': {e}")

    return quotes


def merge_quotes(existing: List[Dict], new: List[Dict]) -> Tuple[List[Dict], int]:
    """Merge new quotes with existing ones, removing duplicates based on text"""
    existing_texts = {quote["text"].strip().lower() for quote in existing}

    merged = existing.copy()
    added = 0

    for quote in new:
        text = quote["text"].strip()
        if text and text.lower() not in existing_texts:
            merged.append(quote)
            existing_texts.add(text.lower())
            added += 1

    return merged, added


def organize_by_tags(all_quotes: List[Dict]) -> Dict[str, List[Dict]]:
    """Organize quotes by tags"""
    tags_db = {}

    for quote in all_quotes:
        tags = quote.get("tags", [])
        for tag in tags:
            if tag not in tags_db:
                tags_db[tag] = []

            # Check for duplicates in this tag
            quote_texts = {q["text"].strip().lower() for q in tags_db[tag]}
            if quote["text"].strip().lower() not in quote_texts:
                tags_db[tag].append(quote)

    return tags_db


def organize_by_authors(all_quotes: List[Dict]) -> Dict[str, List[Dict]]:
    """Organize quotes by author"""
    authors_db = {}

    for quote in all_quotes:
        author = quote.get("author", "Unknown")
        if author not in authors_db:
            authors_db[author] = []

        # Check for duplicates
        quote_texts = {q["text"].strip().lower() for q in authors_db[author]}
        if quote["text"].strip().lower() not in quote_texts:
            authors_db[author].append(quote)

    return authors_db


def save_tag_files(tags_db: Dict[str, List[Dict]]):
    """Save individual tag files"""
    print(f"\nSaving tag files to: {TAGS_DIR.absolute()}")

    for tag, quotes in tags_db.items():
        tag_file = TAGS_DIR / f"{tag}.json"

        tag_data = {
            "tag": tag,
            "count": len(quotes),
            "quotes": quotes
        }

        with open(tag_file, 'w', encoding='utf-8') as f:
            json.dump(tag_data, f, indent=2, ensure_ascii=False)

        print(f"  ✓ Saved {tag}.json ({len(quotes)} quotes)")

    print(f"\n✓ Successfully saved {len(tags_db)} tag files")


def save_author_files(authors_db: Dict[str, List[Dict]]):
    """Save individual author files with slugified names"""
    print(f"\nSaving author files to: {AUTHORS_DIR.absolute()}")

    for author, quotes in authors_db.items():
        author_slug = slugify(author)
        author_file = AUTHORS_DIR / f"{author_slug}.json"

        author_data = {
            "author": author,
            "slug": author_slug,
            "count": len(quotes),
            "quotes": quotes
        }

        with open(author_file, 'w', encoding='utf-8') as f:
            json.dump(author_data, f, indent=2, ensure_ascii=False)

        print(f"  ✓ Saved {author_slug}.json ({len(quotes)} quotes)")

    print(f"\n✓ Successfully saved {len(authors_db)} author files")


def generate_quotes_database():
    """Generate a comprehensive quotes database with flattened structure"""
    print("=" * 60)
    print("Enhanced Quote Database Generator")
    print("Flattened structure with embedded tags")
    print("=" * 60)
    print()

    print("Loading existing quotes database...")
    all_quotes = load_existing_quotes()

    if all_quotes:
        print(f"✓ Loaded {len(all_quotes)} existing quotes")
    else:
        print("No existing database found. Creating new one.")
    print()

    all_tags = list(TAG_KEYWORDS.keys())
    priority_tags = ["war", "strategy", "courage", "leadership"]

    remaining_tags = [tag for tag in all_tags if tag not in priority_tags]
    random.shuffle(remaining_tags)
    processed_order = priority_tags + remaining_tags

    print(f"Processing {len(processed_order)} tags (war-related tags prioritized)...")
    print()

    stats = {
        "tags_processed": 0,
        "quotes_added": 0,
        "quotes_skipped": 0
    }

    for tag in processed_order:
        print(f"Fetching quotes for tag: '{tag}'")
        new_quotes = []

        if tag == "war":
            new_quotes.extend(fetch_military_quotes())
        else:
            new_quotes.extend(fetch_from_quotable(tag, limit=50))
            new_quotes.extend(fetch_from_quotable_search(tag, limit=30))
            new_quotes.extend(fetch_from_quotable_by_author(tag, limit=20))
            new_quotes.extend(fetch_from_zenquotes(tag))

        before_count = len(all_quotes)
        all_quotes, added = merge_quotes(all_quotes, new_quotes)

        stats["tags_processed"] += 1
        stats["quotes_added"] += added
        stats["quotes_skipped"] += len(new_quotes) - added

        print(f"  → New fetched: {len(new_quotes)}, Added: {added}, Total: {len(all_quotes)}")

        print(f"  💾 Saving progress...")
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump({"quotes": all_quotes}, f, indent=2, ensure_ascii=False)

        print()
        time.sleep(1)

    print(f"\n✓ All changes saved to: {OUTPUT_FILE.absolute()}")

    # Organize and save by tags
    print("\nOrganizing quotes by tags...")
    tags_db = organize_by_tags(all_quotes)
    save_tag_files(tags_db)

    # Organize and save by authors
    print("\nOrganizing quotes by authors...")
    authors_db = organize_by_authors(all_quotes)
    #save_author_files(authors_db)

    # Print summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    unique_authors = len(authors_db)
    unique_tags = len(tags_db)
    print(f"Tags processed: {stats['tags_processed']}")
    print(f"New quotes added: {stats['quotes_added']}")
    print(f"Duplicates skipped: {stats['quotes_skipped']}")
    print(f"Total unique quotes: {len(all_quotes)}")
    print(f"Unique tags: {unique_tags}")
    print(f"Unique authors: {unique_authors}")

    print("\nTags with most quotes:")
    sorted_tags = sorted(tags_db.items(), key=lambda x: len(x[1]), reverse=True)[:5]
    for tag, quotes in sorted_tags:
        print(f"  {tag}: {len(quotes)} quotes")

    print("\nAuthors with most quotes:")
    sorted_authors = sorted(authors_db.items(), key=lambda x: len(x[1]), reverse=True)[:10]
    for author, quotes in sorted_authors:
        print(f"  {author}: {len(quotes)} quotes")


if __name__ == "__main__":
    for i in range(50):
        generate_quotes_database()
        time.sleep(60)