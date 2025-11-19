# TTP Monitoring System

Automated daily threat intelligence monitoring system for security researchers. Fetches content from Twitter and security blogs, analyzes with Claude, and generates actionable TTP (Tactics, Techniques, and Procedures) reports.

## Two Workflow Options

### Option A: Hybrid Workflow with Claude Code (No API Required)
Perfect if you have **Claude Max** but no API access. Uses Claude Code for analysis.

### Option B: Fully Automated with Claude API
Requires Anthropic API key but fully automated.

---

## Features

- **Multi-Source Fetching**: Twitter (authenticated) and web articles
- **Intelligent Analysis**: Claude API automatically classifies and extracts relevant intelligence
- **Adaptive Extraction**: Different extraction strategies based on content type:
  - IOC-based threats (hashes, IPs, domains, technical details)
  - Attack technique research (detection gaps, detection ideas)
  - Security tool analysis (detection methods, use cases)
  - Threat actor profiles (targeting, TTP changes)
  - Vulnerability analysis (exploit info, mitigation)
  - Detection engineering (queries, rules)
- **Professional Reports**: Clean, dark-mode HTML reports with source links
- **Focused on Action**: Extracts "the sauce" - technical details that matter, not basic descriptions

---

## Option A: Hybrid Workflow (Claude Code - No API Required)

This workflow is perfect if you have Claude Max subscription but no API access. You'll use Claude Code to perform the analysis interactively.

### Setup

#### 1. Install Dependencies

```bash
pip install -r requirements.txt
playwright install chromium
```

#### 2. Configure Sources

Edit `config.json` to add your Twitter accounts and article URLs (see Configuration section below).

#### 3. Setup Twitter (One-Time, Optional)

If you want to monitor Twitter:

```bash
python setup_twitter.py
```

This saves your Twitter session for future use.

### Daily Workflow

#### Step 1: Fetch Content

Run this daily (or whenever you want fresh intel):

```bash
python fetch_content.py
```

This fetches content from your configured sources and saves it to `fetched_content/content_TIMESTAMP.json`.

**Output:** Raw content saved, no analysis yet.

#### Step 2: Analyze with Claude Code

