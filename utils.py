"""
Utility functions for SEO Analysis Tool
"""

import re
import logging
import validators
from urllib.parse import urljoin, urlparse
from datetime import datetime
import os
import config

def setup_logging():
    """Setup logging configuration"""
    logging.basicConfig(
        level=getattr(logging, config.LOG_LEVEL),
        format=config.LOG_FORMAT
    )
    return logging.getLogger(__name__)

def validate_url(url):
    """
    Validate if the provided URL is valid
    
    Args:
        url (str): URL to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    return validators.url(url)

def normalize_url(url):
    """
    Normalize URL by adding protocol if missing
    
    Args:
        url (str): URL to normalize
        
    Returns:
        str: Normalized URL
    """
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    return url

def get_domain_from_url(url):
    """
    Extract domain from URL
    
    Args:
        url (str): URL to extract domain from
        
    Returns:
        str: Domain name
    """
    parsed = urlparse(url)
    return parsed.netloc.replace('www.', '')

def clean_text(text):
    """
    Clean text by removing extra whitespace and special characters
    
    Args:
        text (str): Text to clean
        
    Returns:
        str: Cleaned text
    """
    if not text:
        return ""
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    # Remove special characters but keep alphanumeric and basic punctuation
    text = re.sub(r'[^\w\s\-.,!?;:]', '', text)
    return text.strip()

def is_internal_link(link_url, base_domain):
    """
    Check if a link is internal (same domain)
    
    Args:
        link_url (str): URL to check
        base_domain (str): Base domain to compare against
        
    Returns:
        bool: True if internal, False if external
    """
    if not link_url:
        return False
    
    # Handle relative URLs
    if link_url.startswith('/'):
        return True
    
    # Handle absolute URLs
    link_domain = get_domain_from_url(link_url)
    return link_domain == base_domain

def create_output_directory():
    """Create output directory if it doesn't exist"""
    if not os.path.exists(config.OUTPUT_DIR):
        os.makedirs(config.OUTPUT_DIR)

def generate_report_filename(domain):
    """
    Generate report filename with timestamp
    
    Args:
        domain (str): Domain name
        
    Returns:
        str: Generated filename
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_domain = re.sub(r'[^\w\-.]', '_', domain)
    return config.REPORT_FILENAME_TEMPLATE.format(
        domain=safe_domain,
        timestamp=timestamp
    )

def extract_keywords_from_text(text, min_length=None, max_length=None):
    """
    Extract potential keywords from text
    
    Args:
        text (str): Text to extract keywords from
        min_length (int): Minimum keyword length
        max_length (int): Maximum keyword length
        
    Returns:
        list: List of potential keywords
    """
    if not text:
        return []
    
    min_length = min_length or config.MIN_KEYWORD_LENGTH
    max_length = max_length or config.MAX_KEYWORD_LENGTH
    
    # Convert to lowercase and split into words
    words = re.findall(r'\b[a-zA-Z]+\b', text.lower())
    
    # Filter words by length and remove stop words
    keywords = [
        word for word in words 
        if min_length <= len(word) <= max_length 
        and word not in config.IGNORE_WORDS
    ]
    
    return keywords
