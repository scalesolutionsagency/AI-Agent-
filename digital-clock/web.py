#!/usr/bin/env python3
"""Flask web interface for digital clock."""

from flask import Flask, render_template, jsonify
from flask_cors import CORS
import yaml
from pathlib import Path
from datetime import datetime
import pytz

from clock.time_manager import TimeManager
from clock.formatter import TimeFormatter


app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False
CORS(app)

# Load configuration
def load_config():
    """Load configuration from YAML file."""
    config_file = Path("config.yaml")
    if config_file.exists():
        with open(config_file, 'r') as f:
            return yaml.safe_load(f) or {}
    return {}


config = load_config()
time_manager = TimeManager()
formatter = TimeFormatter()


@app.route('/')
def index():
    """Serve main page."""
    return render_template('index.html')


@app.route('/api/time')
def get_time():
    """Get current time in all configured zones."""
    zones = config.get('time_zones', [
        'UTC',
        'US/Eastern',
        'US/Pacific',
        'Europe/London',
        'Europe/Paris',
        'Asia/Tokyo',
        'Asia/Shanghai',
        'Australia/Sydney'
    ])
    
    times = time_manager.get_time_in_zones(zones)
    
    # Format for JSON response
    result = {
        'timestamp': datetime.utcnow().isoformat(),
        'clocks': []
    }
    
    for time_data in times:
        if 'error' not in time_data:
            result['clocks'].append({
                'timezone': time_data['timezone'],
                'time': formatter.format_time(
                    time_data['hour'],
                    time_data['minute'],
                    time_data['second']
                ),
                'time_12h': formatter.format_time(
                    time_data['hour'],
                    time_data['minute'],
                    time_data['second'],
                    format_24=False
                ),
                'date': time_data['date'],
                'day': time_data['day_of_week'],
                'hour': time_data['hour'],
                'minute': time_data['minute'],
                'second': time_data['second'],
                'utc_offset': time_data['utc_offset'],
                'is_dst': time_data['is_dst']
            })
    
    return jsonify(result)


@app.route('/api/zones')
def get_zones():
    """Get list of available time zones."""
    zones = time_manager.get_available_zones()
    return jsonify({
        'zones': zones,
        'total': len(zones)
    })


@app.route('/api/time/<timezone>')
def get_time_zone(timezone):
    """Get time in a specific timezone."""
    if not time_manager.validate_timezone(timezone):
        return jsonify({'error': f'Invalid timezone: {timezone}'}), 400
    
    times = time_manager.get_time_in_zones([timezone])
    if times and 'error' not in times[0]:
        time_data = times[0]
        return jsonify({
            'timezone': time_data['timezone'],
            'time': formatter.format_time(
                time_data['hour'],
                time_data['minute'],
                time_data['second']
            ),
            'date': time_data['date'],
            'day': time_data['day_of_week'],
            'utc_offset': time_data['utc_offset'],
            'is_dst': time_data['is_dst']
        })
    
    return jsonify({'error': 'Failed to get time'}), 500


@app.route('/api/config')
def get_config():
    """Get display configuration."""
    display_config = config.get('display', {})
    return jsonify({
        'format': display_config.get('format', 24),
        'theme': display_config.get('theme', 'light'),
        'update_interval': display_config.get('update_interval', 1),
        'show_seconds': display_config.get('show_seconds', True),
        'show_date': display_config.get('show_date', True),
        'show_timezone_name': display_config.get('show_timezone_name', True)
    })


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({'error': 'Not found'}), 404


@app.errorhandler(500)
def server_error(error):
    """Handle 500 errors."""
    return jsonify({'error': 'Server error'}), 500


if __name__ == '__main__':
    web_config = config.get('web', {})
    app.run(
        host=web_config.get('host', '0.0.0.0'),
        port=web_config.get('port', 5000),
        debug=web_config.get('debug', False),
        threaded=web_config.get('threaded', True)
    )
