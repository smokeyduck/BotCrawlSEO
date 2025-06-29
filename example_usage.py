"""
Example usage scenarios for the Advanced SEO Analysis Tool
"""

from seo_analyzer_main import SEOAnalysisTool
import time

def example_basic_analysis():
    """Example 1: Basic SEO analysis of a website"""
    print("Example 1: Basic SEO Analysis")
    print("-" * 40)
    
    # Create analyzer instance
    analyzer = SEOAnalysisTool()
    
    # Analyze a website (replace with actual URL)
    url = "https://example.com"
    print(f"Analyzing: {url}")
    
    # Perform full analysis
    report_path = analyzer.analyze_website(url)
    
    if report_path:
        print(f"✅ Analysis completed!")
        print(f"📄 Report saved to: {report_path}")
        
        # Read and display first few lines of the report
        try:
            with open(report_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()[:20]  # First 20 lines
                print("\n📋 Report Preview:")
                print("".join(lines))
                print("... (truncated)")
        except Exception as e:
            print(f"Could not preview report: {e}")
    else:
        print("❌ Analysis failed")

def example_quick_summary():
    """Example 2: Quick analysis summary"""
    print("\nExample 2: Quick Analysis Summary")
    print("-" * 40)
    
    analyzer = SEOAnalysisTool()
    
    # Get quick summary without full report
    url = "https://example.com"
    print(f"Getting quick summary for: {url}")
    
    summary = analyzer.get_analysis_summary(url)
    
    if summary:
        print("📊 Quick Summary Results:")
        print(f"• SEO Score: {summary['seo_score']}/100")
        print(f"• Word Count: {summary['word_count']}")
        print(f"• Total Links: {summary['total_links']}")
        print(f"• Internal Links: {summary['internal_links']}")
        print(f"• External Links: {summary['external_links']}")
        print(f"• Primary Keywords Found: {summary['primary_keywords_count']}")
        
        if summary['top_keywords']:
            print(f"• Top Keywords: {', '.join(summary['top_keywords'][:5])}")
        
        if summary['main_issues']:
            print("• Main Issues:")
            for issue in summary['main_issues'][:3]:
                print(f"  - {issue}")
    else:
        print("❌ Failed to get summary")

def example_batch_analysis():
    """Example 3: Batch analysis of multiple websites"""
    print("\nExample 3: Batch Analysis")
    print("-" * 40)
    
    # List of websites to analyze
    websites = [
        "https://example.com",
        "https://httpbin.org",  # Simple test site
        # Add more URLs as needed
    ]
    
    analyzer = SEOAnalysisTool()
    results = []
    
    print(f"Analyzing {len(websites)} websites...")
    
    for i, url in enumerate(websites, 1):
        print(f"\n[{i}/{len(websites)}] Analyzing: {url}")
        
        try:
            # Get quick summary for batch processing
            summary = analyzer.get_analysis_summary(url)
            
            if summary:
                results.append(summary)
                print(f"✅ Completed - SEO Score: {summary['seo_score']}/100")
            else:
                print("❌ Failed")
                
            # Add delay between requests to be respectful
            if i < len(websites):
                time.sleep(2)
                
        except Exception as e:
            print(f"❌ Error: {e}")
    
    # Display batch results summary
    if results:
        print(f"\n📊 Batch Analysis Summary ({len(results)} successful):")
        print("-" * 50)
        
        for result in results:
            print(f"• {result['url']}")
            print(f"  SEO Score: {result['seo_score']}/100")
            print(f"  Keywords: {result['primary_keywords_count']}")
            print(f"  Links: {result['total_links']}")
            print()

def example_custom_analysis():
    """Example 4: Custom analysis with specific components"""
    print("\nExample 4: Custom Component Analysis")
    print("-" * 40)
    
    from web_scraper import WebScraper
    from keyword_analyzer import KeywordAnalyzer
    from backlink_analyzer import BacklinkAnalyzer
    from seo_analyzer import SEOAnalyzer
    
    url = "https://httpbin.org/html"
    print(f"Custom analysis of: {url}")
    
    try:
        # Step 1: Scrape content
        print("1. Scraping content...")
        scraper = WebScraper()
        content, status_code, error = scraper.get_page_content(url)
        
        if not content:
            print(f"❌ Failed to scrape: {error}")
            return
        
        # Step 2: Parse HTML
        print("2. Parsing HTML...")
        parsed_data = scraper.parse_html(content)
        
        # Step 3: Analyze keywords
        print("3. Analyzing keywords...")
        keyword_analyzer = KeywordAnalyzer()
        keyword_results = keyword_analyzer.analyze_keywords(parsed_data)
        
        # Step 4: Analyze links
        print("4. Analyzing links...")
        link_analyzer = BacklinkAnalyzer()
        link_results = link_analyzer.analyze_links(parsed_data, url)
        
        # Step 5: SEO analysis
        print("5. Analyzing SEO metrics...")
        seo_analyzer = SEOAnalyzer()
        seo_results = seo_analyzer.analyze_seo_metrics(parsed_data)
        
        # Display custom results
        print("\n📋 Custom Analysis Results:")
        print(f"• Page Title: {parsed_data.get('title', 'N/A')}")
        print(f"• Word Count: {keyword_results.get('content_stats', {}).get('word_count', 0)}")
        print(f"• Primary Keywords: {len(keyword_results.get('primary_keywords', []))}")
        print(f"• Total Links: {link_results.get('total_links', 0)}")
        print(f"• SEO Score: {seo_results.get('seo_score', 0)}/100")
        
        # Show top keywords
        top_keywords = keyword_results.get('primary_keywords', [])[:5]
        if top_keywords:
            print(f"• Top Keywords: {', '.join(top_keywords)}")
        
        # Cleanup
        scraper.close()
        
    except Exception as e:
        print(f"❌ Custom analysis failed: {e}")

def example_configuration_demo():
    """Example 5: Demonstrate configuration options"""
    print("\nExample 5: Configuration Options")
    print("-" * 40)
    
    import config
    
    print("Current Configuration:")
    print(f"• Request Timeout: {config.REQUEST_TIMEOUT} seconds")
    print(f"• Rate Limit Delay: {config.RATE_LIMIT_DELAY} seconds")
    print(f"• Top Keywords Count: {config.TOP_KEYWORDS_COUNT}")
    print(f"• Min Keyword Length: {config.MIN_KEYWORD_LENGTH}")
    print(f"• Output Directory: {config.OUTPUT_DIR}")
    print(f"• User Agent: {config.USER_AGENT[:50]}...")
    
    print("\nYou can modify config.py to customize:")
    print("• Analysis parameters (keyword counts, lengths)")
    print("• Scraping behavior (timeouts, delays)")
    print("• Output settings (directory, filename format)")
    print("• Stop words and ignored terms")

def example_error_handling():
    """Example 6: Demonstrate error handling"""
    print("\nExample 6: Error Handling Demonstration")
    print("-" * 40)
    
    analyzer = SEOAnalysisTool()
    
    # Test various error scenarios
    test_cases = [
        ("invalid-url", "Invalid URL format"),
        ("https://nonexistent-domain-12345.com", "Non-existent domain"),
        ("https://httpstat.us/404", "404 Not Found"),
        ("https://httpstat.us/500", "Server Error"),
    ]
    
    for url, description in test_cases:
        print(f"\nTesting: {description}")
        print(f"URL: {url}")
        
        try:
            summary = analyzer.get_analysis_summary(url)
            if summary:
                print("✅ Unexpected success")
            else:
                print("❌ Failed as expected")
        except Exception as e:
            print(f"❌ Exception caught: {type(e).__name__}")

def main():
    """Run all examples"""
    print("Advanced SEO Analysis Tool - Example Usage")
    print("=" * 60)
    
    examples = [
        ("Basic Analysis", example_basic_analysis),
        ("Quick Summary", example_quick_summary),
        ("Batch Analysis", example_batch_analysis),
        ("Custom Analysis", example_custom_analysis),
        ("Configuration Demo", example_configuration_demo),
        ("Error Handling", example_error_handling),
    ]
    
    print("Available examples:")
    for i, (name, _) in enumerate(examples, 1):
        print(f"{i}. {name}")
    
    print("\nSelect an example to run (1-6), or 'all' to run all examples:")
    choice = input("Enter your choice: ").strip().lower()
    
    if choice == 'all':
        for name, func in examples:
            print(f"\n{'='*60}")
            print(f"Running: {name}")
            print('='*60)
            try:
                func()
            except KeyboardInterrupt:
                print("\n⏹️ Interrupted by user")
                break
            except Exception as e:
                print(f"❌ Example failed: {e}")
    elif choice.isdigit() and 1 <= int(choice) <= len(examples):
        name, func = examples[int(choice) - 1]
        print(f"\nRunning: {name}")
        print("-" * 40)
        try:
            func()
        except KeyboardInterrupt:
            print("\n⏹️ Interrupted by user")
        except Exception as e:
            print(f"❌ Example failed: {e}")
    else:
        print("Invalid choice. Please run the script again.")

if __name__ == "__main__":
    main()
