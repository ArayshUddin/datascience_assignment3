// API Base URL - dynamically determine from current location
const API_BASE_URL = window.location.origin;

// Tab Management
document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        const tab = btn.dataset.tab;
        
        // Update tab buttons
        document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        
        // Update tab content
        document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
        document.getElementById(`${tab}-tab`).classList.add('active');
    });
});

// Option Tabs (URLs vs Excel)
document.querySelectorAll('.option-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        const option = btn.dataset.option;
        
        // Update option buttons
        document.querySelectorAll('.option-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        
        // Update option content
        document.querySelectorAll('.option-content').forEach(c => c.classList.remove('active'));
        document.getElementById(`${option}-option`).classList.add('active');
    });
});

// Scrape URLs Form
document.getElementById('scrape-urls-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const urlsText = document.getElementById('urls-input').value.trim();
    const delay = parseFloat(document.getElementById('delay-input').value);
    
    if (!urlsText) {
        showMessage('Please enter at least one URL', 'error');
        return;
    }
    
    const urls = urlsText.split('\n')
        .map(url => url.trim())
        .filter(url => url && (url.startsWith('http://') || url.startsWith('https://')));
    
    if (urls.length === 0) {
        showMessage('Please enter valid URLs (starting with http:// or https://)', 'error');
        return;
    }
    
    const btn = e.target.querySelector('button[type="submit"]');
    const btnText = btn.querySelector('.btn-text');
    const btnLoader = btn.querySelector('.btn-loader');
    
    // Show progress for URLs too (reuse Excel progress div)
    const progressDiv = document.getElementById('scraping-progress');
    
    btn.disabled = true;
    btnText.style.display = 'none';
    btnLoader.style.display = 'inline';
    progressDiv.style.display = 'block';
    
    // Reset progress
    updateProgress(0, 0, 0, 0, 0, null, null, []);
    
    try {
        const response = await fetch(`${API_BASE_URL}/scraper/scrape-urls`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                urls: urls,
                delay: delay
            })
        });
        
        const data = await response.json();
        
        if (response.ok && data.job_id) {
            currentJobId = data.job_id;
            console.log('URL scraping job started with ID:', data.job_id); // Debug log
            showMessage(`Scraping started! Processing ${data.total_urls} URLs...`, 'success');
            
            // Start polling for progress
            startProgressPolling(data.job_id);
        } else if (response.ok && !data.job_id) {
            // Already completed or no URLs to scrape
            showMessage(data.message || 'No URLs to scrape', 'info');
            progressDiv.style.display = 'none';
            btn.disabled = false;
            btnText.style.display = 'inline';
            btnLoader.style.display = 'none';
        } else {
            showMessage(data.detail || 'Scraping failed', 'error');
            progressDiv.style.display = 'none';
            btn.disabled = false;
            btnText.style.display = 'inline';
            btnLoader.style.display = 'none';
        }
    } catch (error) {
        showMessage(`Error: ${error.message}`, 'error');
        progressDiv.style.display = 'none';
        btn.disabled = false;
        btnText.style.display = 'inline';
        btnLoader.style.display = 'none';
    }
});

// Scrape Excel Form (File Upload)
let progressInterval = null;
let currentJobId = null;

