# Lead Scraper Agent

An automated Python agent that scrapes business leads based on search queries (business type + location), deduplicates results, and pushes cleaned data to Google Sheets.

## Features

- 🔍 Search leads by business type and location
- 📊 Multiple data source support (Apify/Apollo.io/Google Places API)
- ✨ Automatic data cleaning and formatting
- 🗑️ Deduplication against running lead list
- 📈 Auto-push to Google Sheets or Notion
- ⏰ Scheduled daily execution via cron/scheduler
- 🛡️ Error handling & rate-limit protection
- 🔐 Environment-based configuration (no hardcoded secrets)
- 🔄 Modular architecture for easy lead source swapping

## Quick Start

### Prerequisites

- Python 3.9+
- pip or poetry
- API keys for: Google Sheets API, Apify/Apollo.io/Google Places, and optionally Notion

### Installation

1. Clone the repository:
```bash
git clone https://github.com/scalesolutionsagency/AI-Agent-.git
cd AI-Agent-
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your API keys
```

5. Configure search parameters:
```bash
cp config.example.yaml config.yaml
# Edit config.yaml with your search queries
```

### Configuration

Edit `config.yaml` to customize:
- Search queries (business type + location)
- Lead source (Apify, Apollo.io, or Google Places)
- Output format (CSV/JSON)
- Destination (Google Sheets, Notion, or local file)
- Schedule frequency

### Running Manually

```bash
python main.py
```

### Scheduling (Linux/Mac)

Add to crontab for daily 9 AM execution:
```bash
0 9 * * * cd /path/to/AI-Agent- && /path/to/venv/bin/python main.py >> logs/scraper.log 2>&1
```

### Deployment

#### Railway

1. Push to GitHub
2. Connect repository at railway.app
3. Add environment variables in Railway dashboard
4. Deploy and enable scheduled jobs

#### Render

1. Create new service at render.com
2. Connect GitHub repository
3. Set environment variables
4. Configure cron job in Render dashboard

## Project Structure

```
.
├── main.py                 # Entry point
├── config.yaml            # Search & output configuration
├── .env.example           # Environment variables template
├── requirements.txt       # Python dependencies
├── leads/                 # Lead source modules
│   ├── __init__.py
│   ├── base.py           # Abstract base class
│   ├── apify_source.py   # Apify implementation
│   ├── apollo_source.py  # Apollo.io implementation
│   └── google_places.py  # Google Places implementation
├── deduplication/         # Deduplication logic
│   ├── __init__.py
│   └── deduplicator.py   # Lead deduplication
├── outputs/              # Output handlers
│   ├── __init__.py
│   ├── base.py
│   ├── csv_output.py
│   ├── json_output.py
│   ├── google_sheets.py  # Google Sheets API
│   └── notion_output.py  # Notion API
├── utils/                # Utility functions
│   ├── __init__.py
│   ├── logger.py         # Logging setup
│   ├── data_cleaner.py   # Data normalization
│   └── config_loader.py  # Config parser
└── logs/                 # Log files
```

## API Keys Setup

### Google Sheets

1. Create Google Cloud project
2. Enable Google Sheets API
3. Create service account and download JSON key
4. Set `GOOGLE_SHEETS_CREDENTIALS_PATH` in `.env`

### Apify

1. Get API token from apify.com
2. Set `APIFY_API_TOKEN` in `.env`

### Apollo.io

1. Get API key from apollo.io
2. Set `APOLLO_API_KEY` in `.env`

### Google Places API

1. Enable Google Places API in Cloud Console
2. Create API key
3. Set `GOOGLE_PLACES_API_KEY` in `.env`

### Notion (Optional)

1. Create Notion database
2. Get integration token
3. Set `NOTION_API_TOKEN` and `NOTION_DATABASE_ID` in `.env`

## Error Handling

- Rate limit retries with exponential backoff
- Graceful failure logging to `logs/scraper.log`
- Partial results saved if API fails mid-run
- Email alerts on critical failures (optional)

## Contributing

To add a new lead source:

1. Create new file in `leads/`
2. Inherit from `leads/base.py`
3. Implement `search()` method
4. Update `config.yaml` with source option

## License

MIT
