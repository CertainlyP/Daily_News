#!/usr/bin/env python3
"""
Interactive analysis helper for Claude Code workflow
Presents content items for easy analysis
"""

import json
import sys
from pathlib import Path


def load_ttp_prompts():
    """Load the TTP analysis prompts from ttp_analyzer.py"""
    return {
        "ioc_based": """Extract technical threat intelligence. You're analyzing for a security analyst - skip basics, give actionable details.

Return ONLY valid JSON:
{
  "threat_name": "name",
  "iocs": {
    "ips": [],
    "domains": [],
    "urls": [],
    "hashes": {"sha256": [], "md5": [], "sha1": []},
    "file_names": [],
    "registry_keys": [],
    "mutex": [],
    "user_agents": [],
    "email_subjects": []
  },
  "infrastructure": {
    "hosting_provider": "",
    "asn": "",
    "registrar": "",
    "ssl_certs": []
  },
  "technical_details": {
    "execution_flow": "actual command line / process tree",
    "obfuscation": "how it's packed/obfuscated",
    "persistence_mechanism": "exact registry key or scheduled task",
    "c2_protocol": "HTTP/HTTPS/DNS/custom",
    "encryption": "what encryption used",
    "sandbox_evasion": "anti-analysis tricks"
  },
  "detection_queries": [
    "KQL queries for MDO/Defender/Sentinel",
    "specific EDR detection logic"
  ],
  "sample_info": {
    "sample_links": ["any.run/virustotal/hybrid-analysis links"],
    "yara_rules": "YARA rule if provided"
  },
  "key_findings": "the actual sauce - what's new/interesting about this threat"
}""",

        "technique_research": """Extract details about this attack technique or research. Focus on what matters for detection.

Return ONLY valid JSON:
{
  "technique_name": "",
  "attack_vector": "how it works technically",
  "prerequisites": "what attacker needs",
  "detection_gap": "why current tools miss it",
  "detection_ideas": [
    "specific ways to detect this",
    "telemetry sources to monitor",
    "behavioral indicators"
  ],
  "affected_products": ["EDR/product names that are blind to this"],
  "mitigation": "how to prevent or reduce risk",
  "poc_available": true | false,
  "key_takeaway": "why this matters for your environment - what to do about it"
}""",

        "tool_analysis": """Analyze this security tool from a detection perspective.

Return ONLY valid JSON:
{
  "tool_name": "",
  "tool_purpose": "what it does",
  "capabilities": ["list of key features"],
  "detection_methods": [
    "how to detect usage in your environment",
    "specific IOCs or behaviors"
  ],
  "legitimate_use_cases": ["when it's benign"],
  "malicious_use_cases": ["how attackers use it"],
  "telemetry_sources": ["where to look for it - EDR/network/email"],
  "key_takeaway": "should you monitor for this? how?"
}""",

        "threat_actor_profile": """Extract threat actor intelligence.

Return ONLY valid JSON:
{
  "actor_name": "",
  "aliases": [],
  "targeting": {
    "industries": [],
    "geos": [],
    "motivation": "financial/espionage/destructive"
  },
  "ttp_changes": "what's new in their playbook",
  "infrastructure_patterns": "their infrastructure style/preferences",
  "recent_activity": "latest campaigns or changes",
  "watch_for": "specific things to monitor in your environment if you match their targeting"
}""",

        "vulnerability_analysis": """Extract vulnerability details.

Return ONLY valid JSON:
{
  "cve_id": "",
  "affected_products": [],
  "severity": "critical/high/medium/low",
  "exploit_available": true | false,
  "exploit_complexity": "easy/medium/hard",
  "attack_vector": "how it's exploited",
  "detection_methods": ["how to detect exploitation attempts"],
  "mitigation": "patching info or workarounds",
  "observed_in_wild": true | false,
  "key_takeaway": "do you need to act on this immediately?"
}""",

        "detection_engineering": """Extract detection engineering intelligence.

Return ONLY valid JSON:
{
  "detection_name": "",
  "what_it_detects": "specific threat or behavior",
  "data_sources": ["telemetry needed"],
  "detection_logic": "the actual query or rule",
  "false_positive_potential": "low/medium/high",
  "tuning_recommendations": "how to reduce FPs",
  "coverage": "what this does and doesn't catch",
  "key_takeaway": "should you implement this?"
}""",

        "generic": """Summarize this security content from an analyst perspective.

Return ONLY valid JSON:
{
  "summary": "what this is about",
  "actionable_items": ["things you should do based on this"],
  "relevance": "why this matters or doesn't matter"
}"""
    }


