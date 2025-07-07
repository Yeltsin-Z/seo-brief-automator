import time
import logging
from typing import List, Dict, Any
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import requests

from config.config import Config
from src.utils import Utils

logger = logging.getLogger(__name__)

class SERPScraper:
    """Scrapes Google SERP results for a given keyword"""
    
    def __init__(self):
        self.driver = None
        self.setup_driver()
    
    def setup_driver(self):
        """Setup Chrome WebDriver with appropriate options"""
        try:
            chrome_options = Options()
            chrome_options.add_argument("--headless=new")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            chrome_options.add_argument(f"--user-agent={user_agent}")
            chrome_options.add_argument("--disable-images")
            # Use /usr/bin/chromium and /usr/bin/chromedriver for Render
            chrome_options.binary_location = "/usr/bin/chromium"
            driver_path = "/usr/bin/chromedriver"
            logger.info(f"Using ChromeDriver at: {driver_path}")
            service = Service(driver_path)
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            self.driver.set_page_load_timeout(Config.SELENIUM_TIMEOUT)
        except Exception as e:
            logger.error(f"Failed to setup Chrome driver: {e}")
            raise
    
    def search_google(self, keyword: str) -> List[Dict[str, Any]]:
        """Search Google for the keyword and extract top results"""
        try:
            # Construct Google search URL with US locale
            search_url = f"https://www.google.com/search?q={keyword.replace(' ', '+')}&num={Config.SERP_RESULTS_COUNT}&hl=en&gl=US"
            
            logger.info(f"Searching Google for: {keyword}")
            self.driver.get(search_url)
            
            # Wait for search results to load with longer timeout
            try:
                WebDriverWait(self.driver, 15).until(
                    EC.presence_of_element_located((By.ID, "search"))
                )
            except TimeoutException:
                # Try alternative selectors
                try:
                    WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "div#rso"))
                    )
                except TimeoutException:
                    logger.error("Timeout waiting for search results to load")
                    return []
            
            # Additional wait for dynamic content
            time.sleep(2)
            
            # Extract search results
            results = self.extract_search_results()
            
            logger.info(f"Found {len(results)} search results")
            return results
            
        except TimeoutException:
            logger.error("Timeout waiting for search results to load")
            return []
        except Exception as e:
            logger.error(f"Error during Google search: {e}")
            return []
    
    def extract_search_results(self) -> List[Dict[str, Any]]:
        """Extract search results from Google SERP"""
        results = []
        
        try:
            # Try multiple selectors for search results
            selectors = [
                "div.g",
                "div[data-sokoban-container]",
                "div.tF2Cxc",
                "div.yuRUbf",
                "div.rc",
                "div[jscontroller]"
            ]
            
            search_results = []
            for selector in selectors:
                search_results = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if search_results:
                    logger.info(f"Found {len(search_results)} results using selector: {selector}")
                    break
            
            if not search_results:
                # Try a more general approach
                search_results = self.driver.find_elements(By.CSS_SELECTOR, "div")
                search_results = [r for r in search_results if r.get_attribute("data-sokoban-container") or 
                                r.find_elements(By.CSS_SELECTOR, "h3, a[href*='http']")]
                logger.info(f"Found {len(search_results)} results using general selector")
            
            if not search_results:
                logger.warning("No search results found with any selector")
                return []
            
            for i, result in enumerate(search_results[:Config.SERP_RESULTS_COUNT]):
                try:
                    result_data = self.extract_single_result(result, i + 1)
                    if result_data:
                        results.append(result_data)
                except Exception as e:
                    logger.warning(f"Error extracting single result: {e}")
                    continue
            
        except Exception as e:
            logger.error(f"Error extracting search results: {e}")
        
        return results
    
    def extract_single_result(self, result_element, position: int) -> Dict[str, Any]:
        """Extract data from a single search result"""
        try:
            # Try multiple selectors for title
            title_selectors = ["h3", "h3.LC20lb", "h3.DK0T8d"]
            title = ""
            for selector in title_selectors:
                try:
                    title_element = result_element.find_element(By.CSS_SELECTOR, selector)
                    title = title_element.text.strip()
                    if title:
                        break
                except NoSuchElementException:
                    continue
            
            # Try multiple selectors for link
            link_selectors = ["a", "a[href]", "a[ping]"]
            url = ""
            for selector in link_selectors:
                try:
                    link_element = result_element.find_element(By.CSS_SELECTOR, selector)
                    url = link_element.get_attribute("href")
                    if url and url.startswith("http"):
                        break
                except NoSuchElementException:
                    continue
            
            # Extract snippet with multiple selectors
            snippet = ""
            snippet_selectors = ["div.VwiC3b", "div.s3v9rd", "span.aCOpRe", "div.IsZvec"]
            for selector in snippet_selectors:
                try:
                    snippet_element = result_element.find_element(By.CSS_SELECTOR, selector)
                    snippet = snippet_element.text.strip()
                    if snippet:
                        break
                except NoSuchElementException:
                    continue
            
            # Extract domain
            domain = Utils.extract_domain(url) if url else ""
            
            # Only return if we have at least title and URL
            if title and url:
                return {
                    "title": title,
                    "url": url,
                    "snippet": snippet,
                    "domain": domain,
                    "position": position
                }
            else:
                logger.warning(f"Incomplete result data: title='{title}', url='{url}'")
                return None
            
        except Exception as e:
            logger.warning(f"Error extracting result data: {e}")
            return None
    
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
    
    def fallback_serp_search(self, keyword: str) -> List[Dict[str, Any]]:
        """Fallback method using requests to get SERP results"""
        try:
            logger.info(f"Using fallback method for keyword: {keyword}")
            
            # Use a simple search approach
            search_url = f"https://www.google.com/search?q={keyword.replace(' ', '+')}&num=10&hl=en&gl=US"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            }
            
            response = requests.get(search_url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            results = []
            # Look for search result links
            links = soup.find_all('a', href=True)
            
            for i, link in enumerate(links):
                href = link.get('href', '')
                if href.startswith('/url?q='):
                    # Extract actual URL
                    url = href.split('/url?q=')[1].split('&')[0]
                    if url.startswith('http') and 'google.com' not in url:
                        title = link.get_text().strip()
                        if title and len(title) > 10:  # Filter out short/nonsense titles
                            results.append({
                                'title': title,
                                'url': url,
                                'snippet': '',
                                'domain': Utils.extract_domain(url),
                                'position': len(results) + 1
                            })
                            if len(results) >= 10:
                                break
            
            logger.info(f"Fallback method found {len(results)} results")
            return results
            
        except Exception as e:
            logger.error(f"Error in fallback SERP search: {e}")
            return []

    def scrape_top_articles(self, keyword: str) -> List[Dict[str, Any]]:
        """Main method to scrape top articles for a keyword"""
        try:
            # Get search results
            search_results = self.search_google(keyword)
            
            # If Selenium fails, try fallback method
            if not search_results:
                logger.info("Selenium method failed, trying fallback method...")
                search_results = self.fallback_serp_search(keyword)
            
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
    
    def close(self):
        """Close the WebDriver"""
        if self.driver:
            self.driver.quit()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
