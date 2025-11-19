#!/usr/bin/env python3
"""
TTP Monitoring System - Main Script

Daily threat intelligence monitoring system that:
1. Fetches content from Twitter and articles
2. Analyzes content with Claude API
3. Generates HTML report with actionable intelligence
"""

import os
import sys
import json
from datetime import datetime
from pathlib import Path

from fetcher import ContentFetcher
from ttp_analyzer import TTPAnalyzer
from report_generator import ReportGenerator


def load_env():
    """Load environment variables from .env file."""
    env_path = Path('.env')
    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key] = value


def main():
    """Main execution flow."""
    print("=== TTP Monitoring System ===\n")

    # Load environment variables
    load_env()

    # Verify API key
    if not os.getenv('ANTHROPIC_API_KEY'):
        print("❌ ERROR: ANTHROPIC_API_KEY not set")
        print("   Create a .env file with: ANTHROPIC_API_KEY=your_key_here")
        print("   Or: export ANTHROPIC_API_KEY=your_key")
        sys.exit(1)

    # Create output directory
    output_dir = Path('reports')
    output_dir.mkdir(exist_ok=True)

    try:
        # Step 1: Fetch content
        print("📡 Step 1: Fetching content from sources...")
        print("-" * 50)
        fetcher = ContentFetcher()
        content_items = fetcher.fetch_all()
        print(f"\n✓ Fetched {len(content_items)} items total\n")

        if not content_items:
            print("⚠️  No content fetched. Check your configuration.")
            sys.exit(0)

        # Step 2: Analyze with Claude
        print("🤖 Step 2: Analyzing content with Claude API...")
        print("-" * 50)
        analyzer = TTPAnalyzer()
        analyzed_data = []

        for i, item in enumerate(content_items, 1):
            source = item.get('source', 'unknown')
            url = item.get('url', '')
            content = item.get('content', '')

            print(f"  [{i}/{len(content_items)}] Analyzing {source}...")

            try:
                result = analyzer.analyze(content, url)
                analyzed_data.append(result)

                content_type = result.get('content_type', 'unknown')
                has_data = bool(result.get('data'))
                status = "✓ actionable" if has_data else "- informational"
                print(f"      → {content_type} {status}")

            except Exception as e:
                print(f"      ✗ Error: {e}")
                analyzed_data.append({
                    'source_url': url,
                    'content_type': 'error',
                    'data': None,
                    'error': str(e)
                })

        print(f"\n✓ Analyzed {len(analyzed_data)} items\n")

        # Save raw analyzed data
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        json_output = output_dir / f'ttp_data_{timestamp}.json'
        with open(json_output, 'w') as f:
            json.dump(analyzed_data, f, indent=2)
        print(f"💾 Raw data saved: {json_output}")

        # Step 3: Generate report
        print("\n📄 Step 3: Generating HTML report...")
        print("-" * 50)
        html_output = output_dir / f'ttp_report_{timestamp}.html'

        generator = ReportGenerator()
        generator.generate(analyzed_data, str(html_output))

        print(f"\n{'=' * 50}")
        print(f"✅ COMPLETE!")
        print(f"{'=' * 50}")
        print(f"\n📊 Report: {html_output}")
        print(f"   Open in browser: file://{html_output.absolute()}")
        print()

    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
