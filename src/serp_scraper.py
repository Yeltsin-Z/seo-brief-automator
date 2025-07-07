import time
import logging
from typing import List, Dict, Any
from bs4 import BeautifulSoup
import requests
from serpapi import GoogleSearch
from config.config import Config
from src.utils import Utils

logger = logging.getLogger(__name__)

class SERPScraper:
    """Scrapes Google SERP results for a given keyword using SerpAPI"""
    
    def __init__(self):
        self.api_key = "6ac9cbc80ee7f65c249cf87b0abfb6c2ad19bd2cc9a9f75fa67f96aad673d53e"
    
    def search_google(self, keyword: str) -> List[Dict[str, Any]]:
        """Search Google for the keyword and extract top results using SerpAPI"""
        try:
            params = {
                "engine": "google",
                "q": keyword,
                "hl": "en",
                "gl": "us",
                "num": 10,
                "api_key": self.api_key
            }
            search = GoogleSearch(params)
            results = search.get_dict()
            serp_results = []
            for result in results.get("organic_results", []):
                serp_results.append({
                    "title": result.get("title"),
                    "url": result.get("link"),
                    "snippet": result.get("snippet"),
                    "domain": result.get("displayed_link")
                })
            logger.info(f"Found {len(serp_results)} search results from SerpAPI")
            return serp_results
        except Exception as e:
            logger.error(f"Error during Google search with SerpAPI: {e}")
            return []
    
    def scrape_article_content(self, url: str) -> Dict[str, Any]:
        """Scrape content from a specific article URL"""
        try:
            logger.info(f"Scraping content from: {url}")
            
            # Use requests for faster content scraping
            response = Utils.make_request(url)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract main content
            content = self.extract_main_content(soup)
            
            # Extract metadata
            metadata = self.extract_metadata(soup)
            
            return {
                "url": url,
                "content": content,
                "metadata": metadata,
                "word_count": len(content.split()),
                "scraped_at": time.strftime("%Y-%m-%d %H:%M:%S")
            }
            
        except Exception as e:
            logger.error(f"Error scraping article content from {url}: {e}")
            return {
                "url": url,
                "content": "",
                "metadata": {},
                "word_count": 0,
                "error": str(e)
            }
    
    def extract_main_content(self, soup: BeautifulSoup) -> str:
        """Extract main content from HTML"""
        # Remove script and style elements
        for script in soup(["script", "style", "nav", "header", "footer", "aside"]):
            script.decompose()
        
        # Try to find main content areas
        content_selectors = [
            "article",
            "main",
            ".content",
            ".post-content",
            ".entry-content",
            ".article-content",
            "#content",
            ".main-content"
        ]
        
        content = ""
        for selector in content_selectors:
            elements = soup.select(selector)
            if elements:
                content = " ".join([elem.get_text() for elem in elements])
                break
        
        # If no specific content area found, get body text
        if not content:
            content = soup.get_text()
        
        return Utils.clean_text(content)
    
    def extract_metadata(self, soup: BeautifulSoup) -> Dict[str, str]:
        """Extract metadata from HTML"""
        metadata = {}
        
        # Extract title
        title_tag = soup.find('title')
        if title_tag:
            metadata['title'] = title_tag.get_text().strip()
        
        # Extract meta description
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc:
            metadata['description'] = meta_desc.get('content', '').strip()
        
        # Extract meta keywords
        meta_keywords = soup.find('meta', attrs={'name': 'keywords'})
        if meta_keywords:
            metadata['keywords'] = meta_keywords.get('content', '').strip()
        
        # Extract author
        author_selectors = [
            'meta[name="author"]',
            '.author',
            '.byline',
            '[rel="author"]'
        ]
        
        for selector in author_selectors:
            author_elem = soup.select_one(selector)
            if author_elem:
                if author_elem.name == 'meta':
                    metadata['author'] = author_elem.get('content', '').strip()
                else:
                    metadata['author'] = author_elem.get_text().strip()
                break
        
        return metadata
    
    def scrape_top_articles(self, keyword: str) -> List[Dict[str, Any]]:
        """Main method to scrape top articles for a keyword"""
        try:
            # Get search results
            search_results = self.search_google(keyword)
            
            if not search_results:
                logger.warning("No search results found")
                return []
            
            # Scrape content from each result
            articles = []
            for result in search_results:
                article_data = self.scrape_article_content(result['url'])
                article_data.update(result)
                articles.append(article_data)
                
                # Add delay to be respectful
                time.sleep(1)
            
            logger.info(f"Successfully scraped {len(articles)} articles")
            return articles
            
        except Exception as e:
            logger.error(f"Error in scrape_top_articles: {e}")
            return []
