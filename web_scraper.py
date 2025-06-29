"""
Web scraping module for SEO Analysis Tool
"""

import requests
import time
import logging
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager
from urllib.parse import urljoin, urlparse
from urllib.robotparser import RobotFileParser
import config
import utils

class WebScraper:
    """
    Advanced web scraper with support for both static and dynamic content
    """
    
    def __init__(self):
        self.logger = utils.setup_logging()
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': config.USER_AGENT})
        self.driver = None
        
    def check_robots_txt(self, url):
        """
        Check if scraping is allowed according to robots.txt
        
        Args:
            url (str): URL to check
            
        Returns:
            bool: True if allowed, False otherwise
        """
        try:
            parsed_url = urlparse(url)
            robots_url = f"{parsed_url.scheme}://{parsed_url.netloc}/robots.txt"
            
            rp = RobotFileParser()
            rp.set_url(robots_url)
            rp.read()
            
            return rp.can_fetch(config.USER_AGENT, url)
        except Exception as e:
            self.logger.warning(f"Could not check robots.txt: {e}")
            return True  # Allow scraping if robots.txt check fails
    
    def get_page_content(self, url, use_selenium=False):
        """
        Get page content using requests or Selenium
        
        Args:
            url (str): URL to scrape
            use_selenium (bool): Whether to use Selenium for JavaScript rendering
            
        Returns:
            tuple: (content, status_code, error_message)
        """
        try:
            if not self.check_robots_txt(url):
                return None, 403, "Blocked by robots.txt"
            
            if use_selenium:
                return self._get_content_selenium(url)
            else:
                return self._get_content_requests(url)
                
        except Exception as e:
            self.logger.error(f"Error scraping {url}: {e}")
            return None, 500, str(e)
    
    def _get_content_requests(self, url):
        """Get content using requests library"""
        for attempt in range(config.MAX_RETRIES):
            try:
                time.sleep(config.RATE_LIMIT_DELAY)
                
                response = self.session.get(
                    url, 
                    timeout=config.REQUEST_TIMEOUT,
                    allow_redirects=True
                )
                
                if response.status_code == 200:
                    return response.text, response.status_code, None
                else:
                    self.logger.warning(f"HTTP {response.status_code} for {url}")
                    return None, response.status_code, f"HTTP {response.status_code}"
                    
            except requests.exceptions.RequestException as e:
                self.logger.warning(f"Attempt {attempt + 1} failed for {url}: {e}")
                if attempt == config.MAX_RETRIES - 1:
                    return None, 500, str(e)
                time.sleep(2 ** attempt)  # Exponential backoff
        
        return None, 500, "Max retries exceeded"
    
    def _get_content_selenium(self, url):
        """Get content using Selenium for JavaScript-heavy sites"""
        try:
            if not self.driver:
                self._setup_selenium()
            
            self.driver.get(url)
            
            # Wait for page to load
            WebDriverWait(self.driver, config.SELENIUM_TIMEOUT).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Additional wait for dynamic content
            time.sleep(2)
            
            content = self.driver.page_source
            return content, 200, None
            
        except TimeoutException:
            return None, 408, "Page load timeout"
        except WebDriverException as e:
            return None, 500, f"Selenium error: {e}"
    
    def _setup_selenium(self):
        """Setup Selenium WebDriver"""
        try:
            chrome_options = Options()
            if config.HEADLESS_BROWSER:
                chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument(f"--user-agent={config.USER_AGENT}")
            
            self.driver = webdriver.Chrome(
                ChromeDriverManager().install(),
                options=chrome_options
            )
            
        except Exception as e:
            self.logger.error(f"Failed to setup Selenium: {e}")
            raise
    
    def parse_html(self, html_content):
        """
        Parse HTML content and extract structured data
        
        Args:
            html_content (str): HTML content to parse
            
        Returns:
            dict: Parsed data including text, links, meta tags, etc.
        """
        try:
            soup = BeautifulSoup(html_content, 'lxml')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            parsed_data = {
                'title': self._extract_title(soup),
                'meta_description': self._extract_meta_description(soup),
                'meta_keywords': self._extract_meta_keywords(soup),
                'headings': self._extract_headings(soup),
                'text_content': self._extract_text_content(soup),
                'links': self._extract_links(soup),
                'images': self._extract_images(soup),
                'meta_tags': self._extract_all_meta_tags(soup)
            }
            
            return parsed_data
            
        except Exception as e:
            self.logger.error(f"Error parsing HTML: {e}")
            return {}
    
    def _extract_title(self, soup):
        """Extract page title"""
        title_tag = soup.find('title')
        return title_tag.get_text().strip() if title_tag else ""
    
    def _extract_meta_description(self, soup):
        """Extract meta description"""
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        return meta_desc.get('content', '').strip() if meta_desc else ""
    
    def _extract_meta_keywords(self, soup):
        """Extract meta keywords"""
        meta_keywords = soup.find('meta', attrs={'name': 'keywords'})
        return meta_keywords.get('content', '').strip() if meta_keywords else ""
    
    def _extract_headings(self, soup):
        """Extract all headings (H1-H6)"""
        headings = {}
        for i in range(1, 7):
            heading_tags = soup.find_all(f'h{i}')
            headings[f'h{i}'] = [tag.get_text().strip() for tag in heading_tags]
        return headings
    
    def _extract_text_content(self, soup):
        """Extract clean text content"""
        text = soup.get_text()
        return utils.clean_text(text)
    
    def _extract_links(self, soup):
        """Extract all links"""
        links = []
        for link in soup.find_all('a', href=True):
            href = link['href'].strip()
            text = link.get_text().strip()
            rel = link.get('rel', [])
            
            links.append({
                'url': href,
                'text': text,
                'rel': rel,
                'is_nofollow': 'nofollow' in rel
            })
        
        return links
    
    def _extract_images(self, soup):
        """Extract image information"""
        images = []
        for img in soup.find_all('img'):
            src = img.get('src', '').strip()
            alt = img.get('alt', '').strip()
            title = img.get('title', '').strip()
            
            if src:
                images.append({
                    'src': src,
                    'alt': alt,
                    'title': title
                })
        
        return images
    
    def _extract_all_meta_tags(self, soup):
        """Extract all meta tags"""
        meta_tags = {}
        for meta in soup.find_all('meta'):
            name = meta.get('name') or meta.get('property') or meta.get('http-equiv')
            content = meta.get('content')
            
            if name and content:
                meta_tags[name] = content
        
        return meta_tags
    
    def close(self):
        """Clean up resources"""
        if self.driver:
            self.driver.quit()
        self.session.close()
