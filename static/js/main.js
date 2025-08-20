/**
 * Get CSRF token from cookies
 * @param {string} name - Cookie name
 * @returns {string|null} - Cookie value
 */
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

/**
 * Enhanced message function with different colors and icons
 * @param {string} message - Message to display
 * @param {string} type - Message type (success, error, warning, info, primary, secondary)
 */
function showMessage(message, type) {
    // Map message types to Bootstrap alert classes
    const alertClasses = {
        'success': 'alert-success',    // Green - for successful actions
        'error': 'alert-danger',       // Red - for errors
        'warning': 'alert-warning',    // Yellow - for warnings
        'info': 'alert-info',          // Blue - for information
        'primary': 'alert-primary',    // Primary blue
        'secondary': 'alert-secondary', // Gray
        'debug': 'alert-secondary'     // Gray for debug
    };

    // Get the appropriate alert class, default to info if type not found
    const alertClass = alertClasses[type] || 'alert-info';

    // Add appropriate icon based on message type
    const icons = {
        'success': '<i class="fas fa-check-circle me-2"></i>',
        'error': '<i class="fas fa-exclamation-triangle me-2"></i>',
        'warning': '<i class="fas fa-exclamation-circle me-2"></i>',
        'info': '<i class="fas fa-info-circle me-2"></i>',
        'primary': '<i class="fas fa-bell me-2"></i>',
        'secondary': '<i class="fas fa-comment me-2"></i>',
        'debug': '<i class="fas fa-bug me-2"></i>'
    };

    const icon = icons[type] || icons['info'];

    const alertHtml = `
        <div class="alert ${alertClass} alert-dismissible fade show" role="alert">
            ${icon}${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;

    // Insert at top of main container
    const container = document.querySelector('main.container');
    if (container) {
        container.insertAdjacentHTML('afterbegin', alertHtml);
    }

    // Auto-dismiss after 4 seconds
    setTimeout(() => {
        const alert = document.querySelector('.alert');
        if (alert) {
            alert.classList.remove('show');
            setTimeout(() => alert.remove(), 300);
        }
    }, 4000);
}

/*
  Auto-dismiss Django messages after page load
 */
function autoDismissMessages() {
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            if (alert && alert.classList.contains('show')) {
                alert.classList.remove('show');
                setTimeout(() => {
                    if (alert.parentNode) {
                        alert.remove();
                    }
                }, 300);
            }
        }, 5000);
    });
}

/*
  Initialize global functionality when DOM is loaded
 */
document.addEventListener('DOMContentLoaded', function() {
    // Auto-dismiss messages
    autoDismissMessages();

    // Initialize any other global functionality here
    console.log('AW Life Planner JS loaded successfully');
});
