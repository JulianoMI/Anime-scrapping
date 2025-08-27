# Anime Scraper - Python Web Application

A Python-based web scraper that extracts anime information from meownime.ltd with both a beautiful web interface and pure Python backend logic.

## Features

- **🏠 Home Page Scraping**: Browse ongoing anime, completed series, and movies
- **📋 Complete Anime List**: Alphabetical list with letter filtering (A-Z)
- **🔍 Search Functionality**: Find specific anime by title
- **📖 Detailed Information**: View synopsis and download links for each anime
- **💾 Data Export**: Save scraped data to JSON or CSV files
- **🎨 Colorful Interface**: Beautiful terminal output with colors and emojis

## Installation

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
python anime_scraper.py
```

## Menu Options

1. **🏠 Scrape Home Page** - Get categorized anime (ongoing, completed, movies)
2. **📋 Scrape Complete Anime List** - Get all available anime titles
3. **🔤 Filter Anime by Letter** - Filter anime list by starting letter (A-Z)
4. **🔍 Search Anime** - Search for specific anime by title
5. **📖 Get Anime Details** - Get detailed info including synopsis and download links
6. **💾 Export Data** - Save scraped data to JSON or CSV files
7. **❌ Exit** - Close the application

## Technology Stack

- **Language**: Pure Python 3
- **Web Scraping**: BeautifulSoup4, Requests
- **Terminal Colors**: Colorama
- **Table Display**: Tabulate
- **Data Export**: JSON, CSV

## Python Concepts Demonstrated

- **Object-Oriented Programming**: Class-based design with methods
- **Web Scraping**: HTTP requests and HTML parsing
- **Error Handling**: Try-catch blocks and graceful error management
- **File I/O**: Reading/writing JSON and CSV files
- **String Manipulation**: Text processing and formatting
- **Lists and Dictionaries**: Data structure manipulation
- **Control Flow**: Loops, conditionals, and menu systems
- **User Input**: Interactive terminal interface

## Usage Examples

```python
# Create scraper instance
scraper = AnimeScraper()

# Scrape home page
data = scraper.scrape_home_page()

# Search for anime
results = scraper.search_anime("naruto")

# Get anime details
details = scraper.scrape_anime_details("https://meownime.ltd/anime-url")
```

## Sample Output

```
🎌 ANIME SCRAPER - MEOWNIME PORTAL 🎌
Python Web Scraping Application
Target: https://meownime.ltd

📋 MENU OPTIONS:
1. 🏠 Scrape Home Page (Categories)
2. 📋 Scrape Complete Anime List
3. 🔤 Filter Anime by Letter
4. 🔍 Search Anime
5. 📖 Get Anime Details
6. 💾 Export Data
7. ❌ Exit
```

## Educational Value

This project teaches:
- Web scraping fundamentals
- Python programming best practices
- Data extraction and processing
- Terminal application development
- File handling and data export
- Error handling and user experience

## Legal Notice

This application is for educational purposes only. Please respect the original website's terms of service and copyright policies.
# Anime-scrapping
