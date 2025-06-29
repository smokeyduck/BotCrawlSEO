"""
Backlink analysis module for SEO Analysis Tool
"""

import logging
from urllib.parse import urljoin, urlparse
from collections import defaultdict, Counter
import utils

class BacklinkAnalyzer:
    """
    Analyze backlinks and internal links from website content
    """
    
    def __init__(self):
        self.logger = utils.setup_logging()
    
    def analyze_links(self, parsed_data, base_url):
        """
        Analyze all links found on the website
        
        Args:
            parsed_data (dict): Parsed website data
            base_url (str): Base URL of the website
            
        Returns:
            dict: Comprehensive link analysis
        """
        try:
            base_domain = utils.get_domain_from_url(base_url)
            links = parsed_data.get('links', [])
            
            if not links:
                return self._empty_link_analysis()
            
            # Process and categorize links
            processed_links = self._process_links(links, base_url, base_domain)
            
            # Analyze link patterns
            analysis_results = {
                'total_links': len(links),
                'internal_links': processed_links['internal'],
                'external_links': processed_links['external'],
                'link_statistics': self._calculate_link_statistics(processed_links),
                'anchor_text_analysis': self._analyze_anchor_text(processed_links),
                'domain_analysis': self._analyze_external_domains(processed_links['external']),
                'link_types': self._categorize_link_types(processed_links),
                'nofollow_analysis': self._analyze_nofollow_links(processed_links)
            }
            
            return analysis_results
            
        except Exception as e:
            self.logger.error(f"Error in link analysis: {e}")
            return self._empty_link_analysis()
    
    def _process_links(self, links, base_url, base_domain):
        """Process and categorize links"""
        processed = {
            'internal': [],
            'external': [],
            'invalid': []
        }
        
        for link in links:
            try:
                url = link.get('url', '').strip()
                if not url:
                    continue
                
                # Handle relative URLs
                if url.startswith('/'):
                    url = urljoin(base_url, url)
                elif url.startswith('#'):
                    # Skip anchor links
                    continue
                elif url.startswith('mailto:') or url.startswith('tel:'):
                    # Skip email and phone links
                    continue
                elif not url.startswith(('http://', 'https://')):
                    # Try to resolve relative URLs
                    url = urljoin(base_url, url)
                
                # Validate URL
                if not utils.validate_url(url):
                    processed['invalid'].append(link)
                    continue
                
                # Categorize as internal or external
                link_data = {
                    'original_url': link.get('url', ''),
                    'resolved_url': url,
                    'anchor_text': link.get('text', '').strip(),
                    'rel_attributes': link.get('rel', []),
                    'is_nofollow': link.get('is_nofollow', False),
                    'domain': utils.get_domain_from_url(url)
                }
                
                if utils.is_internal_link(url, base_domain):
                    processed['internal'].append(link_data)
                else:
                    processed['external'].append(link_data)
                    
            except Exception as e:
                self.logger.warning(f"Error processing link {link}: {e}")
                processed['invalid'].append(link)
        
        return processed
    
    def _calculate_link_statistics(self, processed_links):
        """Calculate various link statistics"""
        internal_count = len(processed_links['internal'])
        external_count = len(processed_links['external'])
        total_valid = internal_count + external_count
        
        stats = {
            'total_valid_links': total_valid,
            'internal_count': internal_count,
            'external_count': external_count,
            'invalid_count': len(processed_links['invalid']),
            'internal_percentage': 0,
            'external_percentage': 0,
            'nofollow_count': 0,
            'dofollow_count': 0
        }
        
        if total_valid > 0:
            stats['internal_percentage'] = round((internal_count / total_valid) * 100, 2)
            stats['external_percentage'] = round((external_count / total_valid) * 100, 2)
        
        # Count nofollow/dofollow links
        all_links = processed_links['internal'] + processed_links['external']
        for link in all_links:
            if link['is_nofollow']:
                stats['nofollow_count'] += 1
            else:
                stats['dofollow_count'] += 1
        
        return stats
    
    def _analyze_anchor_text(self, processed_links):
        """Analyze anchor text patterns"""
        anchor_analysis = {
            'internal_anchors': Counter(),
            'external_anchors': Counter(),
            'empty_anchors': 0,
            'image_links': 0,
            'common_phrases': Counter()
        }
        
        for link_type in ['internal', 'external']:
            for link in processed_links[link_type]:
                anchor_text = link['anchor_text']
                
                if not anchor_text:
                    anchor_analysis['empty_anchors'] += 1
                elif anchor_text.lower() in ['image', 'img', '[image]']:
                    anchor_analysis['image_links'] += 1
                else:
                    anchor_analysis[f'{link_type}_anchors'][anchor_text] += 1
                    
                    # Extract common phrases (2-3 words)
                    words = anchor_text.lower().split()
                    if 2 <= len(words) <= 3:
                        anchor_analysis['common_phrases'][anchor_text.lower()] += 1
        
        # Convert to regular dicts and get top items
        return {
            'internal_anchors': dict(anchor_analysis['internal_anchors'].most_common(20)),
            'external_anchors': dict(anchor_analysis['external_anchors'].most_common(20)),
            'empty_anchors': anchor_analysis['empty_anchors'],
            'image_links': anchor_analysis['image_links'],
            'common_phrases': dict(anchor_analysis['common_phrases'].most_common(15))
        }
    
    def _analyze_external_domains(self, external_links):
        """Analyze external domains being linked to"""
        domain_analysis = {
            'unique_domains': set(),
            'domain_counts': Counter(),
            'top_domains': {},
            'domain_types': defaultdict(int)
        }
        
        for link in external_links:
            domain = link['domain']
            domain_analysis['unique_domains'].add(domain)
            domain_analysis['domain_counts'][domain] += 1
            
            # Categorize domain types
            if any(social in domain for social in ['facebook', 'twitter', 'linkedin', 'instagram', 'youtube']):
                domain_analysis['domain_types']['social_media'] += 1
            elif any(news in domain for news in ['news', 'blog', 'medium', 'wordpress']):
                domain_analysis['domain_types']['news_blog'] += 1
            elif domain.endswith('.gov'):
                domain_analysis['domain_types']['government'] += 1
            elif domain.endswith('.edu'):
                domain_analysis['domain_types']['education'] += 1
            else:
                domain_analysis['domain_types']['other'] += 1
        
        domain_analysis['unique_domains'] = list(domain_analysis['unique_domains'])
        domain_analysis['top_domains'] = dict(domain_analysis['domain_counts'].most_common(15))
        domain_analysis['domain_types'] = dict(domain_analysis['domain_types'])
        
        return domain_analysis
    
    def _categorize_link_types(self, processed_links):
        """Categorize links by type and purpose"""
        link_types = {
            'navigation': 0,
            'content': 0,
            'footer': 0,
            'social': 0,
            'external_resources': 0
        }
        
        navigation_keywords = ['home', 'about', 'contact', 'services', 'products', 'menu', 'nav']
        footer_keywords = ['privacy', 'terms', 'copyright', 'sitemap', 'legal']
        social_keywords = ['facebook', 'twitter', 'linkedin', 'instagram', 'youtube', 'social']
        
        all_links = processed_links['internal'] + processed_links['external']
        
        for link in all_links:
            anchor_text = link['anchor_text'].lower()
            url = link['resolved_url'].lower()
            
            if any(keyword in anchor_text or keyword in url for keyword in navigation_keywords):
                link_types['navigation'] += 1
            elif any(keyword in anchor_text or keyword in url for keyword in footer_keywords):
                link_types['footer'] += 1
            elif any(keyword in anchor_text or keyword in url for keyword in social_keywords):
                link_types['social'] += 1
            elif link in processed_links['external']:
                link_types['external_resources'] += 1
            else:
                link_types['content'] += 1
        
        return link_types
    
    def _analyze_nofollow_links(self, processed_links):
        """Analyze nofollow link patterns"""
        nofollow_analysis = {
            'internal_nofollow': 0,
            'external_nofollow': 0,
            'internal_dofollow': 0,
            'external_dofollow': 0,
            'nofollow_domains': Counter(),
            'nofollow_patterns': []
        }
        
        for link_type in ['internal', 'external']:
            for link in processed_links[link_type]:
                if link['is_nofollow']:
                    nofollow_analysis[f'{link_type}_nofollow'] += 1
                    if link_type == 'external':
                        nofollow_analysis['nofollow_domains'][link['domain']] += 1
                else:
                    nofollow_analysis[f'{link_type}_dofollow'] += 1
        
        # Convert Counter to dict
        nofollow_analysis['nofollow_domains'] = dict(
            nofollow_analysis['nofollow_domains'].most_common(10)
        )
        
        return nofollow_analysis
    
    def _empty_link_analysis(self):
        """Return empty link analysis structure"""
        return {
            'total_links': 0,
            'internal_links': [],
            'external_links': [],
            'link_statistics': {},
            'anchor_text_analysis': {},
            'domain_analysis': {},
            'link_types': {},
            'nofollow_analysis': {}
        }
