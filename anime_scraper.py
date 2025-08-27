#!/usr/bin/env python3
"""
Anime Scraper - Terminal Application
A Python-based web scraper for meownime.ltd anime website
"""

import requests
from bs4 import BeautifulSoup
import json
import csv
import os
import sys
from urllib.parse import urljoin, urlparse
import time
from colorama import init, Fore, Back, Style
from tabulate import tabulate

# Initialize colorama for colored terminal output
init(autoreset=True)

class AnimeScraper:
    def __init__(self):
        """Initialize the anime scraper with session and headers"""
        self.base_url = "https://meownime.ltd"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.anime_data = {}
        
    def print_header(self):
        """Print application header"""
        print(Fore.CYAN + "=" * 60)
        print(Fore.YELLOW + "🎌 ANIME SCRAPER - MEOWNIME PORTAL 🎌")
        print(Fore.CYAN + "=" * 60)
        print(Fore.GREEN + "Python Web Scraping Application")
        print(Fore.WHITE + "Target: https://meownime.ltd")
        print(Fore.CYAN + "=" * 60)
    
    def get_page(self, url):
        """Fetch page content with error handling"""
        try:
            print(Fore.YELLOW + f"📡 Fetching: {url}")
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            print(Fore.GREEN + "✅ Page loaded successfully!")
            return response.text
        except requests.RequestException as e:
            print(Fore.RED + f"❌ Error fetching {url}: {e}")
            return None
    
    def scrape_home_page(self):
        """Scrape the home page for anime categories"""
        print(Fore.BLUE + "\n🏠 Scraping Home Page...")
        html = self.get_page(self.base_url)
        if not html:
            return {"ongoing": [], "completed": [], "movies": []}
        
        soup = BeautifulSoup(html, 'html.parser')
        
        data = {
            "ongoing": [],
            "completed": [],
            "movies": []
        }
        
        # Find all anime links
        anime_links = soup.find_all('a', href=True)
        
        for link in anime_links:
            href = link.get('href', '')
            title = link.get_text(strip=True)
            
            if '/sub-indo/' in href and title and len(title) > 3:
                anime_info = {
                    "title": title,
                    "url": href
                }
                
                # Categorize based on URL patterns and keywords
                if 'movie' in href.lower() or 'film' in href.lower():
                    data["movies"].append(anime_info)
                elif any(keyword in title.lower() for keyword in ['season', 'part', 'episode']):
                    data["ongoing"].append(anime_info)
                else:
                    data["completed"].append(anime_info)
        
        # Remove duplicates and limit results
        for category in data:
            seen = set()
            unique_items = []
            for item in data[category]:
                if item['title'] not in seen:
                    seen.add(item['title'])
                    unique_items.append(item)
            data[category] = unique_items[:15]  # Limit to 15 items per category
        
        self.anime_data['home'] = data
        return data
    
    def scrape_anime_list(self, letter=None):
        """Scrape the complete anime list"""
        print(Fore.BLUE + f"\n📋 Scraping Anime List{f' (Letter: {letter})' if letter else ''}...")
        url = f"{self.base_url}/anime-list-baru"
        html = self.get_page(url)
        if not html:
            return []
        
        soup = BeautifulSoup(html, 'html.parser')
        anime_list = []
        
        # Find all anime links
        links = soup.find_all('a', href=True)
        
        for link in links:
            href = link.get('href', '')
            title = link.get_text(strip=True)
            
            if '/sub-indo/' in href and title and len(title) > 3:
                if letter is None or title.lower().startswith(letter.lower()):
                    anime_list.append({
                        "title": title,
                        "url": href
                    })
        
        # Remove duplicates and sort
        seen = set()
        unique_anime = []
        for anime in anime_list:
            if anime['title'] not in seen:
                seen.add(anime['title'])
                unique_anime.append(anime)
        
        result = sorted(unique_anime, key=lambda x: x['title'])
        self.anime_data['list'] = result
        return result
    
    def scrape_anime_details(self, anime_url):
        """Scrape detailed information about a specific anime"""
        print(Fore.BLUE + f"\n🔍 Scraping Anime Details...")
        html = self.get_page(anime_url)
        if not html:
            return None
        
        soup = BeautifulSoup(html, 'html.parser')
        
        # Extract title
        title = soup.find('h1')
        title_text = title.get_text(strip=True) if title else "Unknown Title"
        
        # Extract synopsis/description
        synopsis = ""
        synopsis_selectors = [
            '.entry-content p',
            '.post-content p',
            '.content p',
            'p'
        ]
        
        for selector in synopsis_selectors:
            elements = soup.select(selector)
            if elements:
                synopsis_parts = []
                for p in elements[:3]:
                    text = p.get_text(strip=True)
                    if len(text) > 20:  # Only include meaningful paragraphs
                        synopsis_parts.append(text)
                synopsis = ' '.join(synopsis_parts)
                break
        
        # Find download links
        download_links = []
        links = soup.find_all('a', href=True)
        
        for link in links:
            href = link.get('href', '')
            text = link.get_text(strip=True)
            
            if any(domain in href for domain in ['drive.google.com', 'mega.nz', 'mediafire.com', 'zippyshare.com']):
                download_links.append({
                    "text": text,
                    "url": href,
                    "type": self.determine_link_type(href)
                })
        
        return {
            "title": title_text,
            "synopsis": synopsis[:300] + "..." if len(synopsis) > 300 else synopsis,
            "download_links": download_links[:8],  # Limit to 8 links
            "url": anime_url
        }
    
    def determine_link_type(self, url):
        """Determine the type of download link"""
        if 'drive.google.com' in url:
            return 'Google Drive'
        elif 'mega.nz' in url:
            return 'MEGA'
        elif 'mediafire.com' in url:
            return 'MediaFire'
        elif 'zippyshare.com' in url:
            return 'ZippyShare'
        else:
            return 'Other'
    
    def search_anime(self, query):
        """Search for anime by title"""
        print(Fore.BLUE + f"\n🔎 Searching for: '{query}'...")
        
        # First get the complete anime list if not already loaded
        if 'list' not in self.anime_data:
            self.scrape_anime_list()
        
        all_anime = self.anime_data.get('list', [])
        query_lower = query.lower()
        
        results = []
        for anime in all_anime:
            if query_lower in anime['title'].lower():
                results.append(anime)
        
        return results[:20]  # Limit to 20 results
    
    def display_anime_list(self, anime_list, title="Anime List"):
        """Display anime list in a formatted table"""
        if not anime_list:
            print(Fore.RED + "❌ No anime found!")
            return
        
        print(Fore.GREEN + f"\n📺 {title} ({len(anime_list)} items)")
        print(Fore.CYAN + "-" * 80)
        
        # Prepare data for table
        table_data = []
        for i, anime in enumerate(anime_list, 1):
            table_data.append([
                str(i),
                anime['title'][:50] + "..." if len(anime['title']) > 50 else anime['title'],
                anime['url'][:40] + "..." if len(anime['url']) > 40 else anime['url']
            ])
        
        # Display table
        headers = ["#", "Title", "URL"]
        print(tabulate(table_data, headers=headers, tablefmt="grid"))
    
    def display_anime_details(self, details):
        """Display detailed anime information"""
        if not details:
            print(Fore.RED + "❌ No details available!")
            return
        
        print(Fore.GREEN + f"\n🎬 ANIME DETAILS")
        print(Fore.CYAN + "=" * 80)
        print(Fore.YELLOW + f"Title: {details['title']}")
        print(Fore.WHITE + f"URL: {details['url']}")
        print(Fore.CYAN + "-" * 80)
        print(Fore.WHITE + f"Synopsis:")
        print(Fore.LIGHTWHITE_EX + f"{details['synopsis']}")
        
        if details['download_links']:
            print(Fore.CYAN + "-" * 80)
            print(Fore.GREEN + f"📥 Download Links ({len(details['download_links'])} found):")
            
            for i, link in enumerate(details['download_links'], 1):
                print(Fore.YELLOW + f"{i}. {link['text']}")
                print(Fore.WHITE + f"   Type: {link['type']}")
                print(Fore.LIGHTBLUE_EX + f"   URL: {link['url']}")
                print()
        else:
            print(Fore.RED + "❌ No download links found!")
    
    def save_to_json(self, data, filename):
        """Save data to JSON file"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(Fore.GREEN + f"✅ Data saved to {filename}")
        except Exception as e:
            print(Fore.RED + f"❌ Error saving to JSON: {e}")
    
    def save_to_csv(self, anime_list, filename):
        """Save anime list to CSV file"""
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['Title', 'URL'])
                for anime in anime_list:
                    writer.writerow([anime['title'], anime['url']])
            print(Fore.GREEN + f"✅ Data saved to {filename}")
        except Exception as e:
            print(Fore.RED + f"❌ Error saving to CSV: {e}")

def main():
    """Main application function"""
    scraper = AnimeScraper()
    
    while True:
        scraper.print_header()
        
        print(Fore.WHITE + "\n📋 MENU OPTIONS:")
        print(Fore.CYAN + "1. 🏠 Scrape Home Page (Categories)")
        print(Fore.CYAN + "2. 📋 Scrape Complete Anime List")
        print(Fore.CYAN + "3. 🔤 Filter Anime by Letter")
        print(Fore.CYAN + "4. 🔍 Search Anime")
        print(Fore.CYAN + "5. 📖 Get Anime Details")
        print(Fore.CYAN + "6. 💾 Export Data")
        print(Fore.CYAN + "7. ❌ Exit")
        
        choice = input(Fore.YELLOW + "\n👉 Enter your choice (1-7): ").strip()
        
        if choice == '1':
            data = scraper.scrape_home_page()
            
            print(Fore.GREEN + f"\n🔥 ONGOING ANIME ({len(data['ongoing'])} found)")
            scraper.display_anime_list(data['ongoing'], "Ongoing Anime")
            
            print(Fore.GREEN + f"\n✅ COMPLETED ANIME ({len(data['completed'])} found)")
            scraper.display_anime_list(data['completed'], "Completed Anime")
            
            print(Fore.GREEN + f"\n🎬 ANIME MOVIES ({len(data['movies'])} found)")
            scraper.display_anime_list(data['movies'], "Anime Movies")
        
        elif choice == '2':
            anime_list = scraper.scrape_anime_list()
            scraper.display_anime_list(anime_list, "Complete Anime List")
        
        elif choice == '3':
            letter = input(Fore.YELLOW + "Enter letter (A-Z): ").strip().upper()
            if letter and len(letter) == 1 and letter.isalpha():
                anime_list = scraper.scrape_anime_list(letter)
                scraper.display_anime_list(anime_list, f"Anime starting with '{letter}'")
            else:
                print(Fore.RED + "❌ Please enter a valid single letter!")
        
        elif choice == '4':
            query = input(Fore.YELLOW + "Enter search term: ").strip()
            if query:
                results = scraper.search_anime(query)
                scraper.display_anime_list(results, f"Search Results for '{query}'")
            else:
                print(Fore.RED + "❌ Please enter a search term!")
        
        elif choice == '5':
            url = input(Fore.YELLOW + "Enter anime URL: ").strip()
            if url:
                details = scraper.scrape_anime_details(url)
                scraper.display_anime_details(details)
            else:
                print(Fore.RED + "❌ Please enter a valid URL!")
        
        elif choice == '6':
            if not scraper.anime_data:
                print(Fore.RED + "❌ No data to export! Please scrape some data first.")
            else:
                print(Fore.CYAN + "\n💾 EXPORT OPTIONS:")
                print("1. Export to JSON")
                print("2. Export to CSV")
                
                export_choice = input(Fore.YELLOW + "Choose export format (1-2): ").strip()
                
                if export_choice == '1':
                    filename = input(Fore.YELLOW + "Enter filename (without extension): ").strip() or "anime_data"
                    scraper.save_to_json(scraper.anime_data, f"{filename}.json")
                
                elif export_choice == '2':
                    if 'list' in scraper.anime_data:
                        filename = input(Fore.YELLOW + "Enter filename (without extension): ").strip() or "anime_list"
                        scraper.save_to_csv(scraper.anime_data['list'], f"{filename}.csv")
                    else:
                        print(Fore.RED + "❌ No anime list data available for CSV export!")
                
                else:
                    print(Fore.RED + "❌ Invalid choice!")
        
        elif choice == '7':
            print(Fore.GREEN + "\n👋 Thank you for using Anime Scraper!")
            print(Fore.CYAN + "🎌 Sayonara! 🎌")
            break
        
        else:
            print(Fore.RED + "❌ Invalid choice! Please enter 1-7.")
        
        # Wait for user input before continuing
        input(Fore.YELLOW + "\n⏸️  Press Enter to continue...")
        
        # Clear screen (works on both Windows and Unix)
        os.system('cls' if os.name == 'nt' else 'clear')

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(Fore.RED + "\n\n❌ Application interrupted by user!")
        print(Fore.GREEN + "👋 Goodbye!")
    except Exception as e:
        print(Fore.RED + f"\n❌ An error occurred: {e}")
        print(Fore.YELLOW + "Please check your internet connection and try again.")
