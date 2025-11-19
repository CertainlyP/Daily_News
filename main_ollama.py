#!/usr/bin/env python3
"""
TTP Monitoring System - Ollama Version (No API Required)

Daily threat intelligence monitoring system that:
1. Fetches content from Twitter and articles
2. Analyzes content with LOCAL Ollama LLM (FREE)
3. Generates HTML report with actionable intelligence

This version uses Ollama for FREE local AI analysis - no Claude API needed!
"""

import os
import sys
import json
from datetime import datetime
from pathlib import Path

from fetcher import ContentFetcher
from ollama_analyzer import OllamaTTPAnalyzer
from report_generator import ReportGenerator


def main():
    """Main execution flow."""
    print("=== TTP Monitoring System (Ollama Edition) ===\n")

    # Create output directory
    output_dir = Path('reports')
    output_dir.mkdir(exist_ok=True)

    try:
        # Initialize Ollama analyzer
        print("🦙 Initializing Ollama analyzer...")
        print("-" * 50)

        # You can change the model here if you want to use a different one
        # Options: llama3.1, gemma2:9b, mixtral, qwen2.5:14b
        model = os.getenv('OLLAMA_MODEL', 'llama3.1')

        try:
            analyzer = OllamaTTPAnalyzer(model=model)
            print(f"✓ Connected to Ollama (model: {model})\n")
        except ConnectionError as e:
            print(f"❌ ERROR: {e}")
            print("\nQuick fix:")
            print("  1. Install Ollama: curl -fsSL https://ollama.com/install.sh | sh")
            print("  2. Pull model: ollama pull llama3.1")
            print("  3. Start Ollama: ollama serve")
            sys.exit(1)

        # Step 1: Fetch content
        print("📡 Step 1: Fetching content from sources...")
        print("-" * 50)
        fetcher = ContentFetcher()
        content_items = fetcher.fetch_all()
        print(f"\n✓ Fetched {len(content_items)} items total\n")

        if not content_items:
            print("⚠️  No content fetched. Check your configuration.")
            sys.exit(0)

        # Step 2: Analyze with Ollama
        print("🤖 Step 2: Analyzing content with Ollama (local LLM)...")
        print("-" * 50)
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
