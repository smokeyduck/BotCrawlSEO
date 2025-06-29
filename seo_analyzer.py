"""
SEO metrics analysis module for SEO Analysis Tool
"""

import logging
import re
from collections import Counter
import utils

class SEOAnalyzer:
    """
    Analyze various SEO metrics and provide recommendations
    """
    
    def __init__(self):
        self.logger = utils.setup_logging()
    
    def analyze_seo_metrics(self, parsed_data):
        """
        Perform comprehensive SEO analysis
        
        Args:
            parsed_data (dict): Parsed website data
            
        Returns:
            dict: SEO analysis results with recommendations
        """
        try:
            analysis_results = {
                'title_analysis': self._analyze_title(parsed_data.get('title', '')),
                'meta_description_analysis': self._analyze_meta_description(parsed_data.get('meta_description', '')),
                'heading_structure': self._analyze_heading_structure(parsed_data.get('headings', {})),
                'image_seo': self._analyze_image_seo(parsed_data.get('images', [])),
                'content_structure': self._analyze_content_structure(parsed_data),
                'meta_tags_analysis': self._analyze_meta_tags(parsed_data.get('meta_tags', {})),
                'url_structure': self._analyze_url_structure(parsed_data),
                'seo_score': 0,
                'recommendations': []
            }
            
            # Calculate overall SEO score
            analysis_results['seo_score'] = self._calculate_seo_score(analysis_results)
            
            # Generate recommendations
            analysis_results['recommendations'] = self._generate_recommendations(analysis_results)
            
            return analysis_results
            
        except Exception as e:
            self.logger.error(f"Error in SEO analysis: {e}")
            return self._empty_seo_analysis()
    
    def _analyze_title(self, title):
        """Analyze page title for SEO best practices"""
        analysis = {
            'title': title,
            'length': len(title),
            'word_count': len(title.split()) if title else 0,
            'issues': [],
            'score': 0
        }
        
        if not title:
            analysis['issues'].append("Missing page title")
            return analysis
        
        # Check title length (optimal: 50-60 characters)
        if len(title) < 30:
            analysis['issues'].append("Title too short (< 30 characters)")
        elif len(title) > 60:
            analysis['issues'].append("Title too long (> 60 characters)")
        else:
            analysis['score'] += 25
        
        # Check for duplicate words
        words = title.lower().split()
        if len(words) != len(set(words)):
            analysis['issues'].append("Title contains duplicate words")
        else:
            analysis['score'] += 15
        
        # Check for brand/company name
        if any(char in title for char in ['|', '-', ':']):
            analysis['score'] += 10
        
        # Check for numbers (often perform well)
        if any(char.isdigit() for char in title):
            analysis['score'] += 10
        
        # Base score for having a title
        analysis['score'] += 40
        
        return analysis
    
    def _analyze_meta_description(self, meta_desc):
        """Analyze meta description for SEO best practices"""
        analysis = {
            'description': meta_desc,
            'length': len(meta_desc),
            'word_count': len(meta_desc.split()) if meta_desc else 0,
            'issues': [],
            'score': 0
        }
        
        if not meta_desc:
            analysis['issues'].append("Missing meta description")
            return analysis
        
        # Check description length (optimal: 150-160 characters)
        if len(meta_desc) < 120:
            analysis['issues'].append("Meta description too short (< 120 characters)")
        elif len(meta_desc) > 160:
            analysis['issues'].append("Meta description too long (> 160 characters)")
        else:
            analysis['score'] += 30
        
        # Check for call-to-action words
        cta_words = ['learn', 'discover', 'find', 'get', 'buy', 'download', 'try', 'start']
        if any(word in meta_desc.lower() for word in cta_words):
            analysis['score'] += 15
        
        # Check for unique content (not just repeating title)
        if meta_desc and len(set(meta_desc.lower().split())) > 5:
            analysis['score'] += 15
        
        # Base score for having a meta description
        analysis['score'] += 40
        
        return analysis
    
    def _analyze_heading_structure(self, headings):
        """Analyze heading structure for SEO and accessibility"""
        analysis = {
            'heading_counts': {},
            'structure_issues': [],
            'score': 0,
            'total_headings': 0
        }
        
        # Count headings by level
        for level in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            count = len(headings.get(level, []))
            analysis['heading_counts'][level] = count
            analysis['total_headings'] += count
        
        # Check H1 usage
        h1_count = analysis['heading_counts'].get('h1', 0)
        if h1_count == 0:
            analysis['structure_issues'].append("Missing H1 tag")
        elif h1_count > 1:
            analysis['structure_issues'].append("Multiple H1 tags found")
        else:
            analysis['score'] += 30
        
        # Check heading hierarchy
        if self._check_heading_hierarchy(analysis['heading_counts']):
            analysis['score'] += 20
        else:
            analysis['structure_issues'].append("Poor heading hierarchy")
        
        # Check for adequate heading usage
        if analysis['total_headings'] >= 3:
            analysis['score'] += 20
        elif analysis['total_headings'] >= 1:
            analysis['score'] += 10
        else:
            analysis['structure_issues'].append("Insufficient heading usage")
        
        # Analyze heading content
        heading_analysis = self._analyze_heading_content(headings)
        analysis.update(heading_analysis)
        
        return analysis
    
    def _check_heading_hierarchy(self, heading_counts):
        """Check if heading hierarchy is logical"""
        # Simple check: ensure we don't skip levels dramatically
        levels_used = [level for level, count in heading_counts.items() if count > 0]
        
        if not levels_used:
            return False
        
        # Extract numbers and sort
        level_numbers = sorted([int(level[1]) for level in levels_used])
        
        # Check for reasonable progression
        for i in range(1, len(level_numbers)):
            if level_numbers[i] - level_numbers[i-1] > 2:
                return False
        
        return True
    
    def _analyze_heading_content(self, headings):
        """Analyze heading content for keywords and length"""
        content_analysis = {
            'heading_keywords': Counter(),
            'avg_heading_length': 0,
            'long_headings': 0
        }
        
        all_heading_text = []
        
        for level, heading_list in headings.items():
            for heading in heading_list:
                all_heading_text.append(heading)
                
                # Check heading length
                if len(heading) > 70:
                    content_analysis['long_headings'] += 1
                
                # Extract keywords
                keywords = utils.extract_keywords_from_text(heading)
                for keyword in keywords:
                    content_analysis['heading_keywords'][keyword] += 1
        
        if all_heading_text:
            total_length = sum(len(h) for h in all_heading_text)
            content_analysis['avg_heading_length'] = total_length / len(all_heading_text)
        
        content_analysis['heading_keywords'] = dict(
            content_analysis['heading_keywords'].most_common(10)
        )
        
        return content_analysis
    
    def _analyze_image_seo(self, images):
        """Analyze image SEO optimization"""
        analysis = {
            'total_images': len(images),
            'images_with_alt': 0,
            'images_without_alt': 0,
            'empty_alt_tags': 0,
            'avg_alt_length': 0,
            'alt_text_keywords': Counter(),
            'issues': [],
            'score': 0
        }
        
        if not images:
            analysis['issues'].append("No images found")
            return analysis
        
        alt_texts = []
        
        for img in images:
            alt_text = img.get('alt', '').strip()
            
            if alt_text:
                analysis['images_with_alt'] += 1
                alt_texts.append(alt_text)
                
                # Extract keywords from alt text
                keywords = utils.extract_keywords_from_text(alt_text)
                for keyword in keywords:
                    analysis['alt_text_keywords'][keyword] += 1
            else:
                analysis['images_without_alt'] += 1
        
        # Calculate statistics
        if alt_texts:
            analysis['avg_alt_length'] = sum(len(alt) for alt in alt_texts) / len(alt_texts)
        
        # Calculate score
        alt_percentage = (analysis['images_with_alt'] / analysis['total_images']) * 100
        if alt_percentage >= 90:
            analysis['score'] = 100
        elif alt_percentage >= 70:
            analysis['score'] = 80
        elif alt_percentage >= 50:
            analysis['score'] = 60
        else:
            analysis['score'] = 30
        
        # Add issues
        if analysis['images_without_alt'] > 0:
            analysis['issues'].append(f"{analysis['images_without_alt']} images missing alt text")
        
        analysis['alt_text_keywords'] = dict(
            analysis['alt_text_keywords'].most_common(10)
        )
        
        return analysis
    
    def _analyze_content_structure(self, parsed_data):
        """Analyze overall content structure"""
        text_content = parsed_data.get('text_content', '')
        
        analysis = {
            'content_length': len(text_content),
            'word_count': len(text_content.split()) if text_content else 0,
            'paragraph_count': len([p for p in text_content.split('\n\n') if p.strip()]),
            'avg_paragraph_length': 0,
            'issues': [],
            'score': 0
        }
        
        # Calculate average paragraph length
        paragraphs = [p.strip() for p in text_content.split('\n\n') if p.strip()]
        if paragraphs:
            total_words = sum(len(p.split()) for p in paragraphs)
            analysis['avg_paragraph_length'] = total_words / len(paragraphs)
        
        # Analyze content length
        word_count = analysis['word_count']
        if word_count < 300:
            analysis['issues'].append("Content too short (< 300 words)")
            analysis['score'] += 20
        elif word_count < 600:
            analysis['score'] += 60
        else:
            analysis['score'] += 100
        
        # Check paragraph structure
        if analysis['avg_paragraph_length'] > 100:
            analysis['issues'].append("Paragraphs too long (avg > 100 words)")
        
        return analysis
    
    def _analyze_meta_tags(self, meta_tags):
        """Analyze various meta tags"""
        analysis = {
            'total_meta_tags': len(meta_tags),
            'important_tags': {},
            'social_tags': {},
            'technical_tags': {},
            'score': 0
        }
        
        # Important SEO meta tags
        important_tags = ['description', 'keywords', 'author', 'robots']
        for tag in important_tags:
            if tag in meta_tags:
                analysis['important_tags'][tag] = meta_tags[tag]
                analysis['score'] += 10
        
        # Social media tags
        social_tags = ['og:title', 'og:description', 'og:image', 'twitter:card']
        for tag in social_tags:
            if tag in meta_tags:
                analysis['social_tags'][tag] = meta_tags[tag]
                analysis['score'] += 5
        
        # Technical tags
        technical_tags = ['viewport', 'charset', 'robots']
        for tag in technical_tags:
            if tag in meta_tags:
                analysis['technical_tags'][tag] = meta_tags[tag]
        
        return analysis
    
    def _analyze_url_structure(self, parsed_data):
        """Analyze URL structure (basic analysis)"""
        # This would typically analyze the current URL structure
        # For now, return basic structure
        return {
            'analysis': "URL structure analysis would require the actual URL",
            'score': 50  # Neutral score
        }
    
    def _calculate_seo_score(self, analysis_results):
        """Calculate overall SEO score"""
        scores = []
        
        # Collect scores from different analyses
        if 'title_analysis' in analysis_results:
            scores.append(analysis_results['title_analysis'].get('score', 0))
        
        if 'meta_description_analysis' in analysis_results:
            scores.append(analysis_results['meta_description_analysis'].get('score', 0))
        
        if 'heading_structure' in analysis_results:
            scores.append(analysis_results['heading_structure'].get('score', 0))
        
        if 'image_seo' in analysis_results:
            scores.append(analysis_results['image_seo'].get('score', 0))
        
        if 'content_structure' in analysis_results:
            scores.append(analysis_results['content_structure'].get('score', 0))
        
        if 'meta_tags_analysis' in analysis_results:
            scores.append(min(analysis_results['meta_tags_analysis'].get('score', 0), 100))
        
        # Calculate weighted average
        if scores:
            return round(sum(scores) / len(scores), 1)
        
        return 0
    
    def _generate_recommendations(self, analysis_results):
        """Generate SEO recommendations based on analysis"""
        recommendations = []
        
        # Title recommendations
        title_issues = analysis_results.get('title_analysis', {}).get('issues', [])
        recommendations.extend(title_issues)
        
        # Meta description recommendations
        meta_issues = analysis_results.get('meta_description_analysis', {}).get('issues', [])
        recommendations.extend(meta_issues)
        
        # Heading recommendations
        heading_issues = analysis_results.get('heading_structure', {}).get('structure_issues', [])
        recommendations.extend(heading_issues)
        
        # Image recommendations
        image_issues = analysis_results.get('image_seo', {}).get('issues', [])
        recommendations.extend(image_issues)
        
        # Content recommendations
        content_issues = analysis_results.get('content_structure', {}).get('issues', [])
        recommendations.extend(content_issues)
        
        return recommendations
    
    def _empty_seo_analysis(self):
        """Return empty SEO analysis structure"""
        return {
            'title_analysis': {},
            'meta_description_analysis': {},
            'heading_structure': {},
            'image_seo': {},
            'content_structure': {},
            'meta_tags_analysis': {},
            'url_structure': {},
            'seo_score': 0,
            'recommendations': []
        }
