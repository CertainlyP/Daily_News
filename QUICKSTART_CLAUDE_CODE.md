# Quick Start: Claude Code Workflow

**Perfect for Claude Max users without API access!**

## Prerequisites

- Claude Max subscription (what you're using right now!)
- Python 3.8+
- Dependencies installed: `pip install -r requirements.txt`

## 3-Step Daily Workflow

### Step 1: Fetch Content (1 minute)

```bash
python fetch_content.py
```

This fetches content from your configured sources and saves it to `fetched_content/content_TIMESTAMP.json`.

**First time?** You'll need to:
1. Edit `config.json` to add Twitter accounts and article URLs
2. Run `python setup_twitter.py` (one-time Twitter login)

### Step 2: Analyze with Claude Code (5-10 minutes)

```bash
python analyze_with_claude.py fetched_content/content_LATEST.json
```

This presents content in batches. For each batch:

1. **Copy the content** shown in your terminal
2. **Paste it to Claude Code** (me!) with: "Analyze these threat intelligence items"
3. **I'll return structured JSON** for each item
4. **Save my responses** to a file (e.g., `analysis_results.json`)
5. Continue with next batch

**Pro tip:** Analyze 3-5 items at once for efficiency.

### Step 3: Generate Report (30 seconds)

```bash
python generate_report.py analysis_results.json
```

Opens an HTML report in `reports/ttp_report_TIMESTAMP.html`.

## Example: Full Workflow

```bash
# Morning: Fetch fresh content
python fetch_content.py

# You'll see: "Content saved: fetched_content/content_20250119_090000.json"

# Format for analysis
python analyze_with_claude.py fetched_content/content_20250119_090000.json

# The script shows you items to analyze
# Copy and paste them here to Claude Code
# I'll analyze and return JSON

# Save my JSON responses to: analysis_results.json

# Generate the report
python generate_report.py analysis_results.json

# Open: reports/ttp_report_TIMESTAMP.html
```

## JSON Format I Return

When you ask me to analyze items, I'll return JSON like this:

```json
[
  {
    "source_url": "https://twitter.com/user/status/123",
    "content_type": "ioc_based",
    "data": {
      "threat_name": "AsyncRAT Campaign",
      "iocs": {
        "ips": ["1.2.3.4"],
        "domains": ["evil.com"],
        "hashes": {"sha256": ["abc123..."], "md5": [], "sha1": []}
      },
      "detection_queries": ["DeviceNetworkEvents | where RemoteIP == '1.2.3.4'"],
      "key_findings": "New AsyncRAT variant using DNS tunneling for C2"
    }
  },
  {
    "source_url": "https://blog.example.com/research",
    "content_type": "technique_research",
    "data": {
      "technique_name": "BYOVD - Bring Your Own Vulnerable Driver",
      "detection_gap": "Most EDRs don't monitor driver loads",
      "detection_ideas": [
        "Monitor DriverLoaded events with Sysmon Event ID 6",
        "Check for known vulnerable driver hashes"
      ],
      "key_takeaway": "Enable driver signature enforcement and monitor driver loads"
    }
  }
]
```

Save this exact format to `analysis_results.json`.

## Batching Tips

### Analyze Multiple Items at Once

Instead of one-by-one:

```
You: Here are 3 threat intelligence items to analyze:

ITEM 1:
Source: https://twitter.com/researcher/status/123
Content: [paste content]

ITEM 2:
Source: https://blog.example.com/article
Content: [paste content]

ITEM 3:
Source: https://another-site.com/intel
Content: [paste content]

Please analyze all 3 and return JSON array.
```

### Combine Multiple Batches

If you analyzed in separate batches:

```bash
# Combine batch files
jq -s 'add' batch1.json batch2.json batch3.json > analysis_results.json

# Or manually merge into a single JSON array
```

## Automation

Automate the fetching:

```bash
# Add to crontab (Linux/Mac)
crontab -e

# Fetch daily at 9 AM
0 9 * * * cd /path/to/Daily_News && python fetch_content.py
```

Then analyze with Claude Code when you're ready (takes just 5-10 minutes).

## Content Types I Can Analyze

When analyzing, I'll classify content as:

1. **ioc_based** - Malware campaigns with indicators (hashes, IPs, domains)
2. **technique_research** - Attack technique analysis and detection methods
3. **tool_analysis** - Security tool reviews (offensive/defensive)
4. **threat_actor_profile** - APT groups and their TTPs
5. **vulnerability_analysis** - CVE analysis and exploitation
6. **detection_engineering** - Detection rules and queries

For each type, I extract the most actionable intelligence.

## Troubleshooting

### "No files found"
Run `python fetch_content.py` first to fetch content.

### "Error generating report"
Check that your `analysis_results.json` is a valid JSON array (starts with `[`, ends with `]`).

### Twitter session expired
Run `python setup_twitter.py` to re-authenticate.

## Need Help?

Just ask me (Claude Code) during the analysis phase:

- "What content type should this be?"
- "Help me analyze this batch"
- "Is this JSON format correct?"

I'm here to help!
