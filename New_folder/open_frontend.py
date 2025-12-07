"""
Simple script to open the frontend in the default browser
"""
import webbrowser
import os
from pathlib import Path

def open_frontend():
    """Open the frontend HTML file in the default browser"""
    frontend_path = Path(__file__).parent / "frontend" / "index.html"
    
    if frontend_path.exists():
        # Convert to file:// URL
        file_url = frontend_path.as_uri()
        print(f"Opening frontend: {file_url}")
        webbrowser.open(file_url)
        print("\n[OK] Frontend opened in your browser!")
        print("\n[TIP] Make sure your FastAPI server is running:")
        print("   python start_api_server.py")
    else:
        print(f"❌ Frontend not found at: {frontend_path}")
        print("   Please make sure the frontend folder exists.")

if __name__ == "__main__":
    open_frontend()