document.getElementById('scrape-excel-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const fileInput = document.getElementById('excel-file');
    const delay = parseFloat(document.getElementById('excel-delay').value);
    
    if (!fileInput.files || fileInput.files.length === 0) {
        showMessage('Please select an Excel file', 'error');
        return;
    }
    
    const file = fileInput.files[0];
    
    // Validate file type
    if (!file.name.endsWith('.xlsx') && !file.name.endsWith('.xls')) {
        showMessage('Please select a valid Excel file (.xlsx or .xls)', 'error');
        return;
    }
    
    const btn = e.target.querySelector('button[type="submit"]');
    const btnText = btn.querySelector('.btn-text');
    const btnLoader = btn.querySelector('.btn-loader');
    const progressDiv = document.getElementById('scraping-progress');
    
    btn.disabled = true;
    btnText.style.display = 'none';
    btnLoader.style.display = 'inline';
    progressDiv.style.display = 'block';
    
    // Reset progress
    updateProgress(0, 0, 0, 0, 0, null, null, []);
    
    try {
        // Upload file and start scraping
        const formData = new FormData();
        formData.append('file', file);
        formData.append('delay', delay);
        
        const response = await fetch(`${API_BASE_URL}/scraper/scrape-excel-upload`, {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (response.ok && data.job_id) {
            currentJobId = data.job_id;
            console.log('Excel scraping job started with ID:', data.job_id); // Debug log
            showMessage(`Scraping started! Processing ${data.total_urls} URLs from Excel file...`, 'success');
            
            // Start polling for progress
            startProgressPolling(data.job_id);
        } else if (response.ok && !data.job_id) {
            // Already completed or no URLs to scrape
            showMessage(data.message || 'All URLs from Excel have already been scraped', 'info');
            progressDiv.style.display = 'none';
            btn.disabled = false;
            btnText.style.display = 'inline';
            btnLoader.style.display = 'none';
        } else {
            showMessage(data.detail || data.message || 'Scraping failed', 'error');
            progressDiv.style.display = 'none';
            btn.disabled = false;
            btnText.style.display = 'inline';
            btnLoader.style.display = 'none';
        }
    } catch (error) {
        showMessage(`Error: ${error.message}`, 'error');
        progressDiv.style.display = 'none';
        btn.disabled = false;
        btnText.style.display = 'inline';
        btnLoader.style.display = 'none';
    }
});

// Progress Polling
function startProgressPolling(jobId) {
    console.log('Starting progress polling for job:', jobId); // Debug log
    
    // Clear any existing interval
    if (progressInterval) {
        clearInterval(progressInterval);
    }
    
    // Clear any existing completion message
    const progressDiv = document.getElementById('scraping-progress');
    if (progressDiv) {
        const existingMsg = progressDiv.querySelector('.completion-message');
        if (existingMsg) {
            existingMsg.remove();
        }
    }
    
    // Poll every 1 second
    progressInterval = setInterval(async () => {
        try {
            const response = await fetch(`${API_BASE_URL}/scraper/progress/${jobId}`);
            
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }));
                console.error('Progress fetch error:', response.status, errorData);
                
                // If job not found, stop polling
                if (response.status === 404) {
                    clearInterval(progressInterval);
                    progressInterval = null;
                    showMessage('Scraping job not found. It may have expired or completed.', 'error');
                    // Re-enable buttons
                    const buttons = document.querySelectorAll('button[type="submit"]');
                    buttons.forEach(btn => {
                        const btnText = btn.querySelector('.btn-text');
                        const btnLoader = btn.querySelector('.btn-loader');
                        if (btnText && btnLoader) {
                            btn.disabled = false;
                            btnText.style.display = 'inline';
                            btnLoader.style.display = 'none';
                        }
                    });
                }
                return;
            }
            
            const progress = await response.json();
            console.log('Progress update:', progress); // Debug log
            
            updateProgress(
                progress.percentage || 0,
                progress.completed || 0,
                progress.total || 0,
                progress.successful || 0,
                progress.failed || 0,
                progress.estimated_seconds_remaining,
                progress.current_url,
                progress.recent_completed || []
            );
            
            // If completed or failed, stop polling
            if (progress.status === 'completed' || progress.status === 'failed') {
                clearInterval(progressInterval);
                progressInterval = null;
                
                // Re-enable buttons
                const buttons = document.querySelectorAll('button[type="submit"]');
                buttons.forEach(btn => {
                    const btnText = btn.querySelector('.btn-text');
                    const btnLoader = btn.querySelector('.btn-loader');
                    if (btnText && btnLoader) {
                        btn.disabled = false;
                        btnText.style.display = 'inline';
                        btnLoader.style.display = 'none';
                    }
                });
                
                // Show final message with detailed summary
                if (progress.status === 'completed') {
                    const successRate = progress.total > 0 ? ((progress.successful / progress.total) * 100).toFixed(1) : 0;
                    const completionMsg = `✅ Scraping Completed! Total: ${progress.total} | Successful: ${progress.successful} | Failed: ${progress.failed} | Success Rate: ${successRate}%`;
                    showMessage(completionMsg, 'success');
                    
                    // Show detailed completion notification in progress div
                    const progressDiv = document.getElementById('scraping-progress');
                    if (progressDiv) {
                        // Remove any existing completion message
                        const existingMsg = progressDiv.querySelector('.completion-message');
                        if (existingMsg) {
                            existingMsg.remove();
                        }
                        
                        const completionMsgDiv = document.createElement('div');
                        completionMsgDiv.className = 'completion-message';
                        completionMsgDiv.style.cssText = 'margin-top: 15px; padding: 15px; background: #d4edda; border: 1px solid #c3e6cb; border-radius: 6px; color: #155724;';
                        completionMsgDiv.innerHTML = `
                            <strong>🎉 Scraping Finished!</strong><br>
                            <div style="margin-top: 10px;">
                                <div>✅ Successfully scraped: <strong>${progress.successful}</strong> articles</div>
                                <div>❌ Failed: <strong>${progress.failed}</strong> articles</div>
                                <div>📊 Success Rate: <strong>${successRate}%</strong></div>
                                <div style="margin-top: 10px; font-size: 0.9em; color: #666;">
                                    Data has been saved to <code>scrapping_results.csv</code>
                                </div>
                            </div>
                        `;
                        progressDiv.appendChild(completionMsgDiv);
                    }
                } else {
                    showMessage(`❌ Scraping failed: ${progress.description || 'Unknown error'}`, 'error');
                }
                
                // Refresh status
                document.getElementById('refresh-status-btn')?.click();
            }
        } catch (error) {
            console.error('Error polling progress:', error);
            // Don't stop polling on network errors, just log
        }
    }, 1000); // Poll every second
}

