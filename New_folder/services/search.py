"""
Search Service
Finds similar articles based on text/keywords
"""
import re
from typing import List, Dict
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ArticleSearch:
    """Search service for finding similar articles"""
    
    def __init__(self):
        self.vectorizer = TfidfVectorizer(
            max_features=5000,
            stop_words='english',
            ngram_range=(1, 2),
            min_df=1
        )
    
    def search_similar_articles(
        self, 
        query: str, 
        articles: List[Dict], 
        top_k: int = 10
    ) -> List[Dict]:
        """
        Find top K similar articles based on query text/keywords
        
        Args:
            query: Search query (text or keywords)
            articles: List of all articles to search
            top_k: Number of top results to return
        
        Returns:
            List of top K articles sorted by similarity and claps
        """
        if not articles:
            return []
        
        if not query or not query.strip():
            # If no query, return top clapped articles
            sorted_articles = sorted(
                articles, 
                key=lambda x: x.get('claps', 0), 
                reverse=True
            )
            return sorted_articles[:top_k]
        
        try:
            # Prepare documents for vectorization
            documents = []
            for article in articles:
                # Combine title, subtitle, text, and keywords for search
                doc_parts = []
                if article.get('title'):
                    doc_parts.append(str(article['title']))
                if article.get('subtitle'):
                    doc_parts.append(str(article['subtitle']))
                if article.get('text'):
                    # Use first 1000 chars of text to avoid too long documents
                    text = str(article['text'])[:1000]
                    doc_parts.append(text)
                if article.get('keywords'):
                    keywords = str(article['keywords']).replace('|', ' ')
                    doc_parts.append(keywords)
                
                documents.append(' '.join(doc_parts))
            
            # Add query to documents for vectorization
            all_docs = [query] + documents
            
            # Vectorize
            tfidf_matrix = self.vectorizer.fit_transform(all_docs)
            
            # Calculate similarity between query and all articles
            query_vector = tfidf_matrix[0:1]
            article_vectors = tfidf_matrix[1:]
            
            similarities = cosine_similarity(query_vector, article_vectors)[0]
            
            # Combine similarity scores with articles
            scored_articles = []
            for i, article in enumerate(articles):
                similarity_score = float(similarities[i])
                claps = article.get('claps', 0)
                
                # Combined score: 70% similarity, 30% claps (normalized)
                # Normalize claps (assuming max claps around 10000)
                normalized_claps = min(claps / 10000.0, 1.0) if claps > 0 else 0
                combined_score = 0.7 * similarity_score + 0.3 * normalized_claps
                
                scored_articles.append({
                    **article,
                    'similarity_score': similarity_score,
                    'combined_score': combined_score
                })
            
            # Sort by combined score, then by claps
            scored_articles.sort(
                key=lambda x: (x['combined_score'], x.get('claps', 0)), 
                reverse=True
            )
            
            # Return top K
            top_articles = scored_articles[:top_k]
            
            # Remove internal scoring fields from output
            for article in top_articles:
                article.pop('similarity_score', None)
                article.pop('combined_score', None)
            
            return top_articles
            
        except Exception as e:
            logger.error(f"Error in search: {str(e)}")
            # Fallback: return top clapped articles
            sorted_articles = sorted(
                articles, 
                key=lambda x: x.get('claps', 0), 
                reverse=True
            )
            return sorted_articles[:top_k]
    
    def search_by_keywords(
        self, 
        keywords: List[str], 
        articles: List[Dict], 
        top_k: int = 10
    ) -> List[Dict]:
        """
        Search articles by keywords
        
        Args:
            keywords: List of keywords to search for
            articles: List of all articles
            top_k: Number of results to return
        
        Returns:
            List of top K matching articles
        """
        query = ' '.join(keywords)
        return self.search_similar_articles(query, articles, top_k)

