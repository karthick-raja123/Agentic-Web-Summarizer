"""
Advanced Web Scraping Module
Extracts clean, meaningful article content from URLs
Removes noise, validates quality, and prioritizes best sources
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import re
from typing import List, Dict, Tuple


class AdvancedScraper:
    """Professional web scraper that extracts article content"""
    
    # Tags to remove entirely (noise)
    NOISE_TAGS = [
        'script', 'style', 'nav', 'header', 'footer', 'aside',
        'button', 'noscript', 'meta', 'link', 'form', 'iframe'
    ]
    
    # Advertising class/id patterns
    AD_PATTERNS = [
        r'ad', r'advert', r'sponsor', r'promo', r'banner',
        r'sidebar', r'widget', r'popup', r'modal', r'share'
    ]
    
    # Content tags that we prioritize
    CONTENT_TAGS = ['article', 'main', 'section', 'div']
    
    # Minimum content threshold
    MIN_CONTENT_LENGTH = 300  # characters
    MIN_PARAGRAPH_LENGTH = 20  # characters
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def is_ad_or_noise_element(self, element) -> bool:
        """Check if element is ad or noise based on class/id"""
        class_attr = element.get('class', [])
        id_attr = element.get('id', '')
        
        combined = f"{' '.join(class_attr)} {id_attr}".lower()
        
        for pattern in self.AD_PATTERNS:
            if re.search(pattern, combined, re.IGNORECASE):
                return True
        return False
    
    def extract_article_content(self, soup: BeautifulSoup) -> str:
        """
        Extract meaningful article content from HTML
        
        Strategy:
        1. Remove all noise tags and ad elements
        2. Look for article/main/section tags
        3. Extract paragraphs and text blocks
        4. Prioritize longer, meaningful content
        5. Clean and deduplicate
        
        Returns:
            Clean article text or empty string
        """
        
        # Create a copy to avoid modifying original
        soup_copy = BeautifulSoup(str(soup), 'html.parser')
        
        # Remove noise tags
        for tag in self.NOISE_TAGS:
            for element in soup_copy.find_all(tag):
                element.decompose()
        
        # Remove ad/promotional elements by class/id
        for element in soup_copy.find_all(['div', 'aside', 'section']):
            if self.is_ad_or_noise_element(element):
                element.decompose()
        
        # Try to find main content container
        main_content = self._find_main_content_container(soup_copy)
        
        if main_content is None:
            main_content = soup_copy
        
        # Extract paragraphs and text blocks
        content_blocks = self._extract_content_blocks(main_content)
        
        # Clean and combine
        clean_text = self._clean_and_combine_text(content_blocks)
        
        return clean_text
    
    def _find_main_content_container(self, soup: BeautifulSoup) -> BeautifulSoup:
        """Find the main content container"""
        
        # Priority order for content containers
        selectors = [
            'article',
            'main',
            'div.main-content',
            'div.content',
            'div.article',
            'div.post',
            'div.entry-content',
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element and len(element.get_text(strip=True)) > self.MIN_CONTENT_LENGTH:
                return element
        
        return None
    
    def _extract_content_blocks(self, container) -> List[str]:
        """Extract meaningful text blocks"""
        
        blocks = []
        seen = set()  # For deduplication
        
        # Extract from paragraphs (high priority)
        for p in container.find_all('p'):
            text = p.get_text(strip=True)
            if self._is_valid_paragraph(text):
                if text not in seen:
                    blocks.append(text)
                    seen.add(text)
        
        # Extract from headers (h2, h3)
        for h in container.find_all(['h2', 'h3', 'h4']):
            text = h.get_text(strip=True)
            if self._is_valid_paragraph(text):
                if text not in seen:
                    blocks.append(text)
                    seen.add(text)
        
        # Extract from divs with significant text
        for div in container.find_all('div', recursive=True):
            # Only get direct text, not children
            text = self._get_direct_text(div)
            if self._is_valid_paragraph(text) and len(text) > 100:
                if text not in seen:
                    blocks.append(text)
                    seen.add(text)
        
        # Sort by length (prioritize longer, more meaningful blocks)
        blocks.sort(key=len, reverse=True)
        
        return blocks[:20]  # Limit to top 20 content blocks
    
    def _get_direct_text(self, element) -> str:
        """Get only direct text of element, not children"""
        text_parts = []
        for child in element.children:
            if isinstance(child, str):
                text = child.strip()
                if text:
                    text_parts.append(text)
        return ' '.join(text_parts)
    
    def _is_valid_paragraph(self, text: str) -> bool:
        """Check if text is valid paragraph"""
        if not text:
            return False
        
        if len(text) < self.MIN_PARAGRAPH_LENGTH:
            return False
        
        # Exclude common noise patterns
        noise_patterns = [
            r'^(click|share|follow|subscribe|read more)$',
            r'^(home|about|contact|privacy)',
            r'^[0-9]+$',  # Just numbers
            r'^(ad|advertisement)',
        ]
        
        for pattern in noise_patterns:
            if re.match(pattern, text, re.IGNORECASE):
                return False
        
        return True
    
    def _clean_and_combine_text(self, blocks: List[str]) -> str:
        """Clean, deduplicate, and combine text blocks"""
        
        if not blocks:
            return ""
        
        # Remove duplicate lines
        seen = set()
        unique_blocks = []
        
        for block in blocks:
            # Normalize for comparison
            normalized = block.lower().strip()
            if normalized not in seen:
                unique_blocks.append(block)
                seen.add(normalized)
        
        # Join with double newline for readability
        combined = "\n\n".join(unique_blocks)
        
        # Additional cleaning
        # Remove excess whitespace
        combined = re.sub(r'\n\n\n+', '\n\n', combined)
        combined = re.sub(r'  +', ' ', combined)
        
        # Remove URLs (optional - comment out if you want URLs)
        combined = re.sub(r'http[s]?://\S+', '[URL]', combined)
        
        return combined.strip()
    
    def scrape_url(self, url: str, timeout: int = 10) -> Tuple[str, bool]:
        """
        Scrape a single URL and return (content, is_valid)
        
        Returns:
            Tuple of (cleaned_content, is_valid_content)
        """
        try:
            response = self.session.get(url, timeout=timeout)
            response.raise_for_status()
            
            # Decode properly
            response.encoding = response.apparent_encoding or 'utf-8'
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract article content
            content = self.extract_article_content(soup)
            
            # Validate content quality
            is_valid = len(content) >= self.MIN_CONTENT_LENGTH
            
            return content, is_valid
            
        except requests.Timeout:
            return "", False
        except requests.RequestException as e:
            return "", False
        except Exception as e:
            return "", False
    
    def scrape_urls(self, urls: List[str], max_sources: int = 2) -> Tuple[str, List[Dict]]:
        """
        Scrape multiple URLs and return best content + quality metrics
        
        Args:
            urls: List of URLs to scrape
            max_sources: Maximum number of sources to use (1-2 recommended)
        
        Returns:
            Tuple of (combined_content, source_metrics)
        """
        
        results = []
        
        # Scrape all URLs
        for url in urls:
            content, is_valid = self.scrape_url(url)
            
            quality_score = self._calculate_quality_score(content)
            
            results.append({
                'url': url,
                'content': content,
                'is_valid': is_valid,
                'length': len(content),
                'quality_score': quality_score
            })
        
        # Filter valid content
        valid_results = [r for r in results if r['is_valid']]
        
        if not valid_results:
            return "", results
        
        # Sort by quality score
        valid_results.sort(key=lambda x: x['quality_score'], reverse=True)
        
        # Select top sources
        best_sources = valid_results[:max_sources]
        
        # Combine content from best sources
        combined_content = "\n\n--- Source ---\n\n".join([
            r['content'] for r in best_sources
        ])
        
        return combined_content, results
    
    def _calculate_quality_score(self, content: str) -> float:
        """
        Calculate quality score for content (0-100)
        
        Factors:
        - Length (longer = better, up to 5000 chars)
        - Word count (better = more content)
        - Sentence count (better structure)
        """
        
        if not content:
            return 0.0
        
        length = len(content)
        word_count = len(content.split())
        sentence_count = len(re.split(r'[.!?]+', content))
        
        # Scoring
        length_score = min(length / 5000 * 40, 40)  # Max 40 points
        word_score = min(word_count / 100 * 30, 30)  # Max 30 points
        sentence_score = min(sentence_count / 20 * 30, 30)  # Max 30 points
        
        total_score = length_score + word_score + sentence_score
        
        return round(total_score, 2)


def create_improved_scraper() -> AdvancedScraper:
    """Factory function to create scraper instance"""
    return AdvancedScraper()
