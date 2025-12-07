# Frontend for Article Scraper

A modern, user-friendly web interface for scraping articles and searching through your collection.

## Features

### Part A: Scraping Interface
- **Scrape from URLs**: Enter multiple URLs and scrape them
- **Scrape from Excel**: Upload your Excel file with 58,000 URLs
- **Real-time Progress**: See scraping results as they happen
- **CSV Export**: All data automatically saved to `scrapping_results.csv`

### Part B: Search Interface
- **Keyword Search**: Search articles by text/keywords
- **Top Clapped Articles**: View most popular articles
- **Results Display**: See URL and Title for each article (as required)

## How to Use

### Option 1: Direct File Access
1. Make sure your FastAPI server is running:
   ```bash
   python start_api_server.py
   ```

2. Open `frontend/index.html` in your web browser
   - Simply double-click the file, or
   - Right-click → Open with → Your browser

### Option 2: Through FastAPI Server
1. Start the server:
   ```bash
   python start_api_server.py
   ```

2. Open in browser:
   ```
   http://localhost:8000/frontend
   ```

### Option 3: Using a Simple HTTP Server
1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Start a simple HTTP server:
   ```bash
   # Python 3
   python -m http.server 8080
   
   # Or using Node.js (if installed)
   npx http-server -p 8080
   ```

3. Open in browser:
   ```
   http://localhost:8080
   ```

## Usage Guide

### Scraping Articles

1. **Go to "Scrape Articles" tab**

2. **Choose scraping method:**
   - **From URLs**: Paste article URLs (one per line)
   - **From Excel**: Enter the path to your Excel file (e.g., `file/url_technology.xlsx`)

3. **Set delay** (optional): Time between requests (default: 1 second)

4. **Click "Start Scraping"**

5. **View results**: See success/failure counts and status

### Searching Articles

1. **Go to "Search Articles" tab**

2. **Enter search query**: Type keywords or text to search for

3. **Set number of results**: How many articles to return (default: 10)

4. **Click "Search"**

5. **View results**: See top matching articles with:
   - Title
   - URL (clickable)
   - Author name
   - Claps count
   - Reading time

### Viewing Status

1. **Go to "Status" tab**

2. **Click "Refresh Status"** to see:
   - Total articles scraped
   - Current status

## Features

- ✅ Modern, responsive design
- ✅ Real-time feedback
- ✅ Error handling
- ✅ Loading indicators
- ✅ Results display with clickable URLs
- ✅ Mobile-friendly interface

## Troubleshooting

### CORS Errors
If you see CORS errors, make sure:
1. The FastAPI server is running
2. CORS is enabled in `api/main.py` (it should be by default)

### API Connection Issues
- Check that the server is running on `http://localhost:8000`
- Verify the API_BASE_URL in `frontend/script.js` matches your server URL
- Check browser console for errors (F12 → Console)

### File Path Issues
- Make sure Excel file path is relative to the project root
- Example: `file/url_technology.xlsx`

## File Structure

```
frontend/
├── index.html      # Main HTML file
├── styles.css       # Styling
└── script.js        # JavaScript logic
```

## Customization

### Change API URL
Edit `frontend/script.js`:
```javascript
const API_BASE_URL = 'http://localhost:8000'; // Change this
```

### Modify Styling
Edit `frontend/styles.css` to customize colors, fonts, and layout.

## Notes

- The frontend connects to your FastAPI backend
- All scraping data is saved to `scrapping_results.csv` in the project root
- Search requires scraped articles to be available first
- Large Excel files (58,000 URLs) may take a long time to process

