"""
Main application for Advanced SEO Analysis Tool
"""

import sys
import logging
from tqdm import tqdm
import utils
from web_scraper import WebScraper
from keyword_analyzer import KeywordAnalyzer
from backlink_analyzer import BacklinkAnalyzer
from seo_analyzer import SEOAnalyzer
from report_generator import ReportGenerator

class SEOAnalysisTool:
    """
    Main SEO Analysis Tool class
    """
    
    def __init__(self):
        self.logger = utils.setup_logging()
        self.scraper = WebScraper()
        self.keyword_analyzer = KeywordAnalyzer()
        self.backlink_analyzer = BacklinkAnalyzer()
        self.seo_analyzer = SEOAnalyzer()
        self.report_generator = ReportGenerator()
    
    def analyze_website(self, url, use_selenium=False):
        """
        Perform comprehensive SEO analysis of a website
        
        Args:
            url (str): Website URL to analyze
            use_selenium (bool): Whether to use Selenium for JavaScript rendering
            
        Returns:
            str: Path to generated report file or None if failed
        """
        try:
            # Validate and normalize URL
            if not self._validate_url(url):
                return None
            
            url = utils.normalize_url(url)
            self.logger.info(f"Starting SEO analysis for: {url}")
            
            # Progress tracking
            with tqdm(total=5, desc="SEO Analysis Progress") as pbar:
                
                # Step 1: Scrape website content
                pbar.set_description("Scraping website content...")
                parsed_data = self._scrape_website(url, use_selenium)
                if not parsed_data:
                    return None
                pbar.update(1)
                
                # Step 2: Analyze keywords
                pbar.set_description("Analyzing keywords...")
                keyword_analysis = self.keyword_analyzer.analyze_keywords(parsed_data)
                pbar.update(1)
                
                # Step 3: Analyze backlinks
                pbar.set_description("Analyzing links...")
                link_analysis = self.backlink_analyzer.analyze_links(parsed_data, url)
                pbar.update(1)
                
                # Step 4: Analyze SEO metrics
                pbar.set_description("Analyzing SEO metrics...")
                seo_analysis = self.seo_analyzer.analyze_seo_metrics(parsed_data)
                pbar.update(1)
                
                # Step 5: Generate report
                pbar.set_description("Generating report...")
                report_path = self.report_generator.generate_report(
                    url, keyword_analysis, link_analysis, seo_analysis, parsed_data
                )
                pbar.update(1)
            
            if report_path:
                self.logger.info(f"Analysis completed successfully. Report saved to: {report_path}")
                return report_path
            else:
                self.logger.error("Failed to generate report")
                return None
                
        except KeyboardInterrupt:
            self.logger.info("Analysis interrupted by user")
            return None
        except Exception as e:
            self.logger.error(f"Unexpected error during analysis: {e}")
            return None
        finally:
            self._cleanup()
    
    def _validate_url(self, url):
        """Validate the provided URL"""
        if not url:
            self.logger.error("No URL provided")
            return False
        
        # Normalize URL for validation
        normalized_url = utils.normalize_url(url)
        
        if not utils.validate_url(normalized_url):
            self.logger.error(f"Invalid URL: {url}")
            return False
        
        return True
    
    def _scrape_website(self, url, use_selenium=False):
        """Scrape website content with error handling"""
        try:
            # Get page content
            content, status_code, error_msg = self.scraper.get_page_content(url, use_selenium)
            
            if not content:
                if status_code == 403:
                    self.logger.error(f"Access forbidden (403): {error_msg}")
                elif status_code == 404:
                    self.logger.error(f"Page not found (404): {url}")
                elif status_code == 500:
                    self.logger.error(f"Server error (500): {error_msg}")
                else:
                    self.logger.error(f"Failed to retrieve content: {error_msg}")
                
                # Try with Selenium if regular request failed and not already using it
                if not use_selenium:
                    self.logger.info("Retrying with Selenium...")
                    return self._scrape_website(url, use_selenium=True)
                
                return None
            
            # Parse HTML content
            parsed_data = self.scraper.parse_html(content)
            
            if not parsed_data:
                self.logger.error("Failed to parse HTML content")
                return None
            
            self.logger.info(f"Successfully scraped and parsed content from {url}")
            return parsed_data
            
        except Exception as e:
            self.logger.error(f"Error scraping website: {e}")
            return None
    
    def _cleanup(self):
        """Clean up resources"""
        try:
            if self.scraper:
                self.scraper.close()
        except Exception as e:
            self.logger.warning(f"Error during cleanup: {e}")
    
    def get_analysis_summary(self, url):
        """
        Get a quick analysis summary without generating full report
        
        Args:
            url (str): Website URL to analyze
            
        Returns:
            dict: Summary of analysis results
        """
        try:
            if not self._validate_url(url):
                return None
            
            url = utils.normalize_url(url)
            
            # Quick scrape and analysis
            parsed_data = self._scrape_website(url)
            if not parsed_data:
                return None
            
            # Basic analysis
            keyword_analysis = self.keyword_analyzer.analyze_keywords(parsed_data)
            link_analysis = self.backlink_analyzer.analyze_links(parsed_data, url)
            seo_analysis = self.seo_analyzer.analyze_seo_metrics(parsed_data)
            
            # Create summary
            summary = {
                'url': url,
                'seo_score': seo_analysis.get('seo_score', 0),
                'primary_keywords_count': len(keyword_analysis.get('primary_keywords', [])),
                'total_links': link_analysis.get('total_links', 0),
                'internal_links': link_analysis.get('link_statistics', {}).get('internal_count', 0),
                'external_links': link_analysis.get('link_statistics', {}).get('external_count', 0),
                'word_count': keyword_analysis.get('content_stats', {}).get('word_count', 0),
                'top_keywords': keyword_analysis.get('primary_keywords', [])[:10],
                'main_issues': seo_analysis.get('recommendations', [])[:5]
            }
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Error getting analysis summary: {e}")
            return None