def present_items_for_analysis(content_file, batch_size=3):
    """Present content items in batches for analysis."""

    with open(content_file, 'r') as f:
        items = json.load(f)

    if not items:
        print("No items to analyze.")
        return

    prompts = load_ttp_prompts()

    print(f"\n{'=' * 70}")
    print(f"CLAUDE CODE ANALYSIS WORKFLOW")
    print(f"{'=' * 70}\n")
    print(f"Total items: {len(items)}")
    print(f"Batch size: {batch_size} items at a time\n")

    # Process in batches
    for batch_num in range(0, len(items), batch_size):
        batch = items[batch_num:batch_num + batch_size]
        batch_end = min(batch_num + batch_size, len(items))

        print(f"\n{'=' * 70}")
        print(f"BATCH {batch_num // batch_size + 1}: Items {batch_num + 1}-{batch_end}")
        print(f"{'=' * 70}\n")

        for i, item in enumerate(batch, start=batch_num + 1):
            source = item.get('source', 'unknown')
            url = item.get('url', 'no-url')
            content = item.get('content', '')

            print(f"\n{'─' * 70}")
            print(f"ITEM {i}/{len(items)}")
            print(f"{'─' * 70}")
            print(f"Source: {source}")
            print(f"URL: {url}")
            print(f"\nContent:\n")
            # Limit content to reasonable size
            print(content[:6000])
            if len(content) > 6000:
                print("\n[... content truncated ...]")
            print(f"\n{'─' * 70}\n")

        print(f"\n{'=' * 70}")
        print(f"ANALYSIS INSTRUCTIONS FOR THIS BATCH")
        print(f"{'=' * 70}\n")
        print("For each item above:")
        print("1. First classify the content type")
        print("2. Use the appropriate prompt below to extract intelligence")
        print("3. Return JSON in this structure:")
        print("""
{
  "source_url": "<url from item>",
  "content_type": "<type>",
  "data": { <extracted intelligence> }
}
""")
        print("\nAvailable content types and their prompts:")
        print("- ioc_based")
        print("- technique_research")
        print("- tool_analysis")
        print("- threat_actor_profile")
        print("- vulnerability_analysis")
        print("- detection_engineering")
        print("- generic (fallback)")

        print(f"\n{'=' * 70}")
        print("Waiting for your analysis...")
        print("Paste the full prompt reference below when ready:")
        print(f"{'=' * 70}\n")

        # Show relevant prompts
        print("PROMPT REFERENCE (copy these as needed):\n")
        for content_type, prompt in prompts.items():
            print(f"--- {content_type.upper()} ---")
            print(prompt)
            print()

        if batch_end < len(items):
            input(f"\nPress Enter to continue to next batch...")


def main():
    if len(sys.argv) < 2:
        print("Usage: python analyze_with_claude.py <content_json_file> [batch_size]")
        print("\nThis script helps you analyze content with Claude Code")
        print("by presenting items in manageable batches.\n")
        print("Available files:")
        content_dir = Path('fetched_content')
        if content_dir.exists():
            files = sorted(content_dir.glob('content_*.json'), reverse=True)
            for f in files[:5]:
                print(f"  - {f}")
        sys.exit(1)

    content_file = sys.argv[1]
    batch_size = int(sys.argv[2]) if len(sys.argv) > 2 else 3

    if not Path(content_file).exists():
        print(f"Error: File not found: {content_file}")
        sys.exit(1)

    present_items_for_analysis(content_file, batch_size)

    print(f"\n{'=' * 70}")
    print("NEXT STEPS")
    print(f"{'=' * 70}\n")
    print("1. Save Claude's JSON responses to a file (e.g., analysis_results.json)")
    print("2. Combine all batch results into a JSON array")
    print("3. Run: python generate_report.py analysis_results.json")
    print()


if __name__ == "__main__":
    main()
