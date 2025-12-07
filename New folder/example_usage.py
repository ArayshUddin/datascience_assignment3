"""
Example usage of the scraping and search API
This file demonstrates how to use the API endpoints
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def example_scrape_urls():
    """Example: Scrape articles from a list of URLs"""
    url = f"{BASE_URL}/api/scraper/scrape-urls"
    
    payload = {
        "urls": [
            "https://medium.com/@example/article-1",
            "https://medium.com/@example/article-2"
        ],
        "delay": 1.0
    }
    
    response = requests.post(url, json=payload)
    print("Scrape URLs Response:")
    print(json.dumps(response.json(), indent=2))


def example_scrape_excel():
    """Example: Scrape articles from Excel file"""
    url = f"{BASE_URL}/api/scraper/scrape-excel"
    
    payload = {
        "file_path": "file/url_technology.xlsx",
        "column_name": None,  # Uses first column if None
        "delay": 1.0
    }
    
    response = requests.post(url, json=payload)
    print("Scrape Excel Response:")
    print(json.dumps(response.json(), indent=2))


def example_search():
    """Example: Search for similar articles"""
    url = f"{BASE_URL}/api/search/similar"
    
    payload = {
        "query": "machine learning python data science",
        "top_k": 10
    }
    
    response = requests.post(url, json=payload)
    print("Search Response:")
    print(json.dumps(response.json(), indent=2))
    
    # Print results
    results = response.json().get("results", [])
    print(f"\nFound {len(results)} similar articles:")
    for i, article in enumerate(results, 1):
        print(f"{i}. {article['title']}")
        print(f"   URL: {article['url']}")
        print(f"   Claps: {article['claps']}")
        print()


def example_top_clapped():
    """Example: Get top clapped articles"""
    url = f"{BASE_URL}/api/search/top-clapped?top_k=10"
    
    response = requests.get(url)
    print("Top Clapped Response:")
    print(json.dumps(response.json(), indent=2))


def example_status():
    """Example: Get scraping status"""
    url = f"{BASE_URL}/api/scraper/status"
    
    response = requests.get(url)
    print("Status Response:")
    print(json.dumps(response.json(), indent=2))


if __name__ == "__main__":
    print("=" * 60)
    print("Scraping API - Example Usage")
    print("=" * 60)
    print("\nMake sure the API server is running at http://localhost:8000")
    print("\nUncomment the examples you want to run:\n")
    
    # Uncomment to run examples:
    # example_status()
    # example_scrape_urls()
    # example_scrape_excel()
    # example_search()
    # example_top_clapped()

