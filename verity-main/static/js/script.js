// Global variables
let currentPage = 1;
let isLoading = false;
let hasMore = true;

document.addEventListener('DOMContentLoaded', function() {
    // Get the initial current page from the data attribute
    const newsContainer = document.getElementById('news-container');
    if (newsContainer) {
        currentPage = parseInt(newsContainer.getAttribute('data-current-page') || '1');
        hasMore = newsContainer.getAttribute('data-has-more') === 'true';
        
        // Initialize load more button
        const loadMoreBtn = document.getElementById('load-more-btn');
        if (loadMoreBtn) {
            if (!hasMore) {
                loadMoreBtn.classList.add('d-none');
            }
            
            loadMoreBtn.addEventListener('click', function() {
                loadMoreNews();
            });
        }
    }
    
    // Initialize tooltips
    initializeTooltips();
});

/**
 * Load more news articles when the user clicks the "Load More" button
 */
function loadMoreNews() {
    // Prevent multiple simultaneous requests
    if (isLoading || !hasMore) return;
    
    // Update UI to show loading state
    isLoading = true;
    const loadMoreBtn = document.getElementById('load-more-btn');
    const loadingSpinner = document.getElementById('loading-spinner');
    
    loadMoreBtn.disabled = true;
    loadingSpinner.classList.remove('d-none');
    
    // Increment page number
    currentPage++;
    
    // Fetch more news
    fetch(`/load_more?page=${currentPage}`)
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            // Process the new articles
            if (data.articles && data.articles.length > 0) {
                // Append new articles to the container
                const newsContainer = document.getElementById('news-container');
                data.articles.forEach(article => {
                    newsContainer.innerHTML += createArticleCard(article);
                });
                
                // Update the "has more" status
                hasMore = data.hasMore;
                if (!hasMore) {
                    loadMoreBtn.classList.add('d-none');
                }
                
                // Initialize tooltips for new content
                initializeTooltips();
            } else {
                // No more articles
                hasMore = false;
                loadMoreBtn.classList.add('d-none');
            }
        })
        .catch(error => {
            console.error('Error loading more news:', error);
            // Show error message to user
            const errorAlert = document.createElement('div');
            errorAlert.className = 'alert alert-danger mt-3';
            errorAlert.textContent = 'Failed to load more news. Please try again later.';
            document.getElementById('news-container').appendChild(errorAlert);
        })
        .finally(() => {
            // Reset loading state
            isLoading = false;
            loadMoreBtn.disabled = false;
            loadingSpinner.classList.add('d-none');
        });
}

/**
 * Create HTML for a news article card
 * @param {Object} article - The article data
 * @returns {string} HTML string for the article card
 */
function createArticleCard(article) {
    // Get article data
    const title = article.title || 'No title available';
    const source = article.source?.name || 'Unknown source';
    const url = article.url || '#';
    const publishedAt = article.publishedAt ? new Date(article.publishedAt).toLocaleDateString() : 'Unknown date';
    const description = article.description || 'No description available';
    const biasCategory = article.bias_category || 'Unknown';
    const biasColor = article.bias_color || 'secondary';
    const biasScore = article.bias_score || 0;
    const emotionalWords = article.found_emotional_words || [];
    
    // Create the emotional words display
    let emotionalWordsHtml = '';
    if (emotionalWords.length > 0) {
        emotionalWordsHtml = `
        <div class="mt-1">
            <small class="text-muted">
                Emotional words: 
                ${emotionalWords.map(word => {
                    const type = getWordContribution(word);
                    return `<span class="emotional-word ${type}" data-bs-toggle="tooltip" title="${type} emotional word">${word}</span>`;
                }).join(', ')}
            </small>
        </div>`;
    }
    
    // Create the card HTML
    return `
    <div class="col-md-6 col-lg-4 mb-4">
        <div class="card headline-card h-100">
            <div class="card-header d-flex justify-content-between align-items-center">
                <span class="source-badge text-muted">${source}</span>
                <span class="badge bg-${biasColor} bias-badge">${biasCategory}</span>
            </div>
            <div class="card-body">
                <h5 class="card-title">
                    ${title}
                    ${emotionalWordsHtml}
                </h5>
                <p class="card-text text-truncate">${description}</p>
                <div class="score-explanation mb-3">
                    <small class="text-muted">
                        Bias Score: ${biasScore} 
                        ${emotionalWords.length > 0 ? `(Found: ${emotionalWords.join(', ')})` : ''}
                    </small>
                </div>
                <div class="d-flex justify-content-between align-items-center">
                    <small class="text-muted">${publishedAt}</small>
                    <a href="${url}" target="_blank" class="btn btn-sm btn-outline-primary">Read More</a>
                </div>
            </div>
        </div>
    </div>
    `;
}

/**
 * Initialize Bootstrap tooltips
 */
function initializeTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

/**
 * Determine the contribution type of an emotional word
 * @param {string} word - The emotional word
 * @returns {string} The word contribution category
 */
function getWordContribution(word) {
    // This is a simplified version - the real categorization should match the Python code
    // For a production app, this would be better served from the backend
    const word_lower = word.toLowerCase();
    
    const positiveWords = ['amazing', 'awesome', 'breakthrough', 'brilliant', 'celebrate', 'delight', 
        'excellent', 'extraordinary', 'fantastic', 'remarkable', 'triumph', 'wonderful',
        'victory', 'success', 'happy', 'joyful', 'praise', 'champion', 'perfect',
        'liberate', 'defend', 'protect', 'secure', 'alliance', 'stability', 
        'peace', 'victory', 'breakthrough', 'reclaim', 'courage', 'heroic'];
    
    const negativeWords = ['awful', 'catastrophe', 'crisis', 'devastating', 'disaster', 'horrible', 
        'terrible', 'tragic', 'alarming', 'destroy', 'danger', 'deadly', 'fail', 
        'threat', 'worst', 'panic', 'fear', 'chaos', 'fury', 'outrage', 'slam',
        'invasion', 'attack', 'casualties', 'bombing', 'violence', 'atrocities', 
        'war crime', 'missile', 'strike', 'offensive', 'invasion', 'occupation',
        'regime', 'escalation', 'ultimatum', 'threat'];
    
    const controversialWords = ['controversy', 'controversial', 'allegedly', 'shocking', 'scandal', 
        'outrageous', 'debate', 'clash', 'conflict', 'dispute', 'accused', 
        'polarizing', 'disputed', 'contentious', 'divided',
        'operation', 'incursion', 'conflict', 'tension', 'confrontation', 'dispute',
        'insurgent', 'militant', 'rebel', 'resistance', 'separatist', 'loyalist'];
    
    if (positiveWords.includes(word_lower)) return 'positive';
    if (negativeWords.includes(word_lower)) return 'negative';
    if (controversialWords.includes(word_lower)) return 'controversial';
    
    return 'neutral';
}