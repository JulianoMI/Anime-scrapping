#!/usr/bin/env python3
"""
Debug script to test the scraper and see what's being extracted
"""

from scraper_core import AnimeScraper
import json

def debug_scraper():
    scraper = AnimeScraper()
    
    print("🔍 Testing scraper...")
    
    # Test home page scraping
    print("\n📡 Fetching home page...")
    data = scraper.scrape_home_page()
    
    print(f"\n📊 Results:")
    print(f"Ongoing: {len(data['ongoing'])} items")
    print(f"Completed: {len(data['completed'])} items") 
    print(f"Movies: {len(data['movies'])} items")
    
    # Show some examples
    if data['ongoing']:
        print(f"\n🔥 Ongoing anime examples:")
        for anime in data['ongoing'][:3]:
            print(f"  - {anime['title']}")
    
    if data['completed']:
        print(f"\n✅ Completed anime examples:")
        for anime in data['completed'][:3]:
            print(f"  - {anime['title']}")
    
    if data['movies']:
        print(f"\n🎬 Movie examples:")
        for anime in data['movies'][:3]:
            print(f"  - {anime['title']}")
    
    # Save debug data
    with open('debug_output.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 Debug data saved to debug_output.json")

if __name__ == "__main__":
    debug_scraper()