// Update Progress Display
function updateProgress(percentage, completed, total, successful, failed, etaSeconds = null, currentUrl = null, recentCompleted = []) {
    const progressFill = document.getElementById('progress-fill');
    const progressText = document.getElementById('progress-text');
    const progressDetails = document.getElementById('progress-details');
    const progressSuccessful = document.getElementById('progress-successful');
    const progressFailed = document.getElementById('progress-failed');
    const progressEta = document.getElementById('progress-eta');
    const currentUrlSection = document.getElementById('current-url-section');
    const currentUrlDiv = document.getElementById('current-url');
    const recentItemsSection = document.getElementById('recent-items-section');
    const recentItemsList = document.getElementById('recent-items-list');
    
    // Update progress bar
    const percentageValue = Math.round(percentage);
    progressFill.style.width = `${percentageValue}%`;
    progressText.textContent = `${percentageValue}%`;
    progressDetails.textContent = `${completed} / ${total}`;
    progressSuccessful.textContent = successful;
    progressFailed.textContent = failed;
    
    // Update ETA
    if (etaSeconds !== null && etaSeconds > 0) {
        const minutes = Math.floor(etaSeconds / 60);
        const seconds = Math.floor(etaSeconds % 60);
        if (minutes > 0) {
            progressEta.textContent = `⏱️ Estimated time remaining: ${minutes}m ${seconds}s`;
        } else {
            progressEta.textContent = `⏱️ Estimated time remaining: ${seconds}s`;
        }
    } else {
        progressEta.textContent = '';
    }
    
    // Update current URL
    if (currentUrl) {
        currentUrlSection.style.display = 'block';
        currentUrlDiv.textContent = currentUrl;
        currentUrlDiv.style.color = '#1976d2';
    } else {
        currentUrlSection.style.display = 'none';
    }
    
    // Update recent completed items
    if (recentCompleted && recentCompleted.length > 0) {
        recentItemsSection.style.display = 'block';
        
        // Display items in reverse order (most recent first)
        const itemsHtml = recentCompleted.slice().reverse().map(item => {
            const statusIcon = item.status === 'success' ? '✅' : '❌';
            const statusColor = item.status === 'success' ? '#4caf50' : '#f44336';
            const timeAgo = getTimeAgo(item.timestamp);
            
            // Truncate long URLs for display
            const displayUrl = item.url.length > 80 ? item.url.substring(0, 80) + '...' : item.url;
            
            return `
                <div style="padding: 8px; margin-bottom: 5px; background: white; border-left: 3px solid ${statusColor}; border-radius: 4px;">
                    <div style="display: flex; align-items: center; gap: 8px;">
                        <span style="font-size: 1.1em;">${statusIcon}</span>
                        <span style="flex: 1; word-break: break-all; font-size: 0.9em;">${displayUrl}</span>
                        <span style="color: #666; font-size: 0.85em; white-space: nowrap;">${timeAgo}</span>
                    </div>
                </div>
            `;
        }).join('');
        
        recentItemsList.innerHTML = itemsHtml;
    } else {
        recentItemsSection.style.display = 'none';
    }
}

