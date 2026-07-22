import os
from flask import Flask, render_template, jsonify, request
from datetime import datetime
import asyncio
from main import LeadScraperAgent
from utils.config_loader import ConfigLoader

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

# Set environment variables
os.environ['GOOGLE_PLACES_API_KEY'] = 'AIzaSyAjH-2U6p6LumY-mqzrvuTsD91iz7OA0yQ'
os.environ['LEAD_SOURCE'] = 'google_places'

# Global state
scraper_state = {
    'running': False,
    'status': 'idle',
    'leads_found': 0,
    'leads': [],
    'last_run': None,
    'errors': []
}

@app.route('/')
def index():
    """Serve main dashboard."""
    return render_template('dashboard.html')

@app.route('/api/status')
def get_status():
    """Get current scraper status."""
    return jsonify({
        'running': scraper_state['running'],
        'status': scraper_state['status'],
        'leads_found': scraper_state['leads_found'],
        'last_run': scraper_state['last_run'],
        'errors': scraper_state['errors'][-5:]  # Last 5 errors
    })

@app.route('/api/leads')
def get_leads():
    """Get scraped leads."""
    limit = request.args.get('limit', 50, type=int)
    return jsonify({
        'leads': scraper_state['leads'][:limit],
        'total': len(scraper_state['leads'])
    })

@app.route('/api/scrape', methods=['POST'])
def start_scrape():
    """Start a new scrape job."""
    if scraper_state['running']:
        return jsonify({'error': 'Scraper already running'}), 400
    
    data = request.json
    business_type = data.get('business_type', 'Plumbers')
    location = data.get('location', 'Austin, TX')
    limit = data.get('limit', 100)
    
    scraper_state['running'] = True
    scraper_state['status'] = f'Searching for {business_type} in {location}...'
    scraper_state['leads'] = []
    scraper_state['leads_found'] = 0
    scraper_state['errors'] = []
    
    try:
        # Create config
        config = {
            'lead_source': {
                'provider': 'google_places',
                'google_places': {
                    'radius': 50000
                }
            },
            'search_queries': [{
                'business_type': business_type,
                'location': location,
                'limit': limit
            }],
            'logging': {
                'level': 'INFO',
                'file_path': './logs'
            },
            'data_cleaning': {
                'trim_whitespace': True,
                'normalize_phone': True,
                'validate_email': True,
                'remove_empty_fields': True
            },
            'deduplication': {
                'enabled': True,
                'check_fields': ['phone_number', 'email', 'website'],
                'history_file': './data/leads_history.json',
                'keep_history': True
            },
            'output': {
                'format': 'json',
                'output_dir': './output'
            },
            'error_handling': {
                'continue_on_error': True
            }
        }
        
        # Run scraper
        agent = LeadScraperAgent()
        agent.config = config
        agent.initialize_lead_source()
        
        # Execute async scrape
        leads = asyncio.run(agent.scrape_leads())
        processed_leads = agent.process_leads(leads)
        
        scraper_state['leads'] = processed_leads
        scraper_state['leads_found'] = len(processed_leads)
        scraper_state['status'] = 'Scrape completed successfully'
        scraper_state['last_run'] = datetime.now().isoformat()
        
        return jsonify({
            'success': True,
            'leads_found': len(processed_leads),
            'leads': processed_leads
        })
    
    except Exception as e:
        error_msg = str(e)
        scraper_state['errors'].append(error_msg)
        scraper_state['status'] = f'Error: {error_msg}'
        return jsonify({'error': error_msg}), 500
    
    finally:
        scraper_state['running'] = False

@app.route('/api/download')
def download_leads():
    """Download leads as JSON."""
    import json
    response = app.response_class(
        response=json.dumps(scraper_state['leads'], indent=2),
        status=200,
        mimetype='application/json'
    )
    response.headers['Content-Disposition'] = 'attachment; filename=leads.json'
    return response

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def server_error(error):
    return jsonify({'error': 'Server error'}), 500

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
