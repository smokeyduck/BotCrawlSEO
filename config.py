"""
Configuration settings for SEO Analysis Tool
"""

# Web Scraping Settings
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
REQUEST_TIMEOUT = 30
MAX_RETRIES = 3
RATE_LIMIT_DELAY = 1.0  # seconds between requests

# Analysis Settings
MIN_KEYWORD_LENGTH = 3
MAX_KEYWORD_LENGTH = 50
MIN_KEYWORD_FREQUENCY = 2
TOP_KEYWORDS_COUNT = 50
SECONDARY_KEYWORDS_COUNT = 30

# Content Analysis
IGNORE_WORDS = {
    'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 
    'by', 'from', 'up', 'about', 'into', 'through', 'during', 'before', 
    'after', 'above', 'below', 'between', 'among', 'this', 'that', 'these', 
    'those', 'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 
    'you', 'your', 'yours', 'yourself', 'yourselves', 'he', 'him', 'his', 
    'himself', 'she', 'her', 'hers', 'herself', 'it', 'its', 'itself', 
    'they', 'them', 'their', 'theirs', 'themselves', 'what', 'which', 
    'who', 'whom', 'whose', 'this', 'that', 'these', 'those', 'am', 'is', 
    'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 
    'having', 'do', 'does', 'did', 'doing', 'will', 'would', 'could', 
    'should', 'may', 'might', 'must', 'can', 'shall'
}

# File Output Settings
OUTPUT_DIR = "seo_reports"
REPORT_FILENAME_TEMPLATE = "seo_analysis_{domain}_{timestamp}.txt"

# Selenium Settings (for JavaScript-heavy sites)
SELENIUM_TIMEOUT = 10
HEADLESS_BROWSER = True

# Logging
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
