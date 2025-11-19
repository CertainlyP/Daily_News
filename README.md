# Daily_News - TTP Monitoring System

Autonomous threat intelligence monitoring using Google Gemini API.

Monitor Twitter accounts and security blogs daily, get AI-analyzed threat intelligence reports.

## Quick Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Get Gemini API Key

1. Go to https://aistudio.google.com/app/apikey
2. Create API key
3. Copy it

### 3. Configure

**Create `.env` file:**
```bash
GEMINI_API_KEY=your_api_key_here
```

**Edit `config.json`:**
```json
{
  "sources": {
    "twitter_accounts": [
      "vxunderground",
      "TheDFIRReport",
      "malwrhunterteam"
    ],
    "article_urls": [
      "https://www.bleepingcomputer.com/news/security/",
      "https://thehackernews.com/"
    ]
  }
}
```

### 4. Twitter Setup (One-Time)

```bash
python setup_twitter.py
```

Browser opens → Log into Twitter → Close browser. Session saved.

### 5. Run

```bash
python main.py
```

Done. Report generated in `reports/ttp_report_TIMESTAMP.html`

## Daily Usage

```bash
python main.py
```

Opens HTML report in browser. That's it.

## Automate

**Linux/Mac (cron):**
```bash
0 9 * * * cd /path/to/Daily_News && python main.py
```

**Windows (Task Scheduler):**
- Action: `python`
- Arguments: `main.py`
- Start in: `C:\path\to\Daily_News`

## Cost

Gemini API is free up to 1500 requests/day. This uses ~5-20 requests per run.

**Free.**

## What You Get

- IOCs (IPs, domains, hashes, files)
- Attack techniques and TTPs
- Detection queries (KQL, EDR logic)
- Vulnerability analysis
- Threat actor profiles
- HTML report with dark mode

## Files

- `main.py` - Main script
- `gemini_analyzer.py` - AI analysis engine
- `fetcher.py` - Content fetcher (Twitter + blogs)
- `report_generator.py` - HTML report generator
- `setup_twitter.py` - Twitter login helper
- `config.json` - Your sources

## Troubleshooting

**"GEMINI_API_KEY not set"**
```bash
echo "GEMINI_API_KEY=your_key" > .env
```

**Twitter login fails**
```bash
python setup_twitter.py
# Try again, log in manually
```

**No content fetched**
- Check `config.json` has valid sources
- Check Twitter session: `python setup_twitter.py`

## Requirements

- Python 3.8+
- Google Gemini API key (free)
- Internet connection

That's it.
