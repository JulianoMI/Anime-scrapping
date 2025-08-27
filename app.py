from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
from scraper_core import AnimeScraper
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Initialize the pure Python scraper
scraper = AnimeScraper()

# Add some Flask-specific helper functions
def handle_api_error(func):
    """Decorator to handle API errors gracefully"""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"API Error in {func.__name__}: {e}")
            return jsonify({"error": f"An error occurred: {str(e)}"}), 500
    wrapper.__name__ = func.__name__
    return wrapper

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/home')
@handle_api_error
def api_home():
    """API endpoint for home page data using pure Python scraper"""
    logger.info("API: Fetching home page data")
    data = scraper.scrape_home_page()
    logger.info(f"API: Returning home data with {sum(len(v) for v in data.values())} total items")
    return jsonify(data)

@app.route('/api/anime-list')
@handle_api_error
def api_anime_list():
    """API endpoint for anime list using pure Python scraper"""
    letter = request.args.get('letter')
    logger.info(f"API: Fetching anime list (letter: {letter or 'all'})")
    data = scraper.scrape_anime_list(letter)
    logger.info(f"API: Returning {len(data)} anime entries")
    return jsonify(data)

@app.route('/api/anime-details')
@handle_api_error
def api_anime_details():
    """API endpoint for anime details using pure Python scraper"""
    url = request.args.get('url')
    if not url:
        return jsonify({"error": "URL parameter required"}), 400
    
    logger.info(f"API: Fetching anime details for: {url}")
    data = scraper.scrape_anime_details(url)
    if data:
        logger.info(f"API: Successfully fetched details for: {data['title']}")
        return jsonify(data)
    else:
        logger.warning(f"API: Failed to fetch anime details for: {url}")
        return jsonify({"error": "Failed to fetch anime details"}), 404

@app.route('/api/search')
@handle_api_error
def api_search():
    """API endpoint for searching anime using pure Python scraper"""
    query = request.args.get('q', '')
    if not query:
        return jsonify({"error": "Query parameter 'q' required"}), 400
    
    logger.info(f"API: Searching for: {query}")
    results = scraper.search_anime(query)
    logger.info(f"API: Found {len(results)} search results")
    return jsonify(results)

@app.route('/api/statistics')
@handle_api_error
def api_statistics():
    """API endpoint for scraping statistics"""
    logger.info("API: Fetching statistics")
    stats = scraper.get_statistics()
    return jsonify(stats)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