Open Claude Code (the CLI you're using right now) and run:

```bash
python analyze_with_claude.py fetched_content/content_TIMESTAMP.json
```

This script will:
1. Present content items in batches (default: 3 at a time)
2. Show you the appropriate analysis prompts
3. You copy content + prompts into Claude Code
4. Claude analyzes and returns structured JSON
5. You save the JSON responses

**Example interaction:**
```
User: [pastes content item 1-3 from script output]
Claude: [analyzes and returns JSON for each item]
User: [saves JSON to analysis_results.json]
User: [continues with next batch]
```

**Pro tip:** You can analyze multiple items at once. Just paste several items and ask me to analyze them all.

#### Step 3: Generate Report

Once you have all analysis results in a JSON file:

```bash
python generate_report.py analysis_results.json
```

This generates the beautiful HTML report in `reports/ttp_report_TIMESTAMP.html`.

### Expected Format for Analysis Results

Your `analysis_results.json` should be a JSON array like this:

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
        ...
      },
      ...
    }
  },
  {
    "source_url": "https://blog.example.com/article",
    "content_type": "technique_research",
    "data": {
      ...
    }
  }
]
```

### Tips for Efficient Analysis

1. **Batch processing**: Analyze 3-5 items at a time with Claude Code
2. **Save incrementally**: Save analysis results after each batch
3. **Combine JSON files**: Merge multiple batch results into one file
4. **Use jq**: `jq -s 'add' batch*.json > analysis_results.json` to combine

### Automation with Hybrid Workflow

You can automate Step 1 (fetching) with cron/scheduler:

```bash
# Crontab: Fetch content daily at 9 AM
0 9 * * * cd /path/to/Daily_News && python fetch_content.py
```

Then analyze with Claude Code when you're ready (takes 5-10 minutes).

---

## Option B: Fully Automated Workflow (Claude API Required)

For users with Anthropic API access. This is fully automated.

### Setup

#### 1. Install Dependencies

```bash
pip install -r requirements.txt
playwright install chromium
```

#### 2. Configure API Key

Create a `.env` file:

```bash
cp .env.example .env
# Edit .env and add your Anthropic API key
```

Or export directly:

```bash
export ANTHROPIC_API_KEY=sk-ant-your-key-here
```

Get your API key from: https://console.anthropic.com

#### 3. Configure Sources

Edit `config.json` to add your sources:

```json
{
  "sources": {
    "twitter_accounts": [
      "vxunderground",
      "JAMESWT_WT",
      "malwrhunterteam",
      "your_favorite_researchers"
    ],
    "article_urls": [
      "https://blog.example.com/threat-intel",
      "https://research.example.com/latest"
    ]
  },
  "settings": {
    "twitter_session_file": "twitter_session.json",
    "output_dir": "reports",
    "max_tweets_per_account": 10
  }
}
```

#### 4. Setup Twitter Authentication (One-Time)

Run the setup script to log into Twitter:

```bash
python setup_twitter.py
```

This will:
1. Open a browser window
2. Let you log into Twitter
3. Save your authenticated session for future use

**Note**: You only need to do this once. The session is reused for subsequent runs.

### Usage

#### Run the Monitoring System

```bash
python main.py
```

This will:
1. Fetch content from configured Twitter accounts and article URLs
2. Analyze each item with Claude API
3. Generate an HTML report in the `reports/` directory

#### Output

- **HTML Report**: `reports/ttp_report_YYYYMMDD_HHMMSS.html` - Open in your browser
- **JSON Data**: `reports/ttp_data_YYYYMMDD_HHMMSS.json` - Raw analyzed data

#### Schedule Daily Runs

**Linux/Mac** (using cron):

```bash
crontab -e
# Add this line to run daily at 9 AM:
0 9 * * * cd /path/to/ttp-monitor && /path/to/python main.py
```

**Windows** (using Task Scheduler):

1. Open Task Scheduler
2. Create Basic Task
3. Set trigger: Daily at 9:00 AM
4. Action: Start a program
5. Program: `C:\path\to\python.exe`
6. Arguments: `C:\path\to\main.py`
7. Start in: `C:\path\to\ttp-monitor`

---

## What Gets Analyzed

(Applies to both workflows)

The system intelligently categorizes and extracts:

### IOC-Based Threats
- File hashes, IPs, domains, URLs
- Execution flow and command lines
- Persistence mechanisms
- C2 protocols and encryption
- Detection queries (KQL for MDO/Defender/Sentinel)
- Key findings (what's new/interesting)

### Attack Technique Research
- Attack vector details
- Detection gaps (why tools miss it)
- Detection ideas (how to catch it)
- Affected products
- Mitigation strategies

### Security Tool Analysis
- Tool capabilities
- Detection methods (how to spot usage)
- Legitimate vs malicious use cases
- Relevant telemetry sources

### Threat Actor Profiles
- Targeting (industries, geos)
- TTP changes (what's new in their playbook)
- Infrastructure patterns
- What to monitor in your environment

### Vulnerability Analysis
- CVE details and severity
- Exploit availability and complexity
- Attack vectors
- Detection and mitigation

### Detection Engineering
- Detection logic (queries, rules)
- Data sources needed
- False positive potential
- Coverage analysis

## Example Workflow

### With Hybrid Workflow (Claude Code):
1. **Morning**: Run `python fetch_content.py` (or automated via cron)
2. **Analysis**: Run `python analyze_with_claude.py` and analyze with Claude Code (5-10 min)
3. **Report**: Run `python generate_report.py analysis_results.json`
4. **Review**: Open HTML report and scan for high-priority items
5. **Act**: Copy detection queries, block IOCs, update rules, hunt in logs

### With API Workflow:
1. **Morning**: System runs automatically via `python main.py` (scheduled)
2. **You arrive**: Open the HTML report
3. **Review**: Scan executive summary for high-priority items
4. **Act**: Copy detection queries, block IOCs, update rules, hunt in logs

## Troubleshooting

### Twitter Session Expired

If Twitter fetching fails:

```bash
python setup_twitter.py
```

Re-authenticate and save a new session.

### API Rate Limits

Claude API has rate limits. If you hit them:
- Reduce `max_tweets_per_account` in `config.json`
- Add delays between API calls
- Upgrade your Anthropic plan

### Missing Dependencies

```bash
pip install -r requirements.txt --upgrade
playwright install chromium
```

## Architecture

### Hybrid Workflow (Claude Code):
```
fetch_content.py
    └── fetcher.py → saves JSON
         ↓
analyze_with_claude.py → formats for Claude Code
         ↓
[Claude Code Analysis] → returns JSON
         ↓
generate_report.py
    └── report_generator.py → HTML Report
```

### API Workflow:
```
main.py (orchestrator)
    ├── fetcher.py
    │   ├── Twitter (Playwright + auth session)
    │   └── Articles (requests + BeautifulSoup)
    │
    ├── ttp_analyzer.py
    │   ├── Content Classifier (determines type)
    │   └── Adaptive Extractor (extracts based on type)
    │
    └── report_generator.py
        └── HTML Report (dark mode, organized by type)
```

## Security Notes

- Your Twitter session is stored locally in `twitter_session.json`
- Your API key (if using Option B) is in `.env` - **do not commit this file**
- Add `.env`, `twitter_session.json`, and `fetched_content/` to `.gitignore`
- The `fetched_content/` directory may contain sensitive threat intelligence

## License

MIT License - Use freely for security research and threat hunting.
