/**
 * SmartSafi - Smart City Management System
 * Main JavaScript File
 */

// Configuration
const config = {
    apiBaseUrl: '/api/v1',
    refreshInterval: 30000, // 30 seconds
    mapCenter: [32.2994, -9.2372], // Safi coordinates
    defaultZoom: 13
};

// DOM Ready
document.addEventListener('DOMContentLoaded', function() {
    // Initialize all modules
    initTooltips();
    initAutoRefresh();
    initConfirmations();
    initFlashMessages();
    
    // Initialize page-specific modules
    if (document.getElementById('dashboard-charts')) {
        initDashboardCharts();
    }
    
    if (document.getElementById('map-container')) {
        initMap();
    }
    
    if (document.querySelector('.data-table')) {
        initDataTables();
    }
});

/**
 * Initialize Bootstrap tooltips
 */
function initTooltips() {
    const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    tooltipTriggerList.forEach(function(tooltipTriggerEl) {
        new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

/**
 * Initialize auto-refresh for real-time data
 */
function initAutoRefresh() {
    const refreshElements = document.querySelectorAll('[data-refresh]');
    
    refreshElements.forEach(function(element) {
        const url = element.dataset.refresh;
        const interval = parseInt(element.dataset.interval) || config.refreshInterval;
        
        setInterval(function() {
            refreshElement(element, url);
        }, interval);
    });
}

/**
 * Refresh a single element with new data
 */
function refreshElement(element, url) {
    fetch(url)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                updateElementContent(element, data);
            }
        })
        .catch(error => console.error('Refresh error:', error));
}

/**
 * Update element content with new data
 */
function updateElementContent(element, data) {
    // Update based on element type
    if (element.classList.contains('stats-number')) {
        animateNumber(element, data.value);
    } else if (element.tagName === 'TABLE') {
        updateTable(element, data.data);
    } else {
        element.innerHTML = data.html || data.value;
    }
}

/**
 * Animate number change
 */
function animateNumber(element, newValue) {
    const oldValue = parseInt(element.textContent) || 0;
    const duration = 1000;
    const startTime = performance.now();
    
    function updateNumber(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);
        const current = Math.floor(oldValue + (newValue - oldValue) * progress);
        
        element.textContent = current;
        
        if (progress < 1) {
            requestAnimationFrame(updateNumber);
        }
    }
    
    requestAnimationFrame(updateNumber);
}

/**
 * Initialize confirmation dialogs
 */
function initConfirmations() {
    document.querySelectorAll('[data-confirm]').forEach(function(element) {
        element.addEventListener('click', function(e) {
            const message = this.dataset.confirm || 'Êtes-vous sûr ?';
            if (!confirm(message)) {
                e.preventDefault();
                e.stopPropagation();
            }
        });
    });
}

/**
 * Initialize flash message auto-dismiss
 */
function initFlashMessages() {
    const alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            const closeButton = alert.querySelector('.btn-close');
            if (closeButton) {
                closeButton.click();
            }
        }, 5000);
    });
}

/**
 * Initialize dashboard charts
 */
