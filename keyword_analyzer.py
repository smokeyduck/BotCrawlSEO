"""
Keyword analysis module for SEO Analysis Tool
"""

import re
import logging
from collections import Counter, defaultdict
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import CountVectorizer
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.stem import PorterStemmer
from nltk.chunk import ne_chunk
from nltk.tag import pos_tag
import textstat
import config
import utils

class KeywordAnalyzer:
    """
    Advanced keyword analysis using multiple NLP techniques
    """
    
    def __init__(self):
        self.logger = utils.setup_logging()
        self.stemmer = PorterStemmer()
        self._download_nltk_data()
        
        # Initialize stop words
        try:
            self.stop_words = set(stopwords.words('english'))
            self.stop_words.update(config.IGNORE_WORDS)
        except:
            self.stop_words = config.IGNORE_WORDS
    
    def _download_nltk_data(self):
        """Download required NLTK data"""
        try:
            nltk.download('punkt', quiet=True)
            nltk.download('punkt_tab', quiet=True)  # New tokenizer data
            nltk.download('stopwords', quiet=True)
            nltk.download('averaged_perceptron_tagger', quiet=True)
            nltk.download('maxent_ne_chunker', quiet=True)
            nltk.download('words', quiet=True)
        except Exception as e:
            self.logger.warning(f"Could not download NLTK data: {e}")
    
    def analyze_keywords(self, parsed_data):
        """
        Perform comprehensive keyword analysis
        
        Args:
            parsed_data (dict): Parsed website data
            
        Returns:
            dict: Comprehensive keyword analysis results
        """
        try:
            # Combine all text content
            all_text = self._combine_text_content(parsed_data)
            
            if not all_text:
                return self._empty_analysis()
            
            # Perform different types of analysis
            analysis_results = {
                'basic_keywords': self._basic_keyword_analysis(all_text),
                'tfidf_keywords': self._tfidf_analysis(all_text),
                'ngram_analysis': self._ngram_analysis(all_text),
                'heading_keywords': self._analyze_headings(parsed_data.get('headings', {})),
                'meta_keywords': self._analyze_meta_content(parsed_data),
                'content_stats': self._calculate_content_stats(all_text),
                'keyword_density': self._calculate_keyword_density(all_text),
                'primary_keywords': [],
                'secondary_keywords': []
            }
            
            # Combine and rank keywords
            analysis_results['primary_keywords'] = self._get_primary_keywords(analysis_results)
            analysis_results['secondary_keywords'] = self._get_secondary_keywords(analysis_results)
            
            return analysis_results
            
        except Exception as e:
            self.logger.error(f"Error in keyword analysis: {e}")
            return self._empty_analysis()
    
    def _combine_text_content(self, parsed_data):
        """Combine all text content with appropriate weighting"""
        text_parts = []
        
        # Title (high weight)
        title = parsed_data.get('title', '')
        if title:
            text_parts.extend([title] * 5)  # Weight title 5x
        
        # Meta description (high weight)
        meta_desc = parsed_data.get('meta_description', '')
        if meta_desc:
            text_parts.extend([meta_desc] * 3)  # Weight meta description 3x
        
        # Headings (medium-high weight)
        headings = parsed_data.get('headings', {})
        for level, heading_list in headings.items():
            weight = 4 if level == 'h1' else 3 if level == 'h2' else 2
            for heading in heading_list:
                text_parts.extend([heading] * weight)
        
        # Alt text (medium weight)
        images = parsed_data.get('images', [])
        for img in images:
            alt_text = img.get('alt', '')
            if alt_text:
                text_parts.extend([alt_text] * 2)
        
        # Main content (normal weight)
        main_content = parsed_data.get('text_content', '')
        if main_content:
            text_parts.append(main_content)
        
        return ' '.join(text_parts)
    
    def _basic_keyword_analysis(self, text):
        """Basic keyword frequency analysis"""
        keywords = utils.extract_keywords_from_text(text)
        keyword_counts = Counter(keywords)
        
        # Filter by minimum frequency
        filtered_keywords = {
            word: count for word, count in keyword_counts.items()
            if count >= config.MIN_KEYWORD_FREQUENCY
        }
        
        return dict(keyword_counts.most_common(config.TOP_KEYWORDS_COUNT))
    
    def _tfidf_analysis(self, text):
        """TF-IDF based keyword analysis"""
        try:
            # Split text into sentences for TF-IDF
            sentences = sent_tokenize(text)
            if len(sentences) < 2:
                sentences = [text]
            
            # Create TF-IDF vectorizer
            vectorizer = TfidfVectorizer(
                max_features=config.TOP_KEYWORDS_COUNT,
                stop_words='english',
                ngram_range=(1, 2),
                min_df=1,
                max_df=0.8
            )
            
            tfidf_matrix = vectorizer.fit_transform(sentences)
            feature_names = vectorizer.get_feature_names_out()
            
            # Calculate mean TF-IDF scores
            mean_scores = np.mean(tfidf_matrix.toarray(), axis=0)
            
            # Create keyword-score pairs
            tfidf_keywords = {}
            for i, score in enumerate(mean_scores):
                if score > 0:
                    tfidf_keywords[feature_names[i]] = float(score)
            
            # Sort by score
            return dict(sorted(tfidf_keywords.items(), key=lambda x: x[1], reverse=True))
            
        except Exception as e:
            self.logger.warning(f"TF-IDF analysis failed: {e}")
            return {}
    
    def _ngram_analysis(self, text):
        """N-gram analysis for phrase detection"""
        try:
            # Analyze 2-grams and 3-grams
            ngram_results = {}
            
            for n in [2, 3]:
                vectorizer = CountVectorizer(
                    ngram_range=(n, n),
                    stop_words='english',
                    min_df=2,
                    max_features=20
                )
                
                ngram_matrix = vectorizer.fit_transform([text])
                feature_names = vectorizer.get_feature_names_out()
                counts = ngram_matrix.toarray()[0]
                
                ngram_dict = {}
                for i, count in enumerate(counts):
                    if count > 0:
                        ngram_dict[feature_names[i]] = int(count)
                
                ngram_results[f'{n}_grams'] = dict(
                    sorted(ngram_dict.items(), key=lambda x: x[1], reverse=True)
                )
            
            return ngram_results
            
        except Exception as e:
            self.logger.warning(f"N-gram analysis failed: {e}")
            return {}
    
    def _analyze_headings(self, headings):
        """Analyze keywords in headings"""
        heading_keywords = Counter()
        
        for level, heading_list in headings.items():
            weight = 3 if level == 'h1' else 2 if level == 'h2' else 1
            
            for heading in heading_list:
                keywords = utils.extract_keywords_from_text(heading)
                for keyword in keywords:
                    heading_keywords[keyword] += weight
        
        return dict(heading_keywords.most_common(20))
    
    def _analyze_meta_content(self, parsed_data):
        """Analyze meta tags for keywords"""
        meta_keywords = Counter()
        
        # Meta keywords tag
        meta_kw = parsed_data.get('meta_keywords', '')
        if meta_kw:
            keywords = [kw.strip() for kw in meta_kw.split(',')]
            for keyword in keywords:
                if keyword:
                    meta_keywords[keyword.lower()] += 3
        
        # Meta description
        meta_desc = parsed_data.get('meta_description', '')
        if meta_desc:
            keywords = utils.extract_keywords_from_text(meta_desc)
            for keyword in keywords:
                meta_keywords[keyword] += 2
        
        return dict(meta_keywords.most_common(15))
    
    def _calculate_content_stats(self, text):
        """Calculate content statistics"""
        try:
            stats = {
                'word_count': len(text.split()),
                'character_count': len(text),
                'sentence_count': len(sent_tokenize(text)),
                'paragraph_count': len([p for p in text.split('\n\n') if p.strip()]),
                'reading_level': textstat.flesch_reading_ease(text),
                'avg_words_per_sentence': 0,
                'avg_sentence_length': 0
            }
            
            if stats['sentence_count'] > 0:
                stats['avg_words_per_sentence'] = stats['word_count'] / stats['sentence_count']
                stats['avg_sentence_length'] = stats['character_count'] / stats['sentence_count']
            
            return stats
            
        except Exception as e:
            self.logger.warning(f"Content stats calculation failed: {e}")
            return {}
    
    def _calculate_keyword_density(self, text):
        """Calculate keyword density for top keywords"""
        words = text.lower().split()
        total_words = len(words)
        
        if total_words == 0:
            return {}
        
        word_counts = Counter(words)
        keyword_density = {}
        
        for word, count in word_counts.most_common(20):
            if (len(word) >= config.MIN_KEYWORD_LENGTH and 
                word not in self.stop_words):
                density = (count / total_words) * 100
                keyword_density[word] = round(density, 2)
        
        return keyword_density
    
    def _get_primary_keywords(self, analysis_results):
        """Determine primary keywords from all analyses"""
        keyword_scores = defaultdict(float)
        
        # Weight different analysis types
        weights = {
            'basic_keywords': 1.0,
            'tfidf_keywords': 2.0,
            'heading_keywords': 1.5,
            'meta_keywords': 1.8
        }
        
        for analysis_type, weight in weights.items():
            keywords = analysis_results.get(analysis_type, {})
            for keyword, score in keywords.items():
                keyword_scores[keyword] += score * weight
        
        # Sort and return top keywords
        sorted_keywords = sorted(
            keyword_scores.items(), 
            key=lambda x: x[1], 
            reverse=True
        )
        
        return [kw for kw, score in sorted_keywords[:config.TOP_KEYWORDS_COUNT]]
    
    def _get_secondary_keywords(self, analysis_results):
        """Determine secondary keywords"""
        all_keywords = set()
        
        # Collect keywords from various analyses
        for analysis_type in ['basic_keywords', 'tfidf_keywords', 'heading_keywords']:
            keywords = analysis_results.get(analysis_type, {})
            all_keywords.update(keywords.keys())
        
        # Remove primary keywords
        primary_keywords = set(analysis_results.get('primary_keywords', []))
        secondary_keywords = all_keywords - primary_keywords
        
        return list(secondary_keywords)[:config.SECONDARY_KEYWORDS_COUNT]
    
    def _empty_analysis(self):
        """Return empty analysis structure"""
        return {
            'basic_keywords': {},
            'tfidf_keywords': {},
            'ngram_analysis': {},
            'heading_keywords': {},
            'meta_keywords': {},
            'content_stats': {},
            'keyword_density': {},
            'primary_keywords': [],
            'secondary_keywords': []
        }
