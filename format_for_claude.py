#!/usr/bin/env python3
"""
Step 2: Format fetched content for Claude Code analysis
Outputs markdown-formatted content for easy analysis
"""

import json
import sys
from pathlib import Path


def format_for_analysis(content_file):
    """Format content items for Claude Code to analyze."""

    with open(content_file, 'r') as f:
        items = json.load(f)

    if not items:
        print("No items to analyze.")
        return

    print(f"Found {len(items)} items to analyze.\n")
    print("=" * 70)
    print("CONTENT FOR CLAUDE CODE ANALYSIS")
    print("=" * 70)
    print()
    print("Copy the content below and paste it to Claude Code.")
    print("Claude will analyze each item and return structured JSON.")
    print()
    print("=" * 70)
    print()

    # Format each item
    for i, item in enumerate(items, 1):
        source = item.get('source', 'unknown')
        url = item.get('url', 'no-url')
        content = item.get('content', '')

        print(f"### ITEM {i}/{len(items)}")
        print(f"**Source:** {source}")
        print(f"**URL:** {url}")
        print(f"**Content:**")
        print()
        print(content[:4000])  # Limit to first 4000 chars
        if len(content) > 4000:
            print("\n[... content truncated ...]")
        print()
        print("-" * 70)
        print()

    print()
    print("=" * 70)
    print("INSTRUCTIONS FOR CLAUDE CODE")
    print("=" * 70)
    print()
    print("Analyze each item above using the TTP analysis prompts:")
    print("1. Classify content type (ioc_based, technique_research, tool_analysis, etc.)")
    print("2. Extract intelligence based on type")
    print("3. Return results as a JSON array with this structure:")
    print()
    print("""[
  {
    "source_url": "url from item",
    "content_type": "ioc_based/technique_research/tool_analysis/etc",
    "data": { /* extracted intelligence */ }
  },
  ...
]""")
    print()
    print("Save Claude's JSON output to a file, then run:")
    print(f"python generate_report.py <claude_output.json>")
    print()


def main():
    if len(sys.argv) < 2:
        print("Usage: python format_for_claude.py <content_json_file>")
        print("\nAvailable files:")
        content_dir = Path('fetched_content')
        if content_dir.exists():
            files = sorted(content_dir.glob('content_*.json'), reverse=True)
            for f in files[:5]:  # Show last 5
                print(f"  - {f}")
        sys.exit(1)

    content_file = sys.argv[1]
    if not Path(content_file).exists():
        print(f"Error: File not found: {content_file}")
        sys.exit(1)

    format_for_analysis(content_file)


if __name__ == "__main__":
    main()
