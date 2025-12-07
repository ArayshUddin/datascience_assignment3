"""
Progress Tracker Service
Tracks scraping progress for real-time updates
"""
import threading
import time
from typing import Dict, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ProgressTracker:
    """Thread-safe progress tracker for scraping operations"""
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self._progress: Dict[str, Dict] = {}
        self._lock = threading.Lock()
        self._initialized = True
    
    def start_job(self, job_id: str, total: int, description: str = ""):
        """Start tracking a new job"""
        with self._lock:
            self._progress[job_id] = {
                'total': total,
                'completed': 0,
                'successful': 0,
                'failed': 0,
                'description': description,
                'start_time': time.time(),
                'status': 'running',
                'current_url': None,
                'completed_urls': [],  # List of (url, status, timestamp) tuples
                'recent_completed': []  # Last 20 completed items
            }
        logger.info(f"Started tracking job {job_id}: {total} items")
    
    def set_current_url(self, job_id: str, url: str):
        """Set the current URL being scraped"""
        with self._lock:
            if job_id in self._progress:
                self._progress[job_id]['current_url'] = url
    
    def update_progress(self, job_id: str, successful: bool = True, url: str = None):
        """Update progress for a job"""
        with self._lock:
            if job_id in self._progress:
                self._progress[job_id]['completed'] += 1
                if successful:
                    self._progress[job_id]['successful'] += 1
                else:
                    self._progress[job_id]['failed'] += 1
                
                # Track completed URL
                if url:
                    status = 'success' if successful else 'failed'
                    completed_item = {
                        'url': url,
                        'status': status,
                        'timestamp': time.time()
                    }
                    self._progress[job_id]['completed_urls'].append(completed_item)
                    
                    # Keep recent completed list (last 20)
                    self._progress[job_id]['recent_completed'].append(completed_item)
                    if len(self._progress[job_id]['recent_completed']) > 20:
                        self._progress[job_id]['recent_completed'].pop(0)
                
                # Clear current URL after completion
                self._progress[job_id]['current_url'] = None
    
    def get_progress(self, job_id: str) -> Optional[Dict]:
        """Get current progress for a job"""
        with self._lock:
            if job_id in self._progress:
                progress = self._progress[job_id].copy()
                total = progress['total']
                completed = progress['completed']
                
                # Calculate percentage
                progress['percentage'] = (completed / total * 100) if total > 0 else 0
                
                # Calculate estimated time remaining
                if completed > 0:
                    elapsed = time.time() - progress['start_time']
                    avg_time_per_item = elapsed / completed
                    remaining_items = total - completed
                    progress['estimated_seconds_remaining'] = avg_time_per_item * remaining_items
                else:
                    progress['estimated_seconds_remaining'] = None
                
                return progress
        return None
    
    def complete_job(self, job_id: str):
        """Mark a job as completed"""
        with self._lock:
            if job_id in self._progress:
                self._progress[job_id]['status'] = 'completed'
                self._progress[job_id]['completed'] = self._progress[job_id]['total']
    
    def fail_job(self, job_id: str, error: str = ""):
        """Mark a job as failed"""
        with self._lock:
            if job_id in self._progress:
                self._progress[job_id]['status'] = 'failed'
                self._progress[job_id]['error'] = error
    
    def remove_job(self, job_id: str):
        """Remove a completed job (cleanup)"""
        with self._lock:
            if job_id in self._progress:
                del self._progress[job_id]
    
    def cleanup_old_jobs(self, max_age_seconds: int = 3600):
        """Remove old completed jobs"""
        current_time = time.time()
        with self._lock:
            to_remove = []
            for job_id, progress in self._progress.items():
                if progress['status'] in ['completed', 'failed']:
                    age = current_time - progress['start_time']
                    if age > max_age_seconds:
                        to_remove.append(job_id)
            
            for job_id in to_remove:
                del self._progress[job_id]
        
        if to_remove:
            logger.info(f"Cleaned up {len(to_remove)} old jobs")


# Global instance
progress_tracker = ProgressTracker()

