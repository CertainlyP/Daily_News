#!/usr/bin/env python3
"""
Step 1: Fetch content from sources and save to JSON
No API needed - just collects raw content
"""

import os
import json
from datetime import datetime
from pathlib import Path
from fetcher import ContentFetcher


def main():
    """Fetch content and save to JSON file."""
    print("=== TTP Content Fetcher ===\n")

    # Create output directory
    output_dir = Path('fetched_content')
    output_dir.mkdir(exist_ok=True)

    try:
        # Fetch content
        print("📡 Fetching content from sources...")
        print("-" * 50)
        fetcher = ContentFetcher()
        content_items = fetcher.fetch_all()
        print(f"\n✓ Fetched {len(content_items)} items total\n")

        if not content_items:
            print("⚠️  No content fetched. Check your configuration.")
            return

        # Save to JSON
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = output_dir / f'content_{timestamp}.json'

        with open(output_file, 'w') as f:
            json.dump(content_items, f, indent=2)

        print(f"{'=' * 50}")
        print(f"✅ Content saved: {output_file}")
        print(f"{'=' * 50}")
        print(f"\n📊 Next step: Run format_for_claude.py to prepare for analysis")
        print(f"   python format_for_claude.py {output_file}")
        print()

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