// Helper function to get time ago
function getTimeAgo(timestamp) {
    if (!timestamp) return '';
    const seconds = Math.floor((Date.now() / 1000) - timestamp);
    if (seconds < 60) return `${seconds}s ago`;
    const minutes = Math.floor(seconds / 60);
    if (minutes < 60) return `${minutes}m ago`;
    const hours = Math.floor(minutes / 60);
    return `${hours}h ago`;
}

// Search Form
document.getElementById('search-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const query = document.getElementById('search-query').value.trim();
    const topK = parseInt(document.getElementById('top-k').value);
    
    if (!query) {
        showMessage('Please enter a search query', 'error');
        return;
    }
    
    const btn = e.target.querySelector('button[type="submit"]');
    const btnText = btn.querySelector('.btn-text');
    const btnLoader = btn.querySelector('.btn-loader');
    
    btn.disabled = true;
    btnText.style.display = 'none';
    btnLoader.style.display = 'inline';
    
    try {
        const response = await fetch(`${API_BASE_URL}/search/similar`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                query: query,
                top_k: topK
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            displaySearchResults(data);
            showMessage(`Found ${data.total_found} results`, 'success');
        } else {
            showMessage(data.detail || 'Search failed', 'error');
        }
    } catch (error) {
        showMessage(`Error: ${error.message}`, 'error');
    } finally {
        btn.disabled = false;
        btnText.style.display = 'inline';
        btnLoader.style.display = 'none';
    }
});

// Top Clapped Button
document.getElementById('top-clapped-btn').addEventListener('click', async () => {
    const btn = document.getElementById('top-clapped-btn');
    const btnText = btn.querySelector('.btn-text');
    const btnLoader = btn.querySelector('.btn-loader');
    
    btn.disabled = true;
    btnText.style.display = 'none';
    btnLoader.style.display = 'inline';
    
    try {
        const response = await fetch(`${API_BASE_URL}/search/top-clapped?top_k=10`);
        const data = await response.json();
        
        if (response.ok) {
            displayTopClappedResults(data);
            showMessage(`Found ${data.total_found} top clapped articles`, 'success');
        } else {
            showMessage(data.detail || 'Failed to fetch top clapped articles', 'error');
        }
    } catch (error) {
        showMessage(`Error: ${error.message}`, 'error');
    } finally {
        btn.disabled = false;
        btnText.style.display = 'inline';
        btnLoader.style.display = 'none';
    }
});

// Refresh Status Button
document.getElementById('refresh-status-btn').addEventListener('click', async () => {
    const btn = document.getElementById('refresh-status-btn');
    btn.disabled = true;
    btn.textContent = 'Loading...';
    
    try {
        const response = await fetch(`${API_BASE_URL}/scraper/status`);
        const data = await response.json();
        
        if (response.ok) {
            displayStatus(data);
        } else {
            showMessage(data.detail || 'Failed to fetch status', 'error');
        }
    } catch (error) {
        showMessage(`Error: ${error.message}`, 'error');
    } finally {
        btn.disabled = false;
        btn.textContent = 'Refresh Status';
    }
});

