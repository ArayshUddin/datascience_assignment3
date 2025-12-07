"""
URL Reader Service
Reads URLs from Excel files
"""
import pandas as pd
from typing import List
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def read_urls_from_excel(file_path: str, column_name: str = None) -> List[str]:
    """
    Read URLs from Excel file
    
    Args:
        file_path: Path to Excel file
        column_name: Name of column containing URLs (if None, uses first column)
    
    Returns:
        List of URLs
    """
    try:
        df = pd.read_excel(file_path)
        
        # If column name not specified, use first column
        if column_name is None:
            column_name = df.columns[0]
        
        # Extract URLs
        urls = df[column_name].dropna().tolist()
        
        # Filter to only valid URLs
        valid_urls = []
        for url in urls:
            url_str = str(url).strip()
            if url_str.startswith('http://') or url_str.startswith('https://'):
                valid_urls.append(url_str)
        
        logger.info(f"Read {len(valid_urls)} URLs from {file_path}")
        return valid_urls
        
    except Exception as e:
        logger.error(f"Error reading URLs from Excel: {str(e)}")
        return []

