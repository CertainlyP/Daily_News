#!/usr/bin/env python3
"""
Step 3: Generate HTML report from Claude's analysis
Takes JSON output from Claude Code and creates the HTML report
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from report_generator import ReportGenerator


def main():
    if len(sys.argv) < 2:
        print("Usage: python generate_report.py <analysis_json_file>")
        print("\nThis script takes the JSON output from Claude Code analysis")
        print("and generates an HTML report.")
        sys.exit(1)

    analysis_file = sys.argv[1]
    if not Path(analysis_file).exists():
        print(f"Error: File not found: {analysis_file}")
        sys.exit(1)

    print("=== Report Generator ===\n")

    # Load analysis data
    with open(analysis_file, 'r') as f:
        analyzed_data = json.load(f)

    print(f"✓ Loaded {len(analyzed_data)} analyzed items")

    # Create output directory
    output_dir = Path('reports')
    output_dir.mkdir(exist_ok=True)

    # Generate report
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    html_output = output_dir / f'ttp_report_{timestamp}.html'

    print("\n📄 Generating HTML report...")
    generator = ReportGenerator()
    generator.generate(analyzed_data, str(html_output))

    print(f"\n{'=' * 50}")
    print(f"✅ REPORT COMPLETE!")
    print(f"{'=' * 50}")
    print(f"\n📊 Report: {html_output}")
    print(f"   Open in browser: file://{html_output.absolute()}")
    print()


if __name__ == "__main__":
    main()
