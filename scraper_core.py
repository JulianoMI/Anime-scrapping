#!/usr/bin/env python3
"""
Anime Scraper Core Module
Pure Python web scraping logic for meownime.ltd
"""

import requests
from bs4 import BeautifulSoup
import json
from urllib.parse import urljoin, urlparse
import time
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AnimeScraper:
    """
    Pure Python anime scraper class for meownime.ltd
    Demonstrates object-oriented programming and web scraping concepts
    """
    
    def __init__(self):
        """Initialize the anime scraper with session and headers"""
        self.base_url = "https://meownime.ltd"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
        self.cache = {}
        
    def get_page(self, url, use_cache=True):
        """
        Fetch page content with error handling and caching
        
        Args:
            url (str): URL to fetch
            use_cache (bool): Whether to use cached content
            
        Returns:
            str: HTML content or None if error
        """
        if use_cache and url in self.cache:
            logger.info(f"Using cached content for {url}")
            return self.cache[url]
            
        try:
            logger.info(f"Fetching: {url}")
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            
            # Cache the content
            self.cache[url] = response.text
            logger.info(f"Successfully fetched and cached {url}")
            return response.text
            
        except requests.RequestException as e:
            logger.error(f"Error fetching {url}: {e}")
            return None
    
    def extract_anime_links(self, soup):
        """
        Extract anime links from BeautifulSoup object
        
        Args:
            soup (BeautifulSoup): Parsed HTML
            
        Returns:
            list: List of anime dictionaries with title and url
        """
        anime_list = []
        links = soup.find_all('a', href=True)
        
        for link in links:
            href = link.get('href', '')
            title = link.get_text(strip=True)
            
            # More flexible filtering for anime links
            if (('sub-indo' in href.lower() or 'subtitle-indonesia' in href.lower()) 
                and title and len(title) > 3 
                and 'meownime.ltd' in href
                and not any(skip in href.lower() for skip in ['facebook', 'faq', 'genre', 'jadwal', 'anime-list'])):
                
                # Don't over-clean the title, just basic cleanup
                title = title.strip()
                if title and len(title) > 2:  # Keep original titles
                    anime_list.append({
                        "title": title,
                        "url": href
                    })
        
        return anime_list
    
    def clean_title(self, title):
        """
        Clean anime title by removing unwanted characters and text
        
        Args:
            title (str): Raw title
            
        Returns:
            str: Cleaned title
        """
        # Remove common unwanted patterns
        unwanted_patterns = [
            'Sub Indo', 'Subtitle Indonesia', 'Episode', 'Batch',
            'Download', 'Streaming', 'Watch', 'Online'
        ]
        
        cleaned = title.strip()
        
        # Remove unwanted patterns (case insensitive)
        for pattern in unwanted_patterns:
            cleaned = cleaned.replace(pattern, '').replace(pattern.lower(), '')
        
        # Remove extra whitespace
        cleaned = ' '.join(cleaned.split())
        
        return cleaned if len(cleaned) > 2 else title.strip()
    
    def categorize_anime(self, anime_list):
        """
        Categorize anime into ongoing, completed, and movies
        
        Args:
            anime_list (list): List of anime dictionaries
            
        Returns:
            dict: Categorized anime data
        """
        data = {
            "ongoing": [],
            "completed": [],
            "movies": []
        }
        
        for anime in anime_list:
            title_lower = anime['title'].lower()
            url_lower = anime['url'].lower()
            
            # Improved categorization logic
            if 'movie' in title_lower or 'movie' in url_lower or 'film' in url_lower:
                data["movies"].append(anime)
            elif any(keyword in title_lower for keyword in ['season 2', 'season 3', 'season 4', 's2', 's3', 's4', 'part 2', 'part 3']):
                data["ongoing"].append(anime)
            elif any(keyword in title_lower for keyword in ['2025', '2024', 'ongoing', 'airing']):
                data["ongoing"].append(anime)
            else:
                data["completed"].append(anime)
        
        return data
    
    def remove_duplicates(self, anime_list):
        """
        Remove duplicate anime entries
        
        Args:
            anime_list (list): List of anime dictionaries
            
        Returns:
            list: List without duplicates
        """
        seen = set()
        unique_anime = []
        
        for anime in anime_list:
            title_key = anime['title'].lower().strip()
            if title_key not in seen and len(title_key) > 2:
                seen.add(title_key)
                unique_anime.append(anime)
        
        return unique_anime
    
    def scrape_home_page(self):
        """
        Scrape the home page for anime categories
        
        Returns:
            dict: Categorized anime data
        """
        logger.info("Scraping home page...")
        html = self.get_page(self.base_url)
        if not html:
            return {"ongoing": [], "completed": [], "movies": []}
        
        soup = BeautifulSoup(html, 'html.parser')
        anime_list = self.extract_anime_links(soup)
        anime_list = self.remove_duplicates(anime_list)
        
        # Categorize anime
        categorized_data = self.categorize_anime(anime_list)
        
        # Limit results for better performance
        for category in categorized_data:
            categorized_data[category] = categorized_data[category][:20]
        
        logger.info(f"Found {len(anime_list)} unique anime entries")
        return categorized_data
    
    def scrape_anime_list(self, letter=None):
        """
        Scrape the complete anime list
        
        Args:
            letter (str): Filter by starting letter
            
        Returns:
            list: List of anime dictionaries
        """
        logger.info(f"Scraping anime list (letter: {letter or 'all'})")
        url = f"{self.base_url}/anime-list-baru"
        html = self.get_page(url)
        if not html:
            return []
        
        soup = BeautifulSoup(html, 'html.parser')
        anime_list = self.extract_anime_links(soup)
        anime_list = self.remove_duplicates(anime_list)
        
        # Filter by letter if specified
        if letter:
            anime_list = [
                anime for anime in anime_list 
                if anime['title'].lower().startswith(letter.lower())
            ]
        
        # Sort alphabetically
        anime_list.sort(key=lambda x: x['title'].lower())
        
        logger.info(f"Found {len(anime_list)} anime entries")
        return anime_list
    
    def scrape_anime_details(self, anime_url):
        """
        Scrape detailed information about a specific anime
        
        Args:
            anime_url (str): URL of the anime page
            
        Returns:
            dict: Detailed anime information
        """
        logger.info(f"Scraping anime details for: {anime_url}")
        html = self.get_page(anime_url)
        if not html:
            return None
        
        soup = BeautifulSoup(html, 'html.parser')
        
        # Extract title
        title_selectors = ['h1', '.entry-title', '.post-title', 'title']
        title = "Unknown Title"
        
        for selector in title_selectors:
            title_element = soup.find(selector)
            if title_element:
                title = title_element.get_text(strip=True)
                title = self.clean_title(title)
                break
        
        # Extract synopsis
        synopsis = self.extract_synopsis(soup)
        
        # Extract download links
        download_links = self.extract_download_links(soup)
        
        # Extract additional metadata
        metadata = self.extract_metadata(soup)
        
        return {
            "title": title,
            "synopsis": synopsis,
            "download_links": download_links,
            "metadata": metadata,
            "url": anime_url
        }
    
    def extract_synopsis(self, soup):
        """
        Extract synopsis from anime page
        
        Args:
            soup (BeautifulSoup): Parsed HTML
            
        Returns:
            str: Synopsis text
        """
        synopsis_selectors = [
            '.entry-content p',
            '.post-content p',
            '.content p',
            'p'
        ]
        
        synopsis_parts = []
        
        for selector in synopsis_selectors:
            elements = soup.select(selector)
            if elements:
                for p in elements[:3]:  # Take first 3 paragraphs
                    text = p.get_text(strip=True)
                    # Filter out short or irrelevant text
                    if len(text) > 30 and not any(word in text.lower() for word in ['download', 'link', 'episode']):
                        synopsis_parts.append(text)
                
                if synopsis_parts:
                    break
        
        synopsis = ' '.join(synopsis_parts)
        return synopsis[:500] + "..." if len(synopsis) > 500 else synopsis
    
    def extract_download_links(self, soup):
        """
        Extract download links from anime page
        
        Args:
            soup (BeautifulSoup): Parsed HTML
            
        Returns:
            list: List of download link dictionaries
        """
        download_links = []
        links = soup.find_all('a', href=True)
        
        # Known download domains
        download_domains = [
            'drive.google.com', 'mega.nz', 'mediafire.com', 
            'zippyshare.com', 'solidfiles.com', 'uptobox.com'
        ]
        
        for link in links:
            href = link.get('href', '')
            text = link.get_text(strip=True)
            
            if any(domain in href for domain in download_domains):
                download_links.append({
                    "text": text[:100],  # Limit text length
                    "url": href,
                    "type": self.determine_link_type(href)
                })
        
        # Remove duplicates and limit
        seen_urls = set()
        unique_links = []
        for link in download_links:
            if link['url'] not in seen_urls:
                seen_urls.add(link['url'])
                unique_links.append(link)
        
        return unique_links[:10]  # Limit to 10 links
    
    def extract_metadata(self, soup):
        """
        Extract additional metadata from anime page
        
        Args:
            soup (BeautifulSoup): Parsed HTML
            
        Returns:
            dict: Metadata dictionary
        """
        metadata = {
            "genre": [],
            "year": None,
            "status": None,
            "episodes": None
        }
        
        # Try to extract genre information
        genre_selectors = ['.genre a', '.genres a', '[rel="tag"]']
        for selector in genre_selectors:
            genre_elements = soup.select(selector)
            if genre_elements:
                metadata["genre"] = [elem.get_text(strip=True) for elem in genre_elements[:5]]
                break
        
        # Try to extract year
        text_content = soup.get_text()
        import re
        year_match = re.search(r'\b(19|20)\d{2}\b', text_content)
        if year_match:
            metadata["year"] = year_match.group()
        
        return metadata
    
    def determine_link_type(self, url):
        """
        Determine the type of download link
        
        Args:
            url (str): Download URL
            
        Returns:
            str: Link type
        """
        url_lower = url.lower()
        
        if 'drive.google.com' in url_lower:
            return 'Google Drive'
        elif 'mega.nz' in url_lower:
            return 'MEGA'
        elif 'mediafire.com' in url_lower:
            return 'MediaFire'
        elif 'zippyshare.com' in url_lower:
            return 'ZippyShare'
        elif 'solidfiles.com' in url_lower:
            return 'SolidFiles'
        elif 'uptobox.com' in url_lower:
            return 'Uptobox'
        else:
            return 'Other'
    
    def search_anime(self, query):
        """
        Search for anime by title
        
        Args:
            query (str): Search query
            
        Returns:
            list: List of matching anime
        """
        logger.info(f"Searching for: {query}")
        
        # Get all anime first
        all_anime = self.scrape_anime_list()
        query_lower = query.lower().strip()
        
        if not query_lower:
            return []
        
        # Search in titles
        results = []
        for anime in all_anime:
            title_lower = anime['title'].lower()
            if query_lower in title_lower:
                results.append(anime)
        
        # Sort by relevance (exact matches first)
        results.sort(key=lambda x: (
            not x['title'].lower().startswith(query_lower),  # Starts with query first
            len(x['title'])  # Shorter titles first
        ))
        
        logger.info(f"Found {len(results)} matching anime")
        return results[:25]  # Limit to 25 results
    
    def get_statistics(self):
        """
        Get scraping statistics
        
        Returns:
            dict: Statistics about scraped data
        """
        home_data = self.scrape_home_page()
        all_anime = self.scrape_anime_list()
        
        return {
            "total_anime": len(all_anime),
            "ongoing_count": len(home_data["ongoing"]),
            "completed_count": len(home_data["completed"]),
            "movies_count": len(home_data["movies"]),
            "cache_size": len(self.cache)
        }
