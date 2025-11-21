#!/usr/bin/env python3
"""
Enhanced Options Generator
Creates YAML configuration with tags and authors from the quote database
"""

import json
from pathlib import Path
import yaml

# Get the script's directory and navigate to project root
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
DATA_DIR = PROJECT_ROOT / "data"
TAGS_DIR = DATA_DIR / "tags"
AUTHORS_DIR = DATA_DIR / "authors"
OUTPUT_FILE_DATA = DATA_DIR / "options.yml"


def slugify(text: str) -> str:
    """Convert text to URL-friendly slug"""
    import re
    text = text.lower()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[-\s]+', '-', text)
    return text.strip('-')


def load_tag_stats() -> dict:
    """Load all tag files and return statistics"""
    tag_stats = {}

    if not TAGS_DIR.exists():
        print(f"Warning: Tags directory not found at {TAGS_DIR}")
        return tag_stats

    for tag_file in TAGS_DIR.glob("*.json"):
        try:
            with open(tag_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                tag_name = data.get("tag", tag_file.stem)
                count = data.get("count", 0)
                tag_stats[tag_name] = count
        except Exception as e:
            print(f"Warning: Could not load {tag_file.name}: {e}")

    return tag_stats


def load_author_stats() -> dict:
    """Load all author files and return statistics"""
    author_stats = {}

    if not AUTHORS_DIR.exists():
        print(f"Warning: Authors directory not found at {AUTHORS_DIR}")
        return author_stats

    for author_file in AUTHORS_DIR.glob("*.json"):
        try:
            with open(author_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                author_name = data.get("author", "Unknown")
                slug = data.get("slug", author_file.stem)
                count = data.get("count", 0)
                author_stats[author_name] = {"slug": slug, "count": count}
        except Exception as e:
            print(f"Warning: Could not load {author_file.name}: {e}")

    return author_stats


def create_options_yml():
    print("=" * 60)
    print("Quote Plugin Options Generator")
    print("=" * 60)
    print()

    # Load statistics
    print("Loading tag statistics...")
    tag_stats = load_tag_stats()
    print(f"✓ Loaded {len(tag_stats)} tags")

    print("Loading author statistics...")
    author_stats = load_author_stats()
    print(f"✓ Loaded {len(author_stats)} authors")
    print()

    # Calculate totals for description
    total_quotes = sum(tag_stats.values())
    total_tags = len(tag_stats)
    total_authors = len(author_stats)

    # Create the custom fields
    custom_fields = []

    # About field with statistics
    about_field = {
        'keyname': 'about',
        'name': 'About This Plugin',
        'field_type': 'author_bio',
        'description': f'Daily inspirational quotes from a curated collection. Database contains {total_quotes} unique quotes across {total_tags} different tags from {total_authors} unique authors.',
        'github_url': 'https://github.com/ExcuseMi/trmnl-more-quotes.plugin'
    }
    custom_fields.append(about_field)

    # Tags field
    if tag_stats:
        # Sort tags alphabetically
        sorted_tags = sorted(tag_stats.items(), key=lambda x: x[0])

        tag_options = []
        for tag_name, count in sorted_tags:
            tag_options.append({f"{tag_name.capitalize()}: {count}": tag_name})

        tags_field = {
            'keyname': 'tags',
            'field_type': 'select',
            'name': 'Tags',
            'description': f'Select one or more tags to filter quotes. {total_tags} tags available.',
            'multiple': True,
            'help_text': 'Use <kbd>⌘</kbd>+<kbd>click</kbd> (Mac) or <kbd>ctrl</kbd>+<kbd>click</kbd> (Windows) to select multiple items. Use <kbd>Shift</kbd>+<kbd>click</kbd> to select a whole range at once.',
            'options': tag_options
        }
        custom_fields.append(tags_field)
    else:
        print("Warning: No tags found, skipping tags field")

    # # Authors field
    # if author_stats:
    #     # Filter authors with at least 10 quotes
    #     filtered_authors = {author: stats for author, stats in author_stats.items() if stats["count"] >= 10}
    #
    #     if filtered_authors:
    #         # Sort authors by count (descending), then alphabetically
    #         sorted_authors = sorted(
    #             filtered_authors.items(),
    #             key=lambda x: (-x[1]["count"], x[0])
    #         )
    #
    #         author_options = []
    #         for author_name, stats in sorted_authors:
    #             author_slug = stats["slug"]
    #             count = stats["count"]
    #             author_options.append({f"{author_name}: {count}": author_slug})
    #
    #         authors_field = {
    #             'keyname': 'authors',
    #             'field_type': 'select',
    #             'name': 'Authors',
    #             'description': f'Select one or more authors to filter quotes. {len(filtered_authors)} authors available (minimum 10 quotes per author).',
    #             'multiple': True,
    #             'help_text': 'Use <kbd>⌘</kbd>+<kbd>click</kbd> (Mac) or <kbd>ctrl</kbd>+<kbd>click</kbd> (Windows) to select multiple items. Use <kbd>Shift</kbd>+<kbd>click</kbd> to select a whole range at once.',
    #             'options': author_options
    #         }
    #         custom_fields.append(authors_field)
    #
    #         excluded_count = len(author_stats) - len(filtered_authors)
    #         if excluded_count > 0:
    #             print(f"  Note: Excluded {excluded_count} authors with less than 10 quotes")
    #     else:
    #         print("Warning: No authors with 10+ quotes found, skipping authors field")
    # else:
    #     print("Warning: No authors found, skipping authors field")

    # Use custom YAML representer to format the output properly
    def represent_dict_order(dumper, data):
        return dumper.represent_mapping('tag:yaml.org,2002:map', data.items())

    yaml.add_representer(dict, represent_dict_order)

    print(f"Writing to: {OUTPUT_FILE_DATA.absolute()}")

    with open(OUTPUT_FILE_DATA, 'w', encoding='utf-8') as f:
        yaml.dump(custom_fields, f, default_flow_style=False, allow_unicode=True, sort_keys=False, width=1000)

    print(f"✓ Successfully created {OUTPUT_FILE_DATA}")

    # Print summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Total quotes: {total_quotes}")
    print(f"Total tags: {total_tags}")
    print(f"Total authors: {total_authors}")
    print(f"Fields created: {len(custom_fields)}")

    if tag_stats:
        print("\nTop 10 tags by quote count:")
        sorted_tags = sorted(tag_stats.items(), key=lambda x: x[1], reverse=True)[:10]
        for tag, count in sorted_tags:
            print(f"  {tag}: {count}")

    if author_stats:
        print("\nTop 10 authors by quote count:")
        sorted_authors = sorted(author_stats.items(), key=lambda x: x[1]["count"], reverse=True)[:10]
        for author, stats in sorted_authors:
            print(f"  {author}: {stats['count']}")


if __name__ == "__main__":
    create_options_yml()