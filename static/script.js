// Global variables
let currentTab = 'home';
let currentData = {};

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    loadHomeData();
    setupEventListeners();
});

function setupEventListeners() {
    // Search input enter key
    document.getElementById('searchInput').addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            searchAnime();
        }
    });

    // Modal close functionality
    const modal = document.getElementById('animeModal');
    const closeBtn = document.querySelector('.close');
    
    closeBtn.onclick = function() {
        modal.style.display = 'none';
    }
    
    window.onclick = function(event) {
        if (event.target == modal) {
            modal.style.display = 'none';
        }
    }
}

// Tab switching functionality
function switchTab(tabName) {
    // Update tab appearance
    document.querySelectorAll('.tab').forEach(tab => tab.classList.remove('active'));
    event.target.classList.add('active');
    
    // Hide all content sections
    document.getElementById('homeContent').style.display = 'none';
    document.getElementById('listContent').style.display = 'none';
    document.getElementById('searchContent').style.display = 'none';
    
    // Show selected content
    currentTab = tabName;
    
    switch(tabName) {
        case 'home':
            document.getElementById('homeContent').style.display = 'block';
            if (!currentData.home) {
                loadHomeData();
            }
            break;
        case 'list':
            document.getElementById('listContent').style.display = 'block';
            if (!currentData.list) {
                loadAnimeList();
            }
            break;
        case 'search':
            document.getElementById('searchContent').style.display = 'block';
            break;
    }
}

// Load home page data
async function loadHomeData() {
    showLoading('ongoingGrid');
    showLoading('completedGrid');
    showLoading('moviesGrid');
    
    try {
        const response = await fetch('/api/home');
        const data = await response.json();
        
        if (data.error) {
            showError('ongoingGrid', data.error);
            return;
        }
        
        currentData.home = data;
        
        renderAnimeGrid(data.ongoing, 'ongoingGrid');
        renderAnimeGrid(data.completed, 'completedGrid');
        renderAnimeGrid(data.movies, 'moviesGrid');
        
    } catch (error) {
        console.error('Error loading home data:', error);
        showError('ongoingGrid', 'Failed to load data');
        showError('completedGrid', 'Failed to load data');
        showError('moviesGrid', 'Failed to load data');
    }
}

// Load complete anime list
async function loadAnimeList(letter = '') {
    showLoading('animeListGrid');
    
    try {
        const url = letter ? `/api/anime-list?letter=${letter}` : '/api/anime-list';
        const response = await fetch(url);
        const data = await response.json();
        
        if (data.error) {
            showError('animeListGrid', data.error);
            return;
        }
        
        currentData.list = data;
        renderAnimeGrid(data, 'animeListGrid');
        
        // Update active letter button
        document.querySelectorAll('.alphabet-btn').forEach(btn => btn.classList.remove('active'));
        if (letter) {
            document.querySelector(`[onclick="filterByLetter('${letter}')"]`).classList.add('active');
        } else {
            document.querySelector(`[onclick="filterByLetter('')"]`).classList.add('active');
        }
        
    } catch (error) {
        console.error('Error loading anime list:', error);
        showError('animeListGrid', 'Failed to load anime list');
    }
}

// Search anime
async function searchAnime() {
    const query = document.getElementById('searchInput').value.trim();
    
    if (!query) {
        alert('Please enter a search term');
        return;
    }
    
    // Switch to search tab
    switchTab('search');
    showLoading('searchResults');
    
    try {
        const response = await fetch(`/api/search?q=${encodeURIComponent(query)}`);
        const data = await response.json();
        
        if (data.error) {
            showError('searchResults', data.error);
            return;
        }
        
        if (data.length === 0) {
            document.getElementById('searchResults').innerHTML = 
                '<div class="error">No anime found matching your search.</div>';
            return;
        }
        
        renderAnimeGrid(data, 'searchResults');
        
    } catch (error) {
        console.error('Error searching anime:', error);
        showError('searchResults', 'Failed to search anime');
    }
}

// Filter anime list by letter
function filterByLetter(letter) {
    loadAnimeList(letter);
}

// Render anime grid
function renderAnimeGrid(animeList, containerId) {
    const container = document.getElementById(containerId);
    
    if (!animeList || animeList.length === 0) {
        container.innerHTML = '<div class="error">No anime found.</div>';
        return;
    }
    
    const html = animeList.map(anime => `
        <div class="anime-card" onclick="showAnimeDetails('${anime.url}')">
            <div class="anime-title">${escapeHtml(anime.title)}</div>
            <a href="${anime.url}" class="anime-url" target="_blank" onclick="event.stopPropagation()">
                <i class="fas fa-external-link-alt"></i> View Original
            </a>
        </div>
    `).join('');
    
    container.innerHTML = html;
}

// Show anime details in modal
async function showAnimeDetails(url) {
    const modal = document.getElementById('animeModal');
    const modalContent = document.getElementById('modalContent');
    
    modal.style.display = 'block';
    modalContent.innerHTML = '<div class="loading"><i class="fas fa-spinner"></i><br>Loading details...</div>';
    
    try {
        const response = await fetch(`/api/anime-details?url=${encodeURIComponent(url)}`);
        const data = await response.json();
        
        if (data.error) {
            modalContent.innerHTML = `<div class="error">${data.error}</div>`;
            return;
        }
        
        const downloadLinksHtml = data.download_links && data.download_links.length > 0 
            ? `
                <div class="download-links">
                    <h3><i class="fas fa-download"></i> Download Links</h3>
                    ${data.download_links.map(link => `
                        <a href="${link.url}" class="download-link" target="_blank">
                            <i class="fas fa-cloud-download-alt"></i> 
                            ${escapeHtml(link.text)} 
                            <span style="color: #666; font-size: 0.9em;">(${link.type})</span>
                        </a>
                    `).join('')}
                </div>
            `
            : '<div class="error">No download links found.</div>';
        
        modalContent.innerHTML = `
            <h2>${escapeHtml(data.title)}</h2>
            <p><strong>Synopsis:</strong></p>
            <p>${escapeHtml(data.synopsis) || 'No synopsis available.'}</p>
            <p><strong>Source:</strong> <a href="${data.url}" target="_blank">${data.url}</a></p>
            ${downloadLinksHtml}
        `;
        
    } catch (error) {
        console.error('Error loading anime details:', error);
        modalContent.innerHTML = '<div class="error">Failed to load anime details.</div>';
    }
}

// Utility functions
function showLoading(containerId) {
    document.getElementById(containerId).innerHTML = 
        '<div class="loading"><i class="fas fa-spinner"></i><br>Loading...</div>';
}

function showError(containerId, message) {
    document.getElementById(containerId).innerHTML = 
        `<div class="error"><i class="fas fa-exclamation-triangle"></i> ${message}</div>`;
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Auto-refresh functionality (optional)
function enableAutoRefresh() {
    setInterval(() => {
        if (currentTab === 'home') {
            loadHomeData();
        }
    }, 300000); // Refresh every 5 minutes
}
