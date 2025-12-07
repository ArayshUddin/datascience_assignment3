# Testing Guide for Scraping & Search API

This guide will help you test your assignment to ensure everything works correctly.

## Prerequisites

1. **Start the server** (if not already running):
   ```bash
   python start_api_server.py
   ```
   Or:
   ```bash
   uvicorn api.main:app --reload
   ```

2. **Verify server is running**:
   - Open browser: `http://localhost:8000/health`
   - Should return: `{"status":"healthy",...}`

## Method 1: Using Interactive API Documentation (Easiest)

1. **Open Swagger UI**:
   - Navigate to: `http://localhost:8000/docs`
   - This provides an interactive interface to test all endpoints

2. **Test Scraping Endpoints**:
   - Click on `POST /scraper/scrape-urls`
   - Click "Try it out"
   - Enter test URLs:
     ```json
     {
       "urls": [
         "https://medium.com/@example/article-url-1",
         "https://medium.com/@example/article-url-2"
       ],
       "delay": 1.0
     }
     ```
   - Click "Execute"
   - Check the response for success/failure counts

3. **Test Search Endpoints**:
   - Click on `POST /search/similar`
   - Click "Try it out"
   - Enter query:
     ```json
     {
       "query": "machine learning python",
       "top_k": 10
     }
     ```
   - Click "Execute"
   - Verify it returns top 10 similar articles with URLs and titles

## Method 2: Using cURL Commands

### Test 1: Health Check
```bash
curl http://localhost:8000/health
```

### Test 2: Scrape URLs
```bash
curl -X POST "http://localhost:8000/scraper/scrape-urls" \
  -H "Content-Type: application/json" \
  -d "{\"urls\": [\"https://medium.com/@example/article\"], \"delay\": 1.0}"
```

### Test 3: Scrape from Excel File
```bash
curl -X POST "http://localhost:8000/scraper/scrape-excel" \
  -H "Content-Type: application/json" \
  -d "{\"file_path\": \"file/url_technology.xlsx\", \"delay\": 1.0}"
```

### Test 4: Get Scraping Status
```bash
curl http://localhost:8000/scraper/status
```

### Test 5: Search Similar Articles
```bash
curl -X POST "http://localhost:8000/search/similar" \
  -H "Content-Type: application/json" \
  -d "{\"query\": \"machine learning\", \"top_k\": 10}"
```

### Test 6: Get Top Clapped Articles
```bash
curl http://localhost:8000/search/top-clapped?top_k=10
```

## Method 3: Using Python Script

Run the provided test script:
```bash
python test_api.py
```

## Method 4: Using Postman or Insomnia

1. Import the OpenAPI schema from: `http://localhost:8000/openapi.json`
2. Test each endpoint with sample data

## Testing Checklist

### Part A: Scraping Functionality

- [ ] **Test scraping from URLs**
  - Provide a list of URLs
  - Verify response shows successful/failed counts
  - Check that `scrapping_results.csv` is created/updated
  - Verify CSV contains: Title, Subtitle, Text, Images, Links, Author, Claps, Reading time, Keywords

- [ ] **Test scraping from Excel**
  - Use `file/url_technology.xlsx`
  - Verify it reads URLs from the file
  - Check that articles are scraped and saved

- [ ] **Verify CSV output**
  - Open `scrapping_results.csv`
  - Check all required columns are present:
    - url, title, subtitle, text
    - num_images, image_urls
    - num_external_links, external_links
    - author_name, author_url
    - claps, reading_time, keywords

- [ ] **Test duplicate handling**
  - Try scraping the same URL twice
  - Verify it skips duplicates

### Part B: Search Functionality

- [ ] **Test search by text/keywords**
  - Search with query: "machine learning python"
  - Verify it returns top 10 results
  - Check each result has: URL and Title (required)
  - Verify results are sorted by similarity + claps

- [ ] **Test top clapped articles**
  - Call `/search/top-clapped`
  - Verify it returns articles sorted by claps
  - Check response format includes URL and Title

- [ ] **Test with no data**
  - Search before scraping any articles
  - Should return appropriate error message

## Expected Results

### Scraping Response:
```json
{
  "message": "Scraped X articles successfully",
  "total_urls": 10,
  "successful": 8,
  "failed": 2,
  "saved_to_csv": true
}
```

### Search Response:
```json
{
  "query": "machine learning",
  "results": [
    {
      "url": "https://medium.com/@author/article",
      "title": "Article Title",
      "subtitle": "Article Subtitle",
      "author_name": "Author Name",
      "claps": 1500,
      "reading_time": "5 min read"
    }
  ],
  "total_found": 10
}
```

## Troubleshooting

1. **Server not starting**: Check if port 8000 is already in use
2. **Import errors**: Make sure all dependencies are installed: `pip install -r requirements.txt`
3. **CSV not created**: Check file permissions in the project directory
4. **No search results**: Make sure you've scraped some articles first
5. **Scraping fails**: Check if URLs are valid and accessible

## Quick Test Sequence

1. Start server: `python start_api_server.py`
2. Open docs: `http://localhost:8000/docs`
3. Test scrape a few URLs
4. Check CSV file is created
5. Test search with keywords
6. Verify results include URL and Title

