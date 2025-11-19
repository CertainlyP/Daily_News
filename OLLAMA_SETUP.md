# TTP Monitoring with Ollama (FREE, No API)

Simple daily threat intelligence monitoring with **zero cost** using local LLM.

## Quick Setup (5 Minutes)

### 1. Install Ollama

**Linux:**
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

**Mac:**
```bash
brew install ollama
```

**Windows:**
Download from https://ollama.com/download

### 2. Pull AI Model

```bash
ollama pull llama3.1
```

**Other models** (optional):
- `ollama pull gemma2:9b` - Google's Gemma 2 (better structured output)
- `ollama pull qwen2.5:14b` - Qwen 2.5 (excellent at analysis, needs 16GB RAM)
- `ollama pull mixtral` - Mixtral 8x7B (highest quality, slower)

### 3. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 4. Twitter Setup (One-Time)

Twitter requires manual login once:

```bash
python setup_twitter.py
```

This opens a browser. Log into Twitter, then close. Session is saved.

### 5. Configure Sources

Edit `config.json`:

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

## Run Daily Report

**One command:**

```bash
python main_ollama.py
```

That's it! This will:
1. ✅ Fetch from Twitter (your accounts)
2. ✅ Fetch from security blogs
3. ✅ Analyze with local Ollama LLM (FREE)
4. ✅ Generate HTML report in `reports/`

## Output

You get:
- `reports/ttp_report_TIMESTAMP.html` - Visual threat intelligence report
- `reports/ttp_data_TIMESTAMP.json` - Raw structured data

Open the HTML file in your browser.

## Automate Daily

**Add to cron** (Linux/Mac):

```bash
# Run every day at 9 AM
0 9 * * * cd /path/to/Daily_News && python main_ollama.py
```

**Or use systemd timer, Windows Task Scheduler, etc.**

## Model Selection

Change model by setting environment variable:

```bash
export OLLAMA_MODEL=gemma2:9b
python main_ollama.py
```

## Troubleshooting

**"Cannot connect to Ollama"**
```bash
ollama serve  # Start Ollama server
```

**"Model not found"**
```bash
ollama list  # Check installed models
ollama pull llama3.1  # Install model
```

**Twitter login issues**
- Try again with `python setup_twitter.py`
- Check `twitter_session.json` exists after login

## Cost

- ✅ **$0/month** - Completely free
- Ollama runs locally
- No API calls
- No subscriptions

## Requirements

- **RAM**: 8GB minimum (16GB for larger models)
- **Disk**: ~5GB for model
- **CPU**: Any modern CPU works (GPU optional but faster)

## Compare to Claude API

| Feature | Ollama (This) | Claude API |
|---------|---------------|------------|
| Cost | $0 | ~$20/month |
| Speed | Depends on hardware | Fast |
| Quality | Very good | Excellent |
| Privacy | 100% local | Cloud API |
| Setup | 5 minutes | 2 minutes |

Both versions work the same way - just different AI backends.
