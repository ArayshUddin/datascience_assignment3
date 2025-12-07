"""
Article Scraper Service
Extracts article data from URLs
"""
import re
import time
import requests
try:
    import cloudscraper
    CLOUDSCRAPER_AVAILABLE = True
except ImportError:
    CLOUDSCRAPER_AVAILABLE = False
    cloudscraper = None
from bs4 import BeautifulSoup
from typing import Dict, List, Optional
from urllib.parse import urlparse
from collections import Counter
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MediumScraper:
    """Scraper for articles"""
    
    def __init__(self):
        # Use cloudscraper if available (handles Cloudflare challenges)
        if CLOUDSCRAPER_AVAILABLE:
            logger.info("Using cloudscraper to bypass Cloudflare protection")
            self.session = cloudscraper.create_scraper(
                browser={
                    'browser': 'chrome',
                    'platform': 'windows',
                    'desktop': True
                }
            )
        else:
            logger.warning("cloudscraper not available, using requests (may get 403 errors)")
            self.session = requests.Session()
            # More realistic browser headers to avoid 403 errors
            self.session.headers.update({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Cache-Control': 'max-age=0'
            })
        # Disable SSL verification warnings for problematic certificates
        self.session.verify = True
    
    def scrape_article(self, url: str) -> Optional[Dict]:
        """
        Scrape a article and extract all required data
        
        Returns:
            Dictionary with article data or None if scraping fails
        """
        try:
            logger.info(f"Scraping article: {url}")
            
            # Add referer header for Medium articles
            headers = {}
            if 'medium.com' in url:
                headers['Referer'] = 'https://medium.com/'
            
            # Try with retries
            max_retries = 3
            response = None
            
            for attempt in range(max_retries):
                try:
                    # Add referer for Medium articles
                    if 'medium.com' in url and 'Referer' not in headers:
                        headers['Referer'] = 'https://medium.com/'
                    
                    response = self.session.get(url, timeout=30, headers=headers, allow_redirects=True)
                    
                    # Check if we got redirected to a login/block page
                    if response.status_code == 403:
                        logger.warning(f"403 Forbidden for {url} (attempt {attempt + 1}/{max_retries})")
                        if attempt < max_retries - 1:
                            # Exponential backoff
                            wait_time = (attempt + 1) * 3
                            time.sleep(wait_time)
                            
                            # Try different referers
                            if attempt == 1:
                                headers['Referer'] = 'https://www.google.com/'
                            elif attempt == 2:
                                headers['Referer'] = 'https://www.bing.com/'
                            continue
                        else:
                            logger.error(f"Failed to fetch {url} after {max_retries} attempts: 403 Forbidden")
                            return None
                    
                    if response.status_code == 200:
                        break
                    else:
                        response.raise_for_status()
                        
                except requests.exceptions.SSLError as ssl_error:
                    # For SSL errors, try without verification (less secure but works)
                    if attempt < max_retries - 1:
                        logger.warning(f"SSL error for {url}, retrying without verification...")
                        try:
                            response = requests.get(url, timeout=30, headers=headers, verify=False, allow_redirects=True)
                            if response.status_code == 200:
                                break
                        except:
                            pass
                    if attempt == max_retries - 1:
                        logger.error(f"SSL error for {url}: {str(ssl_error)}")
                        return None
                    time.sleep(2)
                    continue
                except requests.exceptions.RequestException as req_error:
                    if attempt < max_retries - 1:
                        logger.warning(f"Request error for {url} (attempt {attempt + 1}): {str(req_error)}")
                        time.sleep((attempt + 1) * 2)
                        continue
                    else:
                        logger.error(f"Request error for {url}: {str(req_error)}")
                        return None
            
            if not response or response.status_code != 200:
                logger.error(f"Failed to fetch {url}: Status {response.status_code if response else 'No response'}")
                return None
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract title
            title = self._extract_title(soup)
            
            # Extract subtitle
            subtitle = self._extract_subtitle(soup)
            
            # Extract text content
            text = self._extract_text(soup)
            
            # Extract images
            images = self._extract_images(soup)
            num_images = len(images)
            
            # Extract external links
            external_links = self._extract_external_links(soup, url)
            num_external_links = len(external_links)
            
            # Extract author information
            author_name, author_url = self._extract_author(soup)
            
            # Extract claps
            claps = self._extract_claps(soup)
            
            # Extract reading time
            reading_time = self._extract_reading_time(soup)
            
            # Extract keywords
            keywords = self._extract_keywords(soup, text)
            
            return {
                'url': url,
                'title': title,
                'subtitle': subtitle,
                'text': text,
                'num_images': num_images,
                'image_urls': '|'.join(images) if images else '',
                'num_external_links': num_external_links,
                'external_links': '|'.join(external_links) if external_links else '',
                'author_name': author_name,
                'author_url': author_url,
                'claps': claps,
                'reading_time': reading_time,
                'keywords': '|'.join(keywords) if keywords else ''
            }
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 403:
                logger.warning(f"403 Forbidden: {url} - Medium is blocking requests. This is normal for automated scraping.")
            elif e.response.status_code == 404:
                logger.warning(f"404 Not Found: {url} - Article may have been deleted or moved.")
            else:
                logger.error(f"HTTP Error {e.response.status_code} scraping {url}: {str(e)}")
            return None
        except requests.exceptions.SSLError as e:
            logger.warning(f"SSL Error scraping {url}: {str(e)}")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error scraping {url}: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error scraping {url}: {str(e)}")
            return None
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract article title"""
        # Try multiple selectors for title
        selectors = [
            'h1',
            'h1[data-testid="storyTitle"]',
            'h1.pw-post-title',
            'article h1',
            'meta[property="og:title"]'
        ]
        
        for selector in selectors:
            if selector.startswith('meta'):
                element = soup.select_one(selector)
                if element and element.get('content'):
                    return element.get('content').strip()
            else:
                element = soup.select_one(selector)
                if element:
                    return element.get_text(strip=True)
        
        return ''
    
    def _extract_subtitle(self, soup: BeautifulSoup) -> str:
        """Extract article subtitle"""
        selectors = [
            'h2[data-testid="storySubtitle"]',
            'h2.pw-subtitle-paragraph',
            'h2[data-selectable-paragraph]',
            'article h2:first-of-type',
            'meta[property="og:description"]'
        ]
        
        for selector in selectors:
            if selector.startswith('meta'):
                element = soup.select_one(selector)
                if element and element.get('content'):
                    return element.get('content').strip()
            else:
                element = soup.select_one(selector)
                if element:
                    text = element.get_text(strip=True)
                    if text:
                        return text
        
        return ''
    
    def _extract_text(self, soup: BeautifulSoup) -> str:
        """Extract main article text"""
        # Remove script and style elements
        for script in soup(["script", "style", "nav", "header", "footer"]):
            script.decompose()
        
        # Try to find main content
        selectors = [
            'article section',
            'article',
            '[data-testid="storyBody"]',
            '.postArticle-content'
        ]
        
        text_parts = []
        for selector in selectors:
            content = soup.select_one(selector)
            if content:
                paragraphs = content.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
                for p in paragraphs:
                    text = p.get_text(strip=True)
                    if text and len(text) > 10:  # Filter out very short text
                        text_parts.append(text)
                if text_parts:
                    break
        
        return '\n\n'.join(text_parts)
    
    def _extract_images(self, soup: BeautifulSoup) -> List[str]:
        """Extract all image URLs from the article"""
        images = []
        
        # Find all img tags
        img_tags = soup.find_all('img')
        for img in img_tags:
            src = img.get('src') or img.get('data-src') or img.get('data-lazy-src')
            if src:
                # Clean up image URLs
                if 'medium.com' in src or 'miro.medium.com' in src:
                    # Remove size parameters to get original
                    src = re.sub(r'[?&]w=\d+', '', src)
                    src = re.sub(r'[?&]q=\d+', '', src)
                if src not in images:
                    images.append(src)
        
        # Also check for picture sources
        picture_tags = soup.find_all('picture')
        for picture in picture_tags:
            source = picture.find('source')
            if source and source.get('srcset'):
                srcset = source.get('srcset')
                # Extract first URL from srcset
                urls = re.findall(r'https?://[^\s,]+', srcset)
                if urls:
                    url = urls[0]
                    url = re.sub(r'[?&]w=\d+', '', url)
                    url = re.sub(r'[?&]q=\d+', '', url)
                    if url not in images:
                        images.append(url)
        
        return images
    
    def _extract_external_links(self, soup: BeautifulSoup, base_url: str) -> List[str]:
        """Extract external links (not internal links)"""
        external_links = []
        base_domain = urlparse(base_url).netloc
        
        links = soup.find_all('a', href=True)
        for link in links:
            href = link.get('href', '')
            if not href:
                continue
            
            # Make absolute URL
            if href.startswith('/'):
                href = f"https://{base_domain}{href}"
            elif not href.startswith('http'):
                continue
            
            # Check if external
            link_domain = urlparse(href).netloc
            if link_domain and link_domain != base_domain and 'medium.com' not in link_domain:
                if href not in external_links:
                    external_links.append(href)
        
        return external_links
    
    def _extract_author(self, soup: BeautifulSoup) -> tuple:
        """Extract author name and URL"""
        author_name = ''
        author_url = ''
        
        # Try multiple selectors
        author_selectors = [
            'a[data-action="show-user-card"]',
            'a[rel="author"]',
            '.author',
            'meta[name="author"]',
            'meta[property="article:author"]'
        ]
        
        for selector in author_selectors:
            if selector.startswith('meta'):
                element = soup.select_one(selector)
                if element:
                    author_name = element.get('content', '').strip()
                    if author_name:
                        break
            else:
                element = soup.select_one(selector)
                if element:
                    author_name = element.get_text(strip=True)
                    author_url = element.get('href', '')
                    if author_url and not author_url.startswith('http'):
                        author_url = f"https://medium.com{author_url}"
                    if author_name:
                        break
        
        # Fallback: try to find in meta tags
        if not author_name:
            meta_author = soup.find('meta', {'name': 'author'})
            if meta_author:
                author_name = meta_author.get('content', '').strip()
        
        return author_name, author_url
    
    def _extract_claps(self, soup: BeautifulSoup) -> int:
        """Extract number of claps"""
        claps = 0
        
        # Try to find clap button or count
        clap_selectors = [
            'button[data-testid="clap-button"]',
            '[data-testid="clapCount"]',
            '.clapCount',
            'button[aria-label*="clap"]'
        ]
        
        for selector in clap_selectors:
            element = soup.select_one(selector)
            if element:
                # Try to get from aria-label or text
                aria_label = element.get('aria-label', '')
                if aria_label:
                    numbers = re.findall(r'\d+', aria_label)
                    if numbers:
                        try:
                            claps = int(numbers[0])
                            break
                        except:
                            pass
                
                text = element.get_text(strip=True)
                if text:
                    numbers = re.findall(r'\d+', text)
                    if numbers:
                        try:
                            claps = int(numbers[0])
                            break
                        except:
                            pass
        
        # Try to find in JSON-LD structured data
        json_scripts = soup.find_all('script', type='application/ld+json')
        for script in json_scripts:
            try:
                import json
                data = json.loads(script.string)
                if isinstance(data, dict):
                    if 'interactionStatistic' in data:
                        for stat in data.get('interactionStatistic', []):
                            if stat.get('interactionType', {}).get('@type') == 'LikeAction':
                                claps = stat.get('userInteractionCount', 0)
                                break
            except:
                pass
        
        return claps
    
    def _extract_reading_time(self, soup: BeautifulSoup) -> str:
        """Extract reading time"""
        reading_time = ''
        
        # Try to find reading time element
        selectors = [
            '[data-testid="storyReadingTime"]',
            '.readingTime',
            'span[title*="min read"]',
            'span[title*="read"]'
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                reading_time = element.get_text(strip=True)
                if reading_time:
                    break
        
        # Try to extract from title attribute
        if not reading_time:
            time_elements = soup.find_all(attrs={'title': re.compile(r'min.*read|read.*min', re.I)})
            if time_elements:
                reading_time = time_elements[0].get('title', '').strip()
        
        return reading_time
    
    def _extract_keywords(self, soup: BeautifulSoup, text: str) -> List[str]:
        """Extract keywords from meta tags and text analysis"""
        keywords = []
        
        # Get keywords from meta tags
        meta_keywords = soup.find('meta', {'name': 'keywords'})
        if meta_keywords and meta_keywords.get('content'):
            keywords.extend([k.strip() for k in meta_keywords.get('content').split(',')])
        
        # Get tags from article
        tag_selectors = [
            'a[href*="/tag/"]',
            '.tags a',
            '[data-testid="tag"]'
        ]
        
        for selector in tag_selectors:
            tags = soup.select(selector)
            for tag in tags:
                tag_text = tag.get_text(strip=True)
                if tag_text and tag_text not in keywords:
                    keywords.append(tag_text)
        
        # Simple keyword extraction from text (most common words)
        if text:
            words = re.findall(r'\b[a-z]{4,}\b', text.lower())
            common_words = Counter(words).most_common(10)
            # Filter out common stop words
            stop_words = {'that', 'this', 'with', 'from', 'have', 'will', 'your', 'they', 'what', 'when', 'where', 'which', 'there', 'their', 'these', 'those', 'about', 'after', 'before', 'could', 'should', 'would'}
            for word, count in common_words:
                if word not in stop_words and word not in keywords and len(keywords) < 15:
                    keywords.append(word)
        
        return keywords[:15]  # Limit to 15 keywords
    
    def scrape_multiple(self, urls: List[str], delay: float = 1.0, progress_callback=None, job_id: str = None) -> List[Dict]:
        """
        Scrape multiple articles with delay between requests
        
        Args:
            urls: List of article URLs
            delay: Delay in seconds between requests
            progress_callback: Optional callback function(successful, url)
            job_id: Optional job ID for progress tracking
        
        Returns:
            List of scraped article data
        """
        from services.progress_tracker import progress_tracker
        
        results = []
        total = len(urls)
        
        for i, url in enumerate(urls, 1):
            logger.info(f"Scraping {i}/{total}: {url}")
            
            # Set current URL in progress tracker
            if job_id:
                progress_tracker.set_current_url(job_id, url)
            
            article_data = self.scrape_article(url)
            success = article_data is not None
            if article_data:
                results.append(article_data)
            
            # Call progress callback if provided
            if progress_callback:
                progress_callback(success, url)
            
            # Update progress tracker with URL
            if job_id:
                progress_tracker.update_progress(job_id, success, url)
            
            # Delay between requests to be respectful
            if i < total:
                time.sleep(delay)
        
        return results

