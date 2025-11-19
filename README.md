# TTP Monitoring System

Automated daily threat intelligence monitoring system for security researchers. Fetches content from Twitter and security blogs, analyzes with Claude API, and generates actionable TTP (Tactics, Techniques, and Procedures) reports.

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

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
playwright install chromium
```

### 2. Configure API Key

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

### 3. Configure Sources

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

### 4. Setup Twitter Authentication (One-Time)

Run the setup script to log into Twitter:

```bash
python setup_twitter.py
```

This will:
1. Open a browser window
2. Let you log into Twitter
3. Save your authenticated session for future use

**Note**: You only need to do this once. The session is reused for subsequent runs.

## Usage

### Run the Monitoring System

```bash
python main.py
```

This will:
1. Fetch content from configured Twitter accounts and article URLs
2. Analyze each item with Claude API
3. Generate an HTML report in the `reports/` directory

### Output

- **HTML Report**: `reports/ttp_report_YYYYMMDD_HHMMSS.html` - Open in your browser
- **JSON Data**: `reports/ttp_data_YYYYMMDD_HHMMSS.json` - Raw analyzed data

### Schedule Daily Runs

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

## What Gets Analyzed

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

1. **Morning**: System runs automatically (via cron/task scheduler)
2. **You arrive**: Open the HTML report
3. **Review**: Scan executive summary for high-priority items
4. **Act**:
   - Copy detection queries into your SIEM
   - Block IOCs in your environment
   - Update detection rules based on new techniques
   - Hunt for indicators in your logs
5. **Click source links**: Read full articles for items that interest you

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
- Your API key is in `.env` - **do not commit this file**
- Add `.env` and `twitter_session.json` to `.gitignore`

## License

MIT License - Use freely for security research and threat hunting.
