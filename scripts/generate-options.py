import json
from pathlib import Path
import yaml

# Get the script's directory and navigate to project root
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
DATA_DIR = PROJECT_ROOT / "data"
OUTPUT_FILE_DATA = DATA_DIR / "options.yml"


def create_options_yml():
    print("=" * 60)
    print("TV Plan Options Generator")
    print("=" * 60)

    # Load data


    # Create the custom fields
    custom_fields = []
    about_field = {
        'keyname': 'about',
        'name': 'About This Plugin',
        'field_type': 'author_bio',
        'github_url': 'https://github.com/ExcuseMi/trmnl-quotes.plugin'
    }
    custom_fields.append(about_field)

    options = [
        "motivation",
        "inspiration",
        "life",
        "wisdom",
        "love",
        "success",
        "leadership",
        "happiness",
        "change",
        "perseverance",
        "mindfulness",
        "growth",
        "courage",
        "gratitude",
        "resilience",
        "friendship",
        "creativity",
        "humility",
        "forgiveness",
        "patience",
        "integrity",
        "self-reflection",
        "empathy",
        "purpose",
        "justice",
        "harmony",
        "knowledge",
        "hope",
        "anger",
        "fear",
        "general"
    ]
    options = sorted(options)
    # Channels field
    channels_field = {
        'keyname': 'tags',
        'field_type': 'select',
        'name': f'Tags',
        'description': 'Select the tags.',
        'multiple': True,
        'help_text': 'Use <kbd>⌘</kbd>+<kbd>click</kbd> (Mac) or <kbd>ctrl</kbd>+<kbd>click</kbd> (Windows) to select multiple items. Use <kbd>Shift</kbd>+<kbd>click</kbd> to select a whole range at once.',
        'options': options,
        'optional': True
    }
    custom_fields.append(channels_field)
    # Use custom YAML representer to format the output properly
    def represent_dict_order(dumper, data):
        return dumper.represent_mapping('tag:yaml.org,2002:map', data.items())

    yaml.add_representer(dict, represent_dict_order)


    print(f"\nWriting to: {OUTPUT_FILE_DATA.absolute()}")

    with open(OUTPUT_FILE_DATA, 'w', encoding='utf-8') as f:
        yaml.dump(custom_fields, f, default_flow_style=False, allow_unicode=True, sort_keys=False, width=1000)

    print(f"✓ Successfully created {OUTPUT_FILE_DATA}")

    # Print summary
    print("SUMMARY")


if __name__ == "__main__":
    create_options_yml()