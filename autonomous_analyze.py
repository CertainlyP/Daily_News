#!/usr/bin/env python3
"""
Autonomous Analysis Script for Claude Code Agent

This script is designed to be executed BY Claude Code, not by you.
Claude will read the fetched content, analyze it using its intelligence,
and generate the structured JSON output.

Usage:
  User: "Run autonomous analysis on the latest fetched content"
  Claude: [executes this, reads content, analyzes, saves results]
"""

import json
import sys
from pathlib import Path
from datetime import datetime


def get_latest_content_file():
    """Find the most recent content file."""
    content_dir = Path('fetched_content')
    if not content_dir.exists():
        return None

    files = sorted(content_dir.glob('content_*.json'), reverse=True)
    return files[0] if files else None


def main():
    """Main entry point - just loads and displays content for Claude to analyze."""

    # Find latest content file
    content_file = get_latest_content_file()

    if not content_file:
        print("ERROR: No fetched content found.")
        print("Run: python fetch_content.py first")
        sys.exit(1)

    # Load the content
    with open(content_file, 'r') as f:
        items = json.load(f)

    print(f"Found {len(items)} items in {content_file}")
    print("\nThis script should be run BY Claude Code agent.")
    print("Claude will autonomously analyze all items and generate the report.")
    print("\nContent loaded successfully. Claude can now analyze it.")

    return content_file, items


if __name__ == "__main__":
    content_file, items = main()
    print(f"\nReady for analysis: {len(items)} items from {content_file}")
