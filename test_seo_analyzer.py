"""
Test script for SEO Analysis Tool
"""

import unittest
import os
import tempfile
from unittest.mock import Mock, patch
from seo_analyzer_main import SEOAnalysisTool
from web_scraper import WebScraper
from keyword_analyzer import KeywordAnalyzer
from backlink_analyzer import BacklinkAnalyzer
from seo_analyzer import SEOAnalyzer
from report_generator import ReportGenerator
import utils

class TestSEOAnalyzer(unittest.TestCase):
    """Test cases for SEO Analysis Tool"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.analyzer = SEOAnalysisTool()
        self.test_url = "https://example.com"
        
        # Sample parsed data for testing
        self.sample_parsed_data = {
            'title': 'Example Website - Best Products and Services',
            'meta_description': 'Find the best products and services at Example Website. Quality guaranteed with fast shipping.',
            'meta_keywords': 'products, services, quality, shipping',
            'headings': {
                'h1': ['Welcome to Example Website'],
                'h2': ['Our Products', 'Our Services'],
                'h3': ['Product Category 1', 'Product Category 2']
            },
            'text_content': 'Welcome to our website. We offer the best products and services in the industry. Our quality products are shipped fast to your location. Contact us for more information about our services.',
            'links': [
                {'url': '/about', 'text': 'About Us', 'rel': [], 'is_nofollow': False},
                {'url': '/contact', 'text': 'Contact', 'rel': [], 'is_nofollow': False},
                {'url': 'https://google.com', 'text': 'Search', 'rel': ['nofollow'], 'is_nofollow': True},
                {'url': 'https://facebook.com', 'text': 'Follow Us', 'rel': [], 'is_nofollow': False}
            ],
            'images': [
                {'src': '/logo.png', 'alt': 'Company Logo', 'title': ''},
                {'src': '/product1.jpg', 'alt': 'Best Product', 'title': 'Our Best Product'},
                {'src': '/banner.jpg', 'alt': '', 'title': ''}
            ],
            'meta_tags': {
                'viewport': 'width=device-width, initial-scale=1',
                'charset': 'utf-8',
                'robots': 'index, follow'
            }
        }
    
    def test_url_validation(self):
        """Test URL validation functionality"""
        # Valid URLs
        self.assertTrue(utils.validate_url('https://example.com'))
        self.assertTrue(utils.validate_url('http://test.org'))
        
        # Invalid URLs
        self.assertFalse(utils.validate_url('not-a-url'))
        self.assertFalse(utils.validate_url(''))
        self.assertFalse(utils.validate_url('ftp://example.com'))
    
    def test_url_normalization(self):
        """Test URL normalization"""
        self.assertEqual(utils.normalize_url('example.com'), 'https://example.com')
        self.assertEqual(utils.normalize_url('https://example.com'), 'https://example.com')
        self.assertEqual(utils.normalize_url('http://example.com'), 'http://example.com')
    
    def test_domain_extraction(self):
        """Test domain extraction from URLs"""
        self.assertEqual(utils.get_domain_from_url('https://www.example.com/path'), 'example.com')
        self.assertEqual(utils.get_domain_from_url('http://subdomain.example.org'), 'subdomain.example.org')
    
    def test_keyword_extraction(self):
        """Test keyword extraction from text"""
        text = "This is a sample text with keywords for testing purposes"
        keywords = utils.extract_keywords_from_text(text)
        
        self.assertIn('sample', keywords)
        self.assertIn('keywords', keywords)
        self.assertIn('testing', keywords)
        self.assertNotIn('this', keywords)  # Should be filtered out as stop word
    
    def test_keyword_analyzer(self):
        """Test keyword analysis functionality"""
        analyzer = KeywordAnalyzer()
        results = analyzer.analyze_keywords(self.sample_parsed_data)
        
        self.assertIn('basic_keywords', results)
        self.assertIn('primary_keywords', results)
        self.assertIn('secondary_keywords', results)
        self.assertIn('content_stats', results)
        
        # Check if primary keywords are identified
        self.assertGreater(len(results['primary_keywords']), 0)
        
        # Check content stats
        stats = results['content_stats']
        self.assertGreater(stats.get('word_count', 0), 0)
    
    def test_backlink_analyzer(self):
        """Test backlink analysis functionality"""
        analyzer = BacklinkAnalyzer()
        results = analyzer.analyze_links(self.sample_parsed_data, self.test_url)
        
        self.assertIn('internal_links', results)
        self.assertIn('external_links', results)
        self.assertIn('link_statistics', results)
        
        # Check link categorization
        stats = results['link_statistics']
        self.assertEqual(stats['total_valid_links'], 4)
        self.assertEqual(stats['internal_count'], 2)  # /about, /contact
        self.assertEqual(stats['external_count'], 2)  # google.com, facebook.com
    
    def test_seo_analyzer(self):
        """Test SEO metrics analysis"""
        analyzer = SEOAnalyzer()
        results = analyzer.analyze_seo_metrics(self.sample_parsed_data)
        
        self.assertIn('title_analysis', results)
        self.assertIn('meta_description_analysis', results)
        self.assertIn('heading_structure', results)
        self.assertIn('image_seo', results)
        self.assertIn('seo_score', results)
        
        # Check SEO score calculation
        self.assertGreaterEqual(results['seo_score'], 0)
        self.assertLessEqual(results['seo_score'], 100)
        
        # Check title analysis
        title_analysis = results['title_analysis']
        self.assertEqual(title_analysis['title'], self.sample_parsed_data['title'])
        self.assertGreater(title_analysis['length'], 0)
    
    def test_report_generation(self):
        """Test report generation"""
        # Mock analysis results
        keyword_analysis = {'primary_keywords': ['test', 'example'], 'secondary_keywords': ['website']}
        link_analysis = {'total_links': 4, 'link_statistics': {'internal_count': 2, 'external_count': 2}}
        seo_analysis = {'seo_score': 75, 'recommendations': ['Improve meta description']}
        
        generator = ReportGenerator()
        
        # Test report generation with temporary file
        with tempfile.TemporaryDirectory() as temp_dir:
            # Temporarily change output directory
            original_output_dir = utils.config.OUTPUT_DIR
            utils.config.OUTPUT_DIR = temp_dir
            
            try:
                report_path = generator.generate_report(
                    self.test_url, keyword_analysis, link_analysis, seo_analysis, self.sample_parsed_data
                )
                
                self.assertIsNotNone(report_path)
                self.assertTrue(os.path.exists(report_path))
                
                # Check report content
                with open(report_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    self.assertIn('SEO ANALYSIS REPORT', content)
                    self.assertIn(self.test_url, content)
                    self.assertIn('PRIMARY KEYWORDS', content)
                    
            finally:
                utils.config.OUTPUT_DIR = original_output_dir
    
    @patch('web_scraper.WebScraper.get_page_content')
    @patch('web_scraper.WebScraper.parse_html')
    def test_full_analysis_workflow(self, mock_parse_html, mock_get_content):
        """Test the complete analysis workflow"""
        # Mock web scraper responses
        mock_get_content.return_value = ('<html><body>Test content</body></html>', 200, None)
        mock_parse_html.return_value = self.sample_parsed_data
        
        # Run analysis
        with tempfile.TemporaryDirectory() as temp_dir:
            original_output_dir = utils.config.OUTPUT_DIR
            utils.config.OUTPUT_DIR = temp_dir
            
            try:
                report_path = self.analyzer.analyze_website(self.test_url)
                
                self.assertIsNotNone(report_path)
                self.assertTrue(os.path.exists(report_path))
                
            finally:
                utils.config.OUTPUT_DIR = original_output_dir
    
    def test_analysis_summary(self):
        """Test quick analysis summary"""
        with patch.object(self.analyzer, '_scrape_website') as mock_scrape:
            mock_scrape.return_value = self.sample_parsed_data
            
            summary = self.analyzer.get_analysis_summary(self.test_url)
            
            self.assertIsNotNone(summary)
            self.assertIn('url', summary)
            self.assertIn('seo_score', summary)
            self.assertIn('primary_keywords_count', summary)
            self.assertIn('total_links', summary)
            
            self.assertEqual(summary['url'], self.test_url)
            self.assertGreaterEqual(summary['seo_score'], 0)

class TestUtilityFunctions(unittest.TestCase):
    """Test utility functions"""
    
    def test_clean_text(self):
        """Test text cleaning functionality"""
        dirty_text = "  This   is    dirty\n\n  text  with   extra   spaces  "
        clean = utils.clean_text(dirty_text)
        self.assertEqual(clean, "This is dirty text with extra spaces")
    
    def test_internal_link_detection(self):
        """Test internal link detection"""
        base_domain = "example.com"
        
        # Internal links
        self.assertTrue(utils.is_internal_link("/about", base_domain))
        self.assertTrue(utils.is_internal_link("https://example.com/page", base_domain))
        self.assertTrue(utils.is_internal_link("http://www.example.com/page", base_domain))
        
        # External links
        self.assertFalse(utils.is_internal_link("https://google.com", base_domain))
        self.assertFalse(utils.is_internal_link("http://other-site.com", base_domain))

def run_demo_analysis():
    """Run a demonstration analysis"""
    print("SEO Analysis Tool - Demo Mode")
    print("=" * 50)
    
    # Test with a simple HTML string (simulated)
    print("Running demo analysis with sample data...")
    
    analyzer = SEOAnalysisTool()
    
    # Create sample data for demo
    sample_data = {
        'title': 'Demo Website - SEO Analysis Example',
        'meta_description': 'This is a demo website for testing SEO analysis functionality.',
        'text_content': 'Welcome to our demo website. This site demonstrates SEO analysis capabilities including keyword extraction, link analysis, and content optimization recommendations.',
        'links': [
            {'url': '/home', 'text': 'Home', 'rel': [], 'is_nofollow': False},
            {'url': 'https://example.com', 'text': 'External Link', 'rel': [], 'is_nofollow': False}
        ],
        'images': [
            {'src': '/demo.jpg', 'alt': 'Demo Image', 'title': 'Demo'}
        ],
        'headings': {
            'h1': ['Demo Website'],
            'h2': ['Features', 'Benefits']
        },
        'meta_tags': {'viewport': 'width=device-width, initial-scale=1'}
    }
    
    # Analyze components
    keyword_analyzer = KeywordAnalyzer()
    keywords = keyword_analyzer.analyze_keywords(sample_data)
    
    backlink_analyzer = BacklinkAnalyzer()
    links = backlink_analyzer.analyze_links(sample_data, "https://demo.com")
    
    seo_analyzer = SEOAnalyzer()
    seo_metrics = seo_analyzer.analyze_seo_metrics(sample_data)
    
    # Display results
    print(f"\n📊 Demo Results:")
    print(f"Primary Keywords: {', '.join(keywords.get('primary_keywords', [])[:5])}")
    print(f"Total Links: {links.get('total_links', 0)}")
    print(f"SEO Score: {seo_metrics.get('seo_score', 0)}/100")
    print(f"Word Count: {keywords.get('content_stats', {}).get('word_count', 0)}")
    
    print("\n✅ Demo completed successfully!")

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == 'demo':
        run_demo_analysis()
    else:
        # Run unit tests
        unittest.main()
