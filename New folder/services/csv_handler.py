"""
CSV Handler Service
Manages reading and writing scraped data to CSV
"""
import os
import pandas as pd
from typing import List, Dict, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

CSV_FILE = "scrapping_results.csv"


class CSVHandler:
    """Handles CSV operations for scraped data"""
    
    def __init__(self, csv_file: str = CSV_FILE):
        self.csv_file = csv_file
        self.columns = [
            'url', 'title', 'subtitle', 'text', 'num_images', 
            'image_urls', 'num_external_links', 'external_links',
            'author_name', 'author_url', 'claps', 'reading_time', 'keywords'
        ]
    
    def save_articles(self, articles: List[Dict], append: bool = True) -> bool:
        """
        Save articles to CSV file
        
        Args:
            articles: List of article dictionaries
            append: If True, append to existing file; if False, overwrite
        
        Returns:
            True if successful, False otherwise
        """
        try:
            if not articles:
                logger.warning("No articles to save")
                return False
            
            df = pd.DataFrame(articles)
            
            # Ensure all columns exist
            for col in self.columns:
                if col not in df.columns:
                    df[col] = ''
            
            # Reorder columns
            df = df[self.columns]
            
            # Check if file exists and append mode
            if append and os.path.exists(self.csv_file):
                existing_df = pd.read_csv(self.csv_file)
                # Remove duplicates based on URL
                df = pd.concat([existing_df, df]).drop_duplicates(subset=['url'], keep='last')
            
            # Save to CSV
            df.to_csv(self.csv_file, index=False, encoding='utf-8')
            logger.info(f"Saved {len(articles)} articles to {self.csv_file}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving articles to CSV: {str(e)}")
            return False
    
    def load_articles(self) -> List[Dict]:
        """
        Load all articles from CSV file
        
        Returns:
            List of article dictionaries
        """
        try:
            if not os.path.exists(self.csv_file):
                logger.warning(f"CSV file {self.csv_file} does not exist")
                return []
            
            df = pd.read_csv(self.csv_file)
            
            # Replace NaN values with empty strings for string columns and 0 for numeric columns
            string_columns = ['url', 'title', 'subtitle', 'text', 'image_urls', 'external_links', 
                            'author_name', 'author_url', 'reading_time', 'keywords']
            numeric_columns = ['claps', 'num_images', 'num_external_links']
            
            for col in string_columns:
                if col in df.columns:
                    df[col] = df[col].fillna('').astype(str)
            
            for col in numeric_columns:
                if col in df.columns:
                    df[col] = df[col].fillna(0).astype(int)
            
            articles = df.to_dict('records')
            
            # Convert all NaN values to appropriate defaults (comprehensive cleanup)
            for article in articles:
                # Handle all string fields
                for key in article:
                    value = article[key]
                    # Check if it's NaN (float NaN)
                    if isinstance(value, float) and pd.isna(value):
                        article[key] = ''
                    # Check if it's the string 'nan'
                    elif isinstance(value, str) and value.lower() == 'nan':
                        article[key] = ''
                    # Check if it's None
                    elif value is None:
                        article[key] = ''
                
                # Convert numeric columns with proper handling
                if 'claps' in article:
                    try:
                        val = article['claps']
                        if pd.isna(val) or val == '' or val == 'nan':
                            article['claps'] = 0
                        else:
                            article['claps'] = int(float(val))
                    except:
                        article['claps'] = 0
                if 'num_images' in article:
                    try:
                        val = article['num_images']
                        if pd.isna(val) or val == '' or val == 'nan':
                            article['num_images'] = 0
                        else:
                            article['num_images'] = int(float(val))
                    except:
                        article['num_images'] = 0
                if 'num_external_links' in article:
                    try:
                        val = article['num_external_links']
                        if pd.isna(val) or val == '' or val == 'nan':
                            article['num_external_links'] = 0
                        else:
                            article['num_external_links'] = int(float(val))
                    except:
                        article['num_external_links'] = 0
            
            logger.info(f"Loaded {len(articles)} articles from {self.csv_file}")
            return articles
            
        except Exception as e:
            logger.error(f"Error loading articles from CSV: {str(e)}")
            return []
    
    def get_article_count(self) -> int:
        """Get total number of articles in CSV"""
        try:
            if not os.path.exists(self.csv_file):
                return 0
            df = pd.read_csv(self.csv_file)
            return len(df)
        except:
            return 0
    
    def article_exists(self, url: str) -> bool:
        """Check if article with given URL already exists"""
        try:
            if not os.path.exists(self.csv_file):
                return False
            df = pd.read_csv(self.csv_file)
            return url in df['url'].values
        except:
            return False

