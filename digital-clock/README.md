# Digital Clock - Multi-Timezone Display

A Python application that displays the current time in multiple time zones with both CLI and web interfaces.

## Features

- 🕐 Real-time digital clock display
- 🌍 Support for multiple time zones
- 💻 CLI interface with live updates
- 🌐 Web interface with modern UI
- 📱 Responsive design
- ⚙️ Customizable time zones
- 🎨 Multiple display themes
- 🔄 Auto-refresh every second

## Quick Start

### Prerequisites
- Python 3.9+
- pip

### Installation

```bash
cd digital-clock
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### CLI Usage

```bash
# Display default time zones
python cli.py

# Display custom time zones
python cli.py --zones "US/Eastern" "US/Pacific" "Europe/London" "Asia/Tokyo"

# Display with 12-hour format
python cli.py --format 12

# Display with different theme
python cli.py --theme dark
```

### Web Interface

```bash
# Start web server
python web.py

# Open browser to http://localhost:5000
```

## Configuration

Edit `config.yaml` to customize:
- Default time zones
- Update frequency
- Display format (12/24 hour)
- UI theme

## Project Structure

```
digital-clock/
├── cli.py                 # CLI interface
├── web.py                 # Flask web app
├── config.yaml            # Configuration
├── requirements.txt       # Dependencies
├── clock/
│   ├── __init__.py
│   ├── time_manager.py   # Time zone handling
│   └── formatter.py      # Time formatting
└── static/
    ├── css/
    │   └── style.css     # Styling
    └── js/
        └── clock.js      # Live updates
```

## Deployment

### Docker

```bash
docker build -t digital-clock .
docker run -p 5000:5000 digital-clock
```

### Railway/Render

See DEPLOYMENT.md for cloud deployment instructions.
