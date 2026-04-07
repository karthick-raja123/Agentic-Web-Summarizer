"""
Text cleaning and preprocessing utilities.
Ensures extracted content is clean, normalized, and deduplicated.
"""

import re
from typing import List
from bs4 import BeautifulSoup


def remove_scripts_and_styles(soup: BeautifulSoup) -> BeautifulSoup:
    """
    Remove script and style tags from parsed HTML.
    
    Args:
        soup: BeautifulSoup object
        
    Returns:
        Cleaned BeautifulSoup object
    """
    for tag in soup.find_all(["script", "style", "meta", "link", "noscript"]):
        tag.decompose()
    return soup


def extract_meaningful_paragraphs(text: str, min_length: int = 30) -> List[str]:
    """
    Extract meaningful paragraphs from text.
    Filters out short, non-informative pieces.
    
    Args:
        text: Raw text content
        min_length: Minimum characters for a paragraph to be considered meaningful
        
    Returns:
        List of meaningful paragraphs
    """
    paragraphs = text.split('\n')
    meaningful = []
    
    for para in paragraphs:
        cleaned = para.strip()
        # Remove sequences of whitespace
        cleaned = re.sub(r'\s+', ' ', cleaned)
        
        if len(cleaned) >= min_length and not cleaned.isdigit():
            meaningful.append(cleaned)
    
    return meaningful


def deduplicate_content(paragraphs: List[str], similarity_threshold: float = 0.85) -> List[str]:
    """
    Remove duplicate or very similar paragraphs.
    Uses simple similarity heuristic based on word overlap.
    
    Args:
        paragraphs: List of text paragraphs
        similarity_threshold: Threshold for considering paragraphs as duplicates
        
    Returns:
        Deduplicated list of paragraphs
    """
    if not paragraphs:
        return []
    
    unique = []
    seen_tokens = set()
    
    for para in paragraphs:
        # Get word tokens
        tokens = set(para.lower().split())
        
        # Check similarity with previously seen paragraphs
        is_duplicate = False
        for seen in seen_tokens:
            # Simple Jaccard similarity
            intersection = len(tokens & seen)
            union = len(tokens | seen)
            if union > 0:
                similarity = intersection / union
                if similarity >= similarity_threshold:
                    is_duplicate = True
                    break
        
        if not is_duplicate:
            unique.append(para)
            seen_tokens.add(frozenset(tokens))
    
    return unique


def chunk_text(text: str, chunk_size: int = 3000, overlap: int = 100) -> List[str]:
    """
    Split text into chunks for processing.
    Useful for managing token limits with LLM APIs.
    
    Args:
        text: Text to chunk
        chunk_size: Characters per chunk
        overlap: Characters to overlap between chunks
        
    Returns:
        List of text chunks
    """
    chunks = []
    start = 0
    
    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunks.append(text[start:end])
        start = end - overlap
        
        # Prevent infinite loop for very small texts
        if start == end - overlap and start >= len(text):
            break
    
    return chunks


def clean_content(html_text: str) -> str:
    """
    Complete pipeline: clean HTML, extract paragraphs, deduplicate.
    
    Args:
        html_text: Raw HTML text
        
    Returns:
        Clean, deduplicated content
    """
    # Parse HTML
    soup = BeautifulSoup(html_text, 'html.parser')
    
    # Remove scripts and styles
    soup = remove_scripts_and_styles(soup)
    
    # Extract text
    text = soup.get_text(separator='\n', strip=True)
    
    # Extract meaningful paragraphs
    paragraphs = extract_meaningful_paragraphs(text)
    
    # Deduplicate
    unique_paragraphs = deduplicate_content(paragraphs)
    
    # Join back
    return '\n'.join(unique_paragraphs)