function initDashboardCharts() {
    // Chart.js configuration
    if (typeof Chart !== 'undefined') {
        // Waste fill levels chart
        const wasteCtx = document.getElementById('waste-chart');
        if (wasteCtx) {
            new Chart(wasteCtx, {
                type: 'doughnut',
                data: {
                    labels: ['Vide', 'Partiel', 'Plein', 'Critique'],
                    datasets: [{
                        data: [30, 45, 15, 10],
                        backgroundColor: ['#10b981', '#3b82f6', '#f59e0b', '#ef4444']
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        legend: {
                            position: 'bottom'
                        }
                    }
                }
            });
        }
        
        // Water quality chart
        const waterCtx = document.getElementById('water-chart');
        if (waterCtx) {
            new Chart(waterCtx, {
                type: 'line',
                data: {
                    labels: ['Lun', 'Mar', 'Mer', 'Jeu', 'Ven', 'Sam', 'Dim'],
                    datasets: [{
                        label: 'pH',
                        data: [7.2, 7.1, 7.3, 7.2, 7.4, 7.3, 7.2],
                        borderColor: '#3b82f6',
                        tension: 0.4
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        legend: {
                            display: false
                        }
                    },
                    scales: {
                        y: {
                            min: 6,
                            max: 8
                        }
                    }
                }
            });
        }
        
        // Air quality chart
        const airCtx = document.getElementById('air-chart');
        if (airCtx) {
            new Chart(airCtx, {
                type: 'bar',
                data: {
                    labels: ['PM2.5', 'PM10', 'O3', 'NO2', 'SO2', 'CO'],
                    datasets: [{
                        label: 'Concentration (µg/m³)',
                        data: [15, 25, 45, 20, 5, 0.5],
                        backgroundColor: [
                            '#3b82f6',
                            '#10b981',
                            '#f59e0b',
                            '#ef4444',
                            '#8b5cf6',
                            '#ec4899'
                        ]
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        legend: {
                            display: false
                        }
                    }
                }
            });
        }
    }
}

/**
 * Initialize map (Leaflet)
 */
function initMap() {
    if (typeof L !== 'undefined') {
        const mapContainer = document.getElementById('map-container');
        if (mapContainer) {
            const map = L.map('map-container').setView(config.mapCenter, config.defaultZoom);
            
            L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                attribution: '© OpenStreetMap contributors'
            }).addTo(map);
            
            // Add markers from data
            const markers = document.querySelectorAll('[data-marker]');
            markers.forEach(function(marker) {
                const lat = parseFloat(marker.dataset.lat);
                const lng = parseFloat(marker.dataset.lng);
                const title = marker.dataset.title;
                const type = marker.dataset.type;
                
                let iconColor = 'blue';
                if (type === 'waste') iconColor = 'green';
                else if (type === 'water') iconColor = 'blue';
                else if (type === 'air') iconColor = 'gray';
                else if (type === 'agriculture') iconColor = 'orange';
                else if (type === 'lighting') iconColor = 'yellow';
                
                const customIcon = L.divIcon({
                    className: 'custom-marker',
                    html: `<i class="fas fa-map-marker-alt" style="color: ${iconColor}; font-size: 24px;"></i>`,
                    iconSize: [24, 24],
                    iconAnchor: [12, 24]
                });
                
                L.marker([lat, lng], { icon: customIcon })
                    .addTo(map)
                    .bindPopup(`<b>${title}</b>`);
            });
        }
    }
}

/**
 * Initialize DataTables
 */
function initDataTables() {
    if (typeof $.fn.DataTable !== 'undefined') {
        $('.data-table').DataTable({
            responsive: true,
            pageLength: 25,
            language: {
                url: '//cdn.datatables.net/plug-ins/1.13.4/i18n/fr-FR.json'
            }
        });
    }
}

/**
 * Utility Functions
 */

// Format number with locale
function formatNumber(num, decimals = 0) {
    return num.toLocaleString('fr-FR', {
        minimumFractionDigits: decimals,
        maximumFractionDigits: decimals
    });
}

// Format date
function formatDate(date, options = {}) {
    const d = new Date(date);
    return d.toLocaleDateString('fr-FR', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
        ...options
    });
}

// Format datetime
function formatDateTime(date) {
    return formatDate(date, {
        hour: '2-digit',
        minute: '2-digit'
    });
}

// Show loading spinner
function showLoading(element) {
    element.innerHTML = '<div class="spinner"></div>';
}

// Hide loading spinner
function hideLoading(element, content) {
    element.innerHTML = content;
}

// Debounce function
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

// Throttle function
function throttle(func, limit) {
    let inThrottle;
    return function(...args) {
        if (!inThrottle) {
            func.apply(this, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

// Export functions for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        config,
        formatNumber,
        formatDate,
        formatDateTime,
        showLoading,
        hideLoading,
        debounce,
        throttle
    };
}
