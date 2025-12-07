"""
Helper script to scrape articles from Excel file
Can be run standalone or imported
"""
import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from services.scraper import MediumScraper
from services.csv_handler import CSVHandler
from services.url_reader import read_urls_from_excel


def main():
    """Main function to scrape from Excel file"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Scrape articles from Excel file')
    parser.add_argument('file_path', help='Path to Excel file containing URLs')
    parser.add_argument('--column', '-c', help='Column name containing URLs (uses first column if not specified)')
    parser.add_argument('--delay', '-d', type=float, default=1.0, help='Delay between requests in seconds (default: 1.0)')
    parser.add_argument('--batch-size', '-b', type=int, default=100, help='Number of URLs to process in each batch (default: 100)')
    
    args = parser.parse_args()
    
    # Read URLs
    print(f"Reading URLs from {args.file_path}...")
    urls = read_urls_from_excel(args.file_path, args.column)
    
    if not urls:
        print("No valid URLs found in Excel file!")
        return
    
    print(f"Found {len(urls)} URLs")
    
    # Initialize services
    scraper = MediumScraper()
    csv_handler = CSVHandler()
    
    # Filter out already scraped URLs
    new_urls = [url for url in urls if not csv_handler.article_exists(url)]
    
    if not new_urls:
        print("All URLs have already been scraped!")
        return
    
    print(f"Scraping {len(new_urls)} new URLs (skipped {len(urls) - len(new_urls)} already scraped)")
    
    # Process in batches
    total_scraped = 0
    for i in range(0, len(new_urls), args.batch_size):
        batch = new_urls[i:i + args.batch_size]
        batch_num = (i // args.batch_size) + 1
        total_batches = (len(new_urls) + args.batch_size - 1) // args.batch_size
        
        print(f"\nProcessing batch {batch_num}/{total_batches} ({len(batch)} URLs)...")
        
        results = scraper.scrape_multiple(batch, delay=args.delay)
        
        if results:
            csv_handler.save_articles(results, append=True)
            total_scraped += len(results)
            print(f"Batch {batch_num} complete: {len(results)} articles scraped")
        else:
            print(f"Batch {batch_num} complete: No articles scraped")
    
    print(f"\n✅ Scraping complete! Total articles scraped: {total_scraped}")
    print(f"Total articles in database: {csv_handler.get_article_count()}")


if __name__ == "__main__":
    main()

