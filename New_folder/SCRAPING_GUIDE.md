# Article Scraping & Search API

This FastAPI backend provides endpoints for scraping articles and searching through them.

## Features

### Part A: Scraping
- Scrape articles from URLs
- Extract: Title, Subtitle, Text, Number of images, Image URLs, Number of external links, Author Name, Author URL, Claps, Reading time, Keywords
- Save results to `scrapping_results.csv`
- Support for scraping from Excel files with URLs
- Automatic duplicate detection (skips already scraped URLs)

### Part B: Search API
- Search for similar articles based on text/keywords
- Returns top 10 most clapped similar articles
- Results include URL and Title (and additional metadata)

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Starting the API Server

```bash
python start_api_server.py
```

Or:
```bash
uvicorn api.main:app --reload
```

The API will be available at `http://localhost:8000`
- API Documentation: `http://localhost:8000/docs`
- Health Check: `http://localhost:8000/health`

### API Endpoints

#### 1. Scrape Articles from URLs

**POST** `/api/scraper/scrape-urls`

Request body:
```json
{
  "urls": [
    "https://medium.com/@user/article-1",
    "https://medium.com/@user/article-2"
  ],
  "delay": 1.0
}
```

Response:
```json
{
  "message": "Scraped 2 articles successfully",
  "total_urls": 2,
  "successful": 2,
  "failed": 0,
  "saved_to_csv": true
}
```

#### 2. Scrape Articles from Excel File

**POST** `/api/scraper/scrape-excel`

Request body:
```json
{
  "file_path": "file/url_technology.xlsx",
  "column_name": null,
  "delay": 1.0
}
```

Note: `column_name` is optional. If not provided, uses the first column.

#### 3. Get Scraping Status

**GET** `/api/scraper/status`

Returns the total number of articles in the database.

#### 4. Search Similar Articles

**POST** `/api/search/similar`

Request body:
```json
{
  "query": "machine learning python",
  "top_k": 10
}
```

Response:
```json
{
  "query": "machine learning python",
  "results": [
    {
      "url": "https://medium.com/@user/article",
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

#### 5. Get Top Clapped Articles

**GET** `/api/search/top-clapped?top_k=10`

Returns the top K most clapped articles.

### Standalone Script

You can also use the standalone script to scrape from Excel:

```bash
python scripts/scrape_from_excel.py file/url_technology.xlsx
```

Options:
- `--column` or `-c`: Column name containing URLs
- `--delay` or `-d`: Delay between requests (default: 1.0 seconds)
- `--batch-size` or `-b`: Number of URLs per batch (default: 100)

Example:
```bash
python scripts/scrape_from_excel.py file/url_technology.xlsx --delay 2.0 --batch-size 50
```

## CSV Output Format

The `scrapping_results.csv` file contains the following columns:

- `url`: Article URL
- `title`: Article title
- `subtitle`: Article subtitle
- `text`: Full article text
- `num_images`: Number of images
- `image_urls`: Pipe-separated image URLs (|)
- `num_external_links`: Number of external links
- `external_links`: Pipe-separated external link URLs (|)
- `author_name`: Author name
- `author_url`: Author profile URL
- `claps`: Number of claps
- `reading_time`: Reading time (e.g., "5 min read")
- `keywords`: Pipe-separated keywords (|)

## Notes

- The scraper includes a delay between requests to be respectful to Medium's servers
- Duplicate URLs are automatically skipped
- The search uses TF-IDF vectorization and cosine similarity for finding similar articles
- Results are ranked by a combination of similarity score (70%) and claps (30%)
- All scraped data is saved to `scrapping_results.csv` in the project root

## Deployment

This API can be deployed on any platform that supports Python/FastAPI:
- Railway (already configured with `railway.json` and `Procfile`)
- Heroku
- AWS Lambda
- Google Cloud Run
- Any VPS with Python

Make sure to set environment variables as needed in your deployment platform.

