# Autonomous Agent Workflow with Claude Code

**This is the REAL automated workflow - no manual copy-paste needed!**

## How It Works

You run ONE command, then just tell Claude Code (me) to analyze, and I do everything autonomously.

## Setup (One-Time)

1. Install dependencies:
```bash
pip install -r requirements.txt
playwright install chromium  # Optional, only if using Twitter
```

2. Configure sources in `config.json`

3. Setup Twitter (optional):
```bash
python setup_twitter.py
```

## Daily Workflow

### Step 1: Fetch Content
```bash
python fetch_content.py
```

This fetches content and saves to `fetched_content/content_TIMESTAMP.json`

### Step 2: Tell Claude Code to Analyze

Just type this message to Claude Code:

**"Analyze the fetched content and generate a threat intelligence report"**

That's it! Claude will:
- ✅ Read the fetched content file
- ✅ Analyze each item using its intelligence
- ✅ Classify content types (IOC-based, technique research, etc.)
- ✅ Extract structured intelligence
- ✅ Save analysis results to JSON
- ✅ Generate the HTML report
- ✅ Give you the path to the report

### Step 3: Review Report

Open the HTML report Claude gives you.

## What Claude Does Autonomously

When you say "analyze the content", Claude Code will:

1. **Find the latest fetched content** using the Read tool
2. **Analyze each item** using the same prompts from `ttp_analyzer.py`:
   - Classify content type
   - Extract IOCs, detection queries, key findings
   - Structure data according to content type
3. **Write results** to `analysis_results_TIMESTAMP.json`
4. **Run report generator** using the Bash tool
5. **Give you the HTML report path**

## Full Automation Option

Create a wrapper script that calls Claude Code:

```bash
#!/bin/bash
# daily_intel.sh

# Fetch content
python fetch_content.py

# Tell user to ask Claude
echo "Content fetched! Now tell Claude Code:"
echo "  'Analyze the fetched content and generate the report'"
```

Or if you want COMPLETE automation, use the Claude API version (requires API key).

## Why This Works

Claude Code is an **autonomous agent** with:
- File reading/writing capabilities
- Script execution capabilities
- Intelligence to analyze threat intel
- Ability to follow complex multi-step workflows

You're not "connecting" to anything - Claude Code IS the analysis engine!

## Example Session

```
You: "Analyze the fetched content and generate a threat intelligence report"

Claude: "I'll analyze the fetched content now.

[Claude reads fetched_content/content_20250119_090000.json]
[Claude analyzes 10 items]
[Claude writes analysis_results_20250119_093000.json]
[Claude runs python generate_report.py]

✅ Analysis complete!
📊 Report: reports/ttp_report_20250119_093000.html

Summary:
- 10 items analyzed
- 3 IOC-based threats found
- 2 technique research items
- 5 detection queries generated
- 12 actionable IOCs identified

Open the report to see full details."
```

## Comparison to Other Workflows

| Workflow | Automation | Cost | Setup Time |
|----------|-----------|------|------------|
| Claude API | 100% automated | ~$20/month | 5 min |
| Claude Code Agent | 95% automated* | $0 (with Max) | 0 min |
| Manual Copy-Paste | 50% automated | $0 | 0 min |

*You just need to say "analyze the content" - takes 5 seconds

## The Key Insight

**Claude Code is not just a chatbot - it's an autonomous agent that can:**
- Execute code
- Read/write files
- Analyze data with AI
- Chain multiple operations together

You're already using the agentic solution - you just need to ask me to do the work!