// Display Functions
function displayScrapeResults(data) {
    const resultsDiv = document.getElementById('scrape-results');
    const contentDiv = document.getElementById('scrape-results-content');
    
    contentDiv.innerHTML = `
        <div class="result-item">
            <h4>Scraping Summary</h4>
            <div class="meta">
                <span><strong>Total URLs:</strong> ${data.total_urls}</span>
                <span><strong>Successful:</strong> <span style="color: green;">${data.successful}</span></span>
                <span><strong>Failed:</strong> <span style="color: red;">${data.failed}</span></span>
                <span><strong>Saved to CSV:</strong> ${data.saved_to_csv ? '✅ Yes' : '❌ No'}</span>
            </div>
            <p style="margin-top: 10px;"><strong>Message:</strong> ${data.message}</p>
        </div>
    `;
    
    resultsDiv.style.display = 'block';
}

function displaySearchResults(data) {
    const resultsDiv = document.getElementById('search-results');
    const contentDiv = document.getElementById('search-results-content');
    
    if (data.results && data.results.length > 0) {
        contentDiv.innerHTML = `
            <div class="article-list">
                ${data.results.map((article, index) => `
                    <div class="article-card">
                        <h4>${index + 1}. ${article.title || 'No Title'}</h4>
                        <a href="${article.url}" target="_blank" class="article-url">${article.url}</a>
                        ${article.subtitle ? `<p style="color: #666; margin: 10px 0;">${article.subtitle}</p>` : ''}
                        <div class="article-meta">
                            ${article.author_name ? `<span>👤 ${article.author_name}</span>` : ''}
                            ${article.claps ? `<span>👏 ${article.claps.toLocaleString()} claps</span>` : ''}
                            ${article.reading_time ? `<span>⏱️ ${article.reading_time}</span>` : ''}
                        </div>
                    </div>
                `).join('')}
            </div>
        `;
    } else {
        contentDiv.innerHTML = '<p>No results found. Try a different search query or scrape some articles first.</p>';
    }
    
    resultsDiv.style.display = 'block';
}

function displayTopClappedResults(data) {
    const resultsDiv = document.getElementById('top-clapped-results');
    const contentDiv = document.getElementById('top-clapped-results-content');
    
    if (data.results && data.results.length > 0) {
        contentDiv.innerHTML = `
            <div class="article-list">
                ${data.results.map((article, index) => `
                    <div class="article-card">
                        <h4>${index + 1}. ${article.title || 'No Title'}</h4>
                        <a href="${article.url}" target="_blank" class="article-url">${article.url}</a>
                        ${article.subtitle ? `<p style="color: #666; margin: 10px 0;">${article.subtitle}</p>` : ''}
                        <div class="article-meta">
                            ${article.author_name ? `<span>👤 ${article.author_name}</span>` : ''}
                            <span>👏 <strong>${article.claps.toLocaleString()}</strong> claps</span>
                            ${article.reading_time ? `<span>⏱️ ${article.reading_time}</span>` : ''}
                        </div>
                    </div>
                `).join('')}
            </div>
        `;
    } else {
        contentDiv.innerHTML = '<p>No articles found. Scrape some articles first.</p>';
    }
    
    resultsDiv.style.display = 'block';
}

function displayStatus(data) {
    const statusDiv = document.getElementById('status-content');
    
    statusDiv.innerHTML = `
        <div class="status-item">
            <strong>Status:</strong>
            <span class="status-value">${data.status}</span>
        </div>
        <div class="status-item">
            <strong>Total Articles:</strong>
            <span class="status-value">${data.total_articles.toLocaleString()}</span>
        </div>
        <div class="status-item">
            <strong>Message:</strong>
            <span class="status-value">${data.message}</span>
        </div>
    `;
}

// Message Display
function showMessage(message, type = 'info') {
    // Remove existing messages
    document.querySelectorAll('.message').forEach(msg => msg.remove());
    
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}`;
    messageDiv.textContent = message;
    
    // Insert at the top of the active tab
    const activeTab = document.querySelector('.tab-content.active');
    activeTab.insertBefore(messageDiv, activeTab.firstChild);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        messageDiv.remove();
    }, 5000);
}

// Load status on page load
window.addEventListener('load', () => {
    document.getElementById('refresh-status-btn').click();
});

