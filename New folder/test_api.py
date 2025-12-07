"""
Test script for Scraping & Search API
Run this to test all endpoints
"""
import requests
import json
import time
import os

BASE_URL = "http://localhost:8000"

def print_section(title):
    """Print a section header"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)

def test_health():
    """Test health endpoint"""
    print_section("Test 1: Health Check")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("✅ Health check passed!")
            print(f"   Status: {data.get('status')}")
            print(f"   Service: {data.get('service')}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Is it running?")
        print("   Start server with: python start_api_server.py")
        return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def test_scrape_urls():
    """Test scraping from URLs"""
    print_section("Test 2: Scrape URLs")
    # Using a sample URL (you can replace with real URLs)
    test_urls = [
        "https://medium.com/@example/test-article-1",
        "https://medium.com/@example/test-article-2"
    ]
    
    payload = {
        "urls": test_urls,
        "delay": 1.0
    }
    
    try:
        print(f"   Testing with {len(test_urls)} URLs...")
        response = requests.post(
            f"{BASE_URL}/scraper/scrape-urls",
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Scrape URLs endpoint works!")
            print(f"   Message: {data.get('message')}")
            print(f"   Total URLs: {data.get('total_urls')}")
            print(f"   Successful: {data.get('successful')}")
            print(f"   Failed: {data.get('failed')}")
            print(f"   Saved to CSV: {data.get('saved_to_csv')}")
            return True
        else:
            print(f"❌ Request failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def test_scrape_excel():
    """Test scraping from Excel file"""
    print_section("Test 3: Scrape from Excel")
    
    excel_path = "file/url_technology.xlsx"
    
    if not os.path.exists(excel_path):
        print(f"⚠️  Excel file not found: {excel_path}")
        print("   Skipping this test...")
        return None
    
    payload = {
        "file_path": excel_path,
        "column_name": None,
        "delay": 1.0
    }
    
    try:
        print(f"   Testing with Excel file: {excel_path}")
        print("   Note: This may take a while with many URLs...")
        response = requests.post(
            f"{BASE_URL}/scraper/scrape-excel",
            json=payload,
            timeout=300  # 5 minutes timeout for large files
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Scrape Excel endpoint works!")
            print(f"   Message: {data.get('message')}")
            print(f"   Total URLs: {data.get('total_urls')}")
            print(f"   Successful: {data.get('successful')}")
            print(f"   Failed: {data.get('failed')}")
            return True
        else:
            print(f"❌ Request failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def test_scrape_status():
    """Test scraping status endpoint"""
    print_section("Test 4: Scraping Status")
    
    try:
        response = requests.get(f"{BASE_URL}/scraper/status", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Status endpoint works!")
            print(f"   Status: {data.get('status')}")
            print(f"   Total Articles: {data.get('total_articles')}")
            print(f"   Message: {data.get('message')}")
            return True
        else:
            print(f"❌ Request failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def test_search_similar():
    """Test search similar articles"""
    print_section("Test 5: Search Similar Articles")
    
    payload = {
        "query": "machine learning python data science",
        "top_k": 10
    }
    
    try:
        print(f"   Searching for: '{payload['query']}'")
        response = requests.post(
            f"{BASE_URL}/search/similar",
            json=payload,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Search endpoint works!")
            print(f"   Query: {data.get('query')}")
            print(f"   Results found: {data.get('total_found')}")
            
            results = data.get('results', [])
            if results:
                print(f"\n   Top {min(3, len(results))} results:")
                for i, article in enumerate(results[:3], 1):
                    print(f"   {i}. {article.get('title', 'No title')}")
                    print(f"      URL: {article.get('url', 'No URL')}")
                    print(f"      Claps: {article.get('claps', 0)}")
            else:
                print("   ⚠️  No results found. Scrape some articles first!")
            
            return True
        elif response.status_code == 404:
            print("⚠️  No articles in database yet.")
            print("   Scrape some articles first, then try searching.")
            return None
        else:
            print(f"❌ Request failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def test_top_clapped():
    """Test top clapped articles"""
    print_section("Test 6: Top Clapped Articles")
    
    try:
        response = requests.get(
            f"{BASE_URL}/search/top-clapped?top_k=10",
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Top clapped endpoint works!")
            print(f"   Results found: {data.get('total_found')}")
            
            results = data.get('results', [])
            if results:
                print(f"\n   Top {min(3, len(results))} articles:")
                for i, article in enumerate(results[:3], 1):
                    print(f"   {i}. {article.get('title', 'No title')}")
                    print(f"      URL: {article.get('url', 'No URL')}")
                    print(f"      Claps: {article.get('claps', 0)}")
            else:
                print("   ⚠️  No articles found. Scrape some articles first!")
            
            return True
        elif response.status_code == 404:
            print("⚠️  No articles in database yet.")
            print("   Scrape some articles first.")
            return None
        else:
            print(f"❌ Request failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def check_csv_file():
    """Check if CSV file exists and has data"""
    print_section("Test 7: Check CSV File")
    
    csv_file = "scrapping_results.csv"
    
    if os.path.exists(csv_file):
        import pandas as pd
        try:
            df = pd.read_csv(csv_file)
            print(f"✅ CSV file exists: {csv_file}")
            print(f"   Total articles: {len(df)}")
            print(f"   Columns: {', '.join(df.columns.tolist())}")
            
            # Check required columns
            required_cols = [
                'url', 'title', 'subtitle', 'text', 'num_images',
                'image_urls', 'num_external_links', 'external_links',
                'author_name', 'author_url', 'claps', 'reading_time', 'keywords'
            ]
            
            missing_cols = [col for col in required_cols if col not in df.columns]
            if missing_cols:
                print(f"   ⚠️  Missing columns: {', '.join(missing_cols)}")
            else:
                print("   ✅ All required columns present!")
            
            return True
        except Exception as e:
            print(f"   ⚠️  Error reading CSV: {str(e)}")
            return False
    else:
        print(f"⚠️  CSV file not found: {csv_file}")
        print("   Scrape some articles first to create the file.")
        return False

def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("  Scraping & Search API - Test Suite")
    print("=" * 60)
    
    results = {}
    
    # Test 1: Health check
    results['health'] = test_health()
    if not results['health']:
        print("\n❌ Server is not running. Please start it first!")
        return
    
    # Test 2: Scrape URLs
    results['scrape_urls'] = test_scrape_urls()
    
    # Test 3: Scrape Excel (optional - may take time)
    print("\n⚠️  Note: Excel scraping test will be skipped (takes too long)")
    print("   You can test it manually via the API docs")
    # results['scrape_excel'] = test_scrape_excel()
    
    # Test 4: Status
    results['status'] = test_scrape_status()
    
    # Test 5: Search
    results['search'] = test_search_similar()
    
    # Test 6: Top clapped
    results['top_clapped'] = test_top_clapped()
    
    # Test 7: CSV file
    results['csv'] = check_csv_file()
    
    # Summary
    print_section("Test Summary")
    passed = sum(1 for v in results.values() if v is True)
    total = len([v for v in results.values() if v is not None])
    
    print(f"Tests passed: {passed}/{total}")
    print("\n✅ = Passed")
    print("❌ = Failed")
    print("⚠️  = Skipped/Warning")
    
    for test_name, result in results.items():
        if result is True:
            print(f"  ✅ {test_name}")
        elif result is False:
            print(f"  ❌ {test_name}")
        else:
            print(f"  ⚠️  {test_name} (skipped)")
    
    print("\n" + "=" * 60)
    print("  Testing Complete!")
    print("=" * 60)
    print("\n💡 Tips:")
    print("  - Use http://localhost:8000/docs for interactive testing")
    print("  - Scrape some articles before testing search")
    print("  - Check scrapping_results.csv for scraped data")

if __name__ == "__main__":
    main()