def main():
    """Main function for command-line usage"""
    if len(sys.argv) != 2:
        print("Usage: python seo_analyzer_main.py <website_url>")
        print("Example: python seo_analyzer_main.py https://example.com")
        sys.exit(1)
    
    url = sys.argv[1]
    
    print("Advanced SEO Analysis Tool")
    print("=" * 50)
    print(f"Analyzing: {url}")
    print()
    
    # Create analyzer instance
    analyzer = SEOAnalysisTool()
    
    # Perform analysis
    report_path = analyzer.analyze_website(url)
    
    if report_path:
        print(f"\n✅ Analysis completed successfully!")
        print(f"📄 Report saved to: {report_path}")
        print("\nYou can now open the report file to view the detailed analysis.")
    else:
        print("\n❌ Analysis failed. Please check the logs for more information.")
        sys.exit(1)

def interactive_mode():
    """Interactive mode for user input"""
    print("Advanced SEO Analysis Tool - Interactive Mode")
    print("=" * 50)
    
    analyzer = SEOAnalysisTool()
    
    while True:
        try:
            print("\nOptions:")
            print("1. Full SEO Analysis")
            print("2. Quick Summary")
            print("3. Exit")
            
            choice = input("\nSelect an option (1-3): ").strip()
            
            if choice == '3':
                print("Goodbye!")
                break
            elif choice in ['1', '2']:
                url = input("Enter website URL: ").strip()
                
                if not url:
                    print("Please enter a valid URL.")
                    continue
                
                if choice == '1':
                    print(f"\nStarting full analysis of: {url}")
                    report_path = analyzer.analyze_website(url)
                    
                    if report_path:
                        print(f"\n✅ Analysis completed!")
                        print(f"📄 Report saved to: {report_path}")
                    else:
                        print("\n❌ Analysis failed.")
                
                elif choice == '2':
                    print(f"\nGetting quick summary for: {url}")
                    summary = analyzer.get_analysis_summary(url)
                    
                    if summary:
                        print(f"\n📊 Quick Summary:")
                        print(f"SEO Score: {summary['seo_score']}/100")
                        print(f"Word Count: {summary['word_count']}")
                        print(f"Total Links: {summary['total_links']}")
                        print(f"Primary Keywords: {len(summary['top_keywords'])}")
                        print(f"Top Keywords: {', '.join(summary['top_keywords'][:5])}")
                    else:
                        print("\n❌ Failed to get summary.")
            else:
                print("Invalid option. Please select 1, 2, or 3.")
                
        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            print(f"\nError: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        main()
    else:
        interactive_mode()
