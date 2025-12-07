# Guide: What to Exclude When Creating a ZIP File

When creating a ZIP file of this project, **exclude the following** to keep the file size small and avoid including unnecessary files:

## 🚫 Files and Directories to EXCLUDE:

### 1. **Python Cache Files** (Auto-generated)
- `__pycache__/` (all directories)
- `*.pyc` files
- `*.pyo` files
- `*.pyd` files

### 2. **Virtual Environment** (if exists)
- `venv/`
- `env/`
- `.venv/`
- `ENV/`

### 3. **Scraped Data** (Large output file)
- `scrapping_results.csv` (can be very large with 58K+ articles)

### 4. **Temporary Files**
- `temp_*.xlsx` (temporary Excel files from uploads)
- `*.tmp`
- `*.log`

### 5. **IDE/Editor Files**
- `.vscode/`
- `.idea/`
- `*.swp`
- `*.swo`

### 6. **OS Files**
- `.DS_Store` (macOS)
- `Thumbs.db` (Windows)
- `desktop.ini`

### 7. **Environment Files** (Sensitive)
- `.env`
- `.env.local`

### 8. **Build/Distribution Files**
- `build/`
- `dist/`
- `*.egg-info/`
- `*.egg`

## ✅ Files to INCLUDE:

- All `.py` source files
- `requirements.txt`
- `README.md` and documentation files
- `frontend/` directory (HTML, CSS, JS)
- `file/url_technology.xlsx` (input data - include if needed, but it's large)
- Configuration files (`config.py`, `Procfile`, etc.)
- `start_api_server.py`
- All other project files

## 📦 Quick ZIP Command (Windows PowerShell):

```powershell
# Exclude cache, venv, CSV results, and temp files
Compress-Archive -Path * -DestinationPath web_scraping_project.zip -Exclude @('__pycache__','*.pyc','venv','env','.venv','scrapping_results.csv','temp_*','*.log','.vscode','.idea')
```

## 📦 Manual ZIP Creation:

1. **Select all files and folders**
2. **Exclude these specifically:**
   - All `__pycache__` folders
   - `scrapping_results.csv` (if it exists and is large)
   - `venv/` or `env/` (if you have a virtual environment)
   - Any `.log` files
   - Temporary files

## 💡 Recommendation:

**For sharing/deployment:**
- ✅ Include: All source code, requirements.txt, frontend, documentation
- ❌ Exclude: `scrapping_results.csv` (too large, can be regenerated)
- ❌ Exclude: `__pycache__/` (auto-generated)
- ⚠️ Optional: `file/url_technology.xlsx` (large file, include only if needed)

**For backup:**
- Include everything except `__pycache__/` and virtual environments

