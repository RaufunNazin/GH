// Girls' Hall Search Portal JavaScript

let currentLanguage = 'en';
let allData = [];
let currentResults = [];
let contactStatus = {};

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    loadData();
    setupEventListeners();
});

// Load data from the API
async function loadData() {
    try {
        const response = await fetch('/api/data');
        if (response.ok) {
            allData = await response.json();
            console.log(`Loaded ${allData.length} records`);
        } else {
            showError('Failed to load data from server');
        }
    } catch (error) {
        console.error('Error loading data:', error);
        showError('Error connecting to server');
    }
}

// Generate unique ID for a record
function getRecordId(record) {
    return `${record.Name || ''}_${record.Contact || ''}_${record.Email || ''}`;
}

// Update contact status
async function updateContactStatus(recordId, status) {
    try {
        const response = await fetch('/api/contact-status', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                record_id: recordId,
                status: status
            })
        });
        
        if (response.ok) {
            contactStatus[recordId] = status;
            return true;
        } else {
            console.error('Failed to update contact status');
            return false;
        }
    } catch (error) {
        console.error('Error updating contact status:', error);
        return false;
    }
}

// Get contact status for a record
async function getContactStatus(recordId) {
    try {
        const response = await fetch(`/api/contact-status/${encodeURIComponent(recordId)}`);
        if (response.ok) {
            const data = await response.json();
            return data.status;
        }
        return 'not_contacted';
    } catch (error) {
        console.error('Error getting contact status:', error);
        return 'not_contacted';
    }
}

// Setup event listeners
function setupEventListeners() {
    const searchInput = document.getElementById('searchInput');
    
    // Search on input with debouncing
    let searchTimeout;
    searchInput.addEventListener('input', function() {
        clearTimeout(searchTimeout);
        searchTimeout = setTimeout(() => {
            const query = this.value.trim();
            if (query.length >= 2) {
                showSuggestions(query);
            } else {
                hideSuggestions();
            }
        }, 300);
    });
    
    // Search on Enter key
    searchInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            performSearch();
        }
    });
    
    // Hide suggestions when clicking outside
    document.addEventListener('click', function(e) {
        if (!e.target.closest('.search-container')) {
            hideSuggestions();
        }
    });
}

// Perform search
async function performSearch() {
    const query = document.getElementById('searchInput').value.trim();
    
    if (!query) {
        showError('Please enter a search term');
        return;
    }
    
    showLoading();
    hideSuggestions();
    
    try {
        const response = await fetch(`/api/search?q=${encodeURIComponent(query)}`);
        if (response.ok) {
            currentResults = await response.json();
            displayResults(currentResults, query);
        } else {
            showError('Search failed. Please try again.');
        }
    } catch (error) {
        console.error('Search error:', error);
        showError('Error performing search');
    } finally {
        hideLoading();
    }
}

// Show search suggestions
function showSuggestions(query) {
    if (allData.length === 0) return;
    
    const suggestions = [];
    const queryLower = query.toLowerCase();
    
    // Find matching records
    allData.forEach(record => {
        Object.values(record).forEach(value => {
            if (typeof value === 'string' && value.toLowerCase().includes(queryLower)) {
                // Find the field that matches
                Object.entries(record).forEach(([key, val]) => {
                    if (typeof val === 'string' && val.toLowerCase().includes(queryLower)) {
                        suggestions.push({
                            text: val,
                            field: key,
                            record: record
                        });
                    }
                });
            }
        });
    });
    
    // Remove duplicates and limit to 10
    const uniqueSuggestions = suggestions
        .filter((suggestion, index, self) => 
            index === self.findIndex(s => s.text === suggestion.text)
        )
        .slice(0, 10);
    
    displaySuggestions(uniqueSuggestions);
}

// Display suggestions
function displaySuggestions(suggestions) {
    const container = document.getElementById('searchSuggestions');
    
    if (suggestions.length === 0) {
        hideSuggestions();
        return;
    }
    
    container.innerHTML = suggestions.map(suggestion => `
        <div class="suggestion-item" onclick="selectSuggestion('${suggestion.text.replace(/'/g, "\\'")}')">
            <div class="fw-bold">${suggestion.text}</div>
            <small class="text-muted">${suggestion.field}</small>
        </div>
    `).join('');
    
    container.style.display = 'block';
}

// Select suggestion
function selectSuggestion(text) {
    document.getElementById('searchInput').value = text;
    hideSuggestions();
    performSearch();
}

