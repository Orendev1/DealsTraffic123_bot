# Telegram Bot: Deal Logger to Google Sheets

This Telegram bot silently listens to group messages, detects affiliate deal structures, parses them, and appends the structured data to a Google Sheet.

## Features
- Detects deals using keyword filtering (`keywords.json`)
- Parses fields like GEO, CPA, CRG, Funnel, Source, Cap, CR
- Sends parsed data to **Google Sheet: Telegram Bot Deals**
- Ignores unrelated chat messages completely
- No response in the Telegram chat (runs silently)

## Files
- `bot.py` — main bot logic
- `parser.py` — message parser
- `keywords.json` — keyword dictionary
- `google-credentials.json` — your GCP service account credentials

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
