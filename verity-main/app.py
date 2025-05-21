import os
import logging
import re
from flask import Flask, render_template, request, jsonify
from flask_caching import Cache
import news_analyzer
import requests

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev_secret_key")

# Custom Jinja2 filters
@app.template_filter('regex_replace')
def regex_replace(s, pattern, replacement, flags=0):
    """Replace pattern in string with regex"""
    if isinstance(flags, str):
        if 'i' in flags:
            flags = re.IGNORECASE
    return re.sub(pattern, replacement, s, flags=flags)

@app.template_filter('format_datetime')
def format_datetime(value):
    """Format a datetime string to a readable date"""
    if not value:
        return 'Unknown date'
    
    # This is a simple implementation. For more complex formatting,
    # consider using datetime module to parse and format the date
    parts = value.split('T')
    if len(parts) > 0:
        date_part = parts[0]
        date_elements = date_part.split('-')
        if len(date_elements) == 3:
            year, month, day = date_elements
            return f"{month}/{day}/{year}"
    
    return value

# Configure caching
cache_config = {
    "DEBUG": True,
    "CACHE_TYPE": "SimpleCache",
    "CACHE_DEFAULT_TIMEOUT": 300  # Cache news for 5 minutes
}
app.config.from_mapping(cache_config)
cache = Cache(app)

# Get News API key from environment variables
NEWS_API_KEY = os.environ.get("NEWS_API_KEY", "")
if not NEWS_API_KEY:
    logger.warning("NEWS_API_KEY not found in environment variables!")

@app.route("/")
def index():
    """Render the main page with news headlines"""
    page = request.args.get('page', 1, type=int)
    try:
        news_data = get_news_data(page)
        return render_template("index.html", news_data=news_data, current_page=page, news_analyzer=news_analyzer)
    except Exception as e:
        logger.error(f"Error fetching news: {str(e)}")
        return render_template("error.html", error=str(e))

@app.route("/load_more")
def load_more():
    """API endpoint to load more news for pagination"""
    page = request.args.get('page', 1, type=int)
    try:
        news_data = get_news_data(page)
        return jsonify(news_data)
    except Exception as e:
        logger.error(f"Error fetching additional news: {str(e)}")
        return jsonify({"error": str(e)}), 500

@cache.memoize(timeout=300)
def get_news_data(page=1):
    """Fetch and analyze news headlines with caching"""
    logger.debug(f"Fetching news for page {page}")
    
    # Articles per page
    page_size = 10
    
    # Call News API
    url = "https://newsapi.org/v2/top-headlines"
    params = {
        "country": "us",
        "apiKey": NEWS_API_KEY,
        "page": page,
        "pageSize": page_size
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()  # Raise exception for HTTP errors
        
        data = response.json()
        
        if data.get("status") != "ok":
            raise Exception(f"News API error: {data.get('message', 'Unknown error')}")
        
        articles = data.get("articles", [])
        total_results = data.get("totalResults", 0)
        
        # Add bias analysis to each article
        analyzed_articles = []
        for article in articles:
            headline = article.get("title", "")
            if headline:
                bias_info = news_analyzer.analyze_headline(headline)
                article.update(bias_info)
                analyzed_articles.append(article)
        
        return {
            "articles": analyzed_articles,
            "totalResults": total_results,
            "hasMore": total_results > page * page_size
        }
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Request error: {str(e)}")
        raise Exception(f"Failed to fetch news data: {str(e)}")
    except Exception as e:
        logger.error(f"General error: {str(e)}")
        raise Exception(f"An error occurred while processing news data: {str(e)}")

@app.errorhandler(404)
def page_not_found(e):
    """Handle 404 errors"""
    return render_template("error.html", error="Page not found"), 404

@app.errorhandler(500)
def server_error(e):
    """Handle 500 errors"""
    return render_template("error.html", error="Internal server error"), 500