// Hide suggestions
function hideSuggestions() {
    document.getElementById('searchSuggestions').style.display = 'none';
}

// Display search results
function displayResults(results, query) {
    const container = document.getElementById('resultsContainer');
    const content = document.getElementById('resultsContent');
    const title = document.getElementById('resultsTitle');
    const noResults = document.getElementById('noResults');
    
    // Hide all result containers
    container.classList.add('d-none');
    noResults.classList.add('d-none');
    
    if (results.length === 0) {
        noResults.classList.remove('d-none');
        noResults.classList.add('fade-in');
        return;
    }
    
    title.textContent = `Search Results for "${query}" (${results.length} found)`;
    
    // Get column names for display
    const columns = Object.keys(results[0] || {});
    
    content.innerHTML = results.map((record, index) => `
        <div class="result-card fade-in" style="animation-delay: ${index * 0.1}s" id="card-${index}">
            <div class="card-header d-flex justify-content-between align-items-center">
                <h5 class="mb-0">
                    <i class="fas fa-building me-2"></i>
                    Record ${index + 1}
                </h5>
                <div class="btn-group">
                    <button class="btn btn-outline-primary btn-sm" onclick="showDetails(${index})">
                        <i class="fas fa-eye me-1"></i>
                        View Details
                    </button>
                </div>
            </div>
            <div class="card-body">
                <div class="row">
                    ${columns.map(column => `
                        <div class="col-md-6 mb-2">
                            <div class="field-item">
                                <span class="field-label">${formatFieldName(column)}:</span>
                                <span class="field-value">${formatValue(record[column], column)}</span>
                            </div>
                        </div>
                    `).join('')}
                </div>
                <div class="contact-tracking mt-3 pt-3 border-top">
                    <div class="d-flex justify-content-between align-items-center">
                        <span class="contact-status-text">
                            <i class="fas fa-phone me-1"></i>
                            Contact Status: <span id="status-${index}" class="status-badge">Loading...</span>
                        </span>
                        <div class="btn-group">
                            <button class="btn btn-success btn-sm" onclick="markAsContacted(${index})" id="contact-btn-${index}">
                                <i class="fas fa-check me-1"></i>
                                Mark as Contacted
                            </button>
                            <button class="btn btn-warning btn-sm" onclick="resetContact(${index})" id="reset-btn-${index}" style="display: none;">
                                <i class="fas fa-undo me-1"></i>
                                Reset
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `).join('');
    
    // Load contact status for each record
    results.forEach((record, index) => {
        loadContactStatusForRecord(record, index);
    });
    
    container.classList.remove('d-none');
    container.classList.add('fade-in');
}

// Show detailed view in modal
function showDetails(index) {
    const record = currentResults[index];
    const modalBody = document.getElementById('modalBody');
    
    modalBody.innerHTML = Object.entries(record).map(([key, value]) => `
        <div class="field-item mb-3">
            <div class="field-label">${formatFieldName(key)}:</div>
            <div class="field-value">${formatValue(value, key)}</div>
        </div>
    `).join('');
    
    const modal = new bootstrap.Modal(document.getElementById('detailModal'));
    modal.show();
}

// Format field names for display
function formatFieldName(fieldName) {
    // Custom formatting for specific fields
    const fieldMappings = {
        'Contact': '📞 Contact',
        'Department': '🏛️ Department',
        'Email': '📧 Email',
        'Hall Name': '🏢 Hall Name',
        'Name': '👤 Name',
        'Year': '📅 Year'
    };
    
    return fieldMappings[fieldName] || fieldName
        .replace(/([A-Z])/g, ' $1')
        .replace(/^./, str => str.toUpperCase())
        .trim();
}

// Format values for display
function formatValue(value, fieldName) {
    if (value === null || value === undefined) {
        return '<span class="text-muted">Not available</span>';
    }
    
    if (typeof value === 'string' && value.trim() === '') {
        return '<span class="text-muted">Empty</span>';
    }
    
    const stringValue = String(value);
    
    // Special formatting for specific fields
    if (fieldName === 'Email' && stringValue.includes('@')) {
        return `<a href="mailto:${escapeHtml(stringValue)}" class="text-primary">${escapeHtml(stringValue)}</a>`;
    }
    
    if (fieldName === 'Contact' && /^\d+$/.test(stringValue.replace(/\s+/g, ''))) {
        return `<a href="tel:${escapeHtml(stringValue)}" class="text-success">${escapeHtml(stringValue)}</a>`;
    }
    
    // Check if the value contains Bengali text
    const hasBengali = /[\u0980-\u09FF]/.test(stringValue);
    if (hasBengali) {
        return `<span class="bengali-text">${escapeHtml(stringValue)}</span>`;
    }
    
    return escapeHtml(stringValue);
}

// Escape HTML to prevent XSS
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Clear results
function clearResults() {
    document.getElementById('searchInput').value = '';
    document.getElementById('resultsContainer').classList.add('d-none');
    document.getElementById('noResults').classList.add('d-none');
    currentResults = [];
}

// Export results
function exportResults() {
    if (currentResults.length === 0) {
        showError('No results to export');
        return;
    }
    
    const csv = convertToCSV(currentResults);
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    
    if (link.download !== undefined) {
        const url = URL.createObjectURL(blob);
        link.setAttribute('href', url);
        link.setAttribute('download', 'hall_search_results.csv');
        link.style.visibility = 'hidden';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    }
}

// Convert data to CSV
function convertToCSV(data) {
    if (data.length === 0) return '';
    
    const headers = Object.keys(data[0]);
    const csvContent = [
        headers.join(','),
        ...data.map(row => 
            headers.map(header => {
                const value = row[header];
                return typeof value === 'string' && value.includes(',') 
                    ? `"${value.replace(/"/g, '""')}"` 
                    : value;
            }).join(',')
        )
    ].join('\n');
    
    return csvContent;
}

// Toggle language (placeholder for future multilingual support)
function toggleLanguage() {
    currentLanguage = currentLanguage === 'en' ? 'bn' : 'en';
    const langText = document.getElementById('lang-text');
    langText.textContent = currentLanguage === 'en' ? 'বাংলা' : 'English';
    
    // Here you could implement language switching logic
    console.log('Language switched to:', currentLanguage);
}

// Show loading spinner
function showLoading() {
    document.getElementById('loadingSpinner').classList.remove('d-none');
}

// Hide loading spinner
function hideLoading() {
    document.getElementById('loadingSpinner').classList.add('d-none');
}

// Show error message
function showError(message) {
    // Create a simple alert for now
    alert(message);
    // You could implement a more sophisticated notification system here
}

// Load contact status for a specific record
async function loadContactStatusForRecord(record, index) {
    const recordId = getRecordId(record);
    const status = await getContactStatus(recordId);
    updateContactStatusUI(index, status);
}

// Update contact status UI
function updateContactStatusUI(index, status) {
    const statusElement = document.getElementById(`status-${index}`);
    const contactBtn = document.getElementById(`contact-btn-${index}`);
    const resetBtn = document.getElementById(`reset-btn-${index}`);
    
    if (statusElement && contactBtn && resetBtn) {
        if (status === 'contacted') {
            statusElement.textContent = 'Contacted';
            statusElement.className = 'status-badge badge bg-success';
            contactBtn.style.display = 'none';
            resetBtn.style.display = 'inline-block';
        } else {
            statusElement.textContent = 'Not Contacted';
            statusElement.className = 'status-badge badge bg-secondary';
            contactBtn.style.display = 'inline-block';
            resetBtn.style.display = 'none';
        }
    }
}

// Mark record as contacted
async function markAsContacted(index) {
    const record = currentResults[index];
    const recordId = getRecordId(record);
    
    const success = await updateContactStatus(recordId, 'contacted');
    if (success) {
        updateContactStatusUI(index, 'contacted');
        showSuccessMessage('Marked as contacted successfully!');
    } else {
        showError('Failed to update contact status');
    }
}

// Reset contact status
async function resetContact(index) {
    const record = currentResults[index];
    const recordId = getRecordId(record);
    
    const success = await updateContactStatus(recordId, 'not_contacted');
    if (success) {
        updateContactStatusUI(index, 'not_contacted');
        showSuccessMessage('Contact status reset successfully!');
    } else {
        showError('Failed to reset contact status');
    }
}

// Show success message
function showSuccessMessage(message) {
    // Create a simple success notification
    const notification = document.createElement('div');
    notification.className = 'alert alert-success alert-dismissible fade show position-fixed';
    notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(notification);
    
    // Auto remove after 3 seconds
    setTimeout(() => {
        if (notification.parentNode) {
            notification.parentNode.removeChild(notification);
        }
    }, 3000);
}

// Utility function to debounce
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}
