// static/js/cart.js
// Shopping cart functionality

/**
 * Remove individual item from cart
 * @param {number} moduleId - ID of the module to remove
 * @param {string} moduleName - Name of the module for confirmation
 */
function removeFromCart(moduleId, moduleName) {
    if (confirm(`Are you sure you want to remove "${moduleName}" from your cart?`)) {
        fetch(`/shop/remove-from-cart/${moduleId}/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
                'X-Requested-With': 'XMLHttpRequest',
                'Content-Type': 'application/json',
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Remove the row with animation
                const row = document.getElementById(`cart-item-${moduleId}`);
                if (row) {
                    row.style.transition = 'opacity 0.3s ease';
                    row.style.opacity = '0';
                    setTimeout(() => row.remove(), 300);
                }

                // Update cart count and totals
                updateCartDisplay(data);

                // Show success message using global function
                showMessage('Item removed from cart successfully!', 'success');

                // If cart is empty, reload page to show empty cart message
                if (data.cart_count === 0) {
                    setTimeout(() => location.reload(), 500);
                }
            } else {
                showMessage(data.message || 'Failed to remove item.', 'error');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showMessage('Something went wrong. Please try again.', 'error');
        });
    }
}

/**
 * Clear entire cart
 */
function clearCart() {
    if (confirm('Are you sure you want to clear your entire cart?')) {
        fetch('/shop/clear-cart/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
                'X-Requested-With': 'XMLHttpRequest',
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showMessage('Cart cleared successfully!', 'success');
                setTimeout(() => location.reload(), 500);
            } else {
                showMessage(data.message || 'Failed to clear cart.', 'error');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showMessage('Something went wrong. Please try again.', 'error');
        });
    }
}

/**
 * Update cart display elements
 * @param {Object} data - Response data with cart count and total
 */
function updateCartDisplay(data) {
    // Update cart count
    const cartCountEl = document.getElementById('cart-count');
    if (cartCountEl) {
        cartCountEl.textContent = data.cart_count;
    }

    // Update subtotal and total
    const subtotalEl = document.getElementById('cart-subtotal');
    const totalEl = document.getElementById('cart-total');

    if (subtotalEl) {
        subtotalEl.textContent = `${data.cart_total.toFixed(2)}`;
    }

    if (totalEl) {
        totalEl.textContent = `${data.cart_total.toFixed(2)}`;
    }

    // Update navbar cart badge
    const navCartBadge = document.querySelector('.navbar .cart-badge');
    if (navCartBadge) {
        navCartBadge.textContent = data.cart_count;
        navCartBadge.style.display = data.cart_count > 0 ? 'inline' : 'none';
    }
}

/**
 * Setup cart functionality when page loads
 */
function initializeCart() {
    // Setup remove buttons
    const removeButtons = document.querySelectorAll('.btn-remove-item');
    removeButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const moduleId = this.dataset.moduleId;
            const moduleName = this.dataset.moduleName;
            removeFromCart(moduleId, moduleName);
        });
    });

    // Setup clear cart button
    const clearButton = document.querySelector('.btn-clear-cart');
    if (clearButton) {
        clearButton.addEventListener('click', function(e) {
            e.preventDefault();
            clearCart();
        });
    }

    console.log('Cart functionality initialized');
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeCart();
});

console.log('Cart JS loaded successfully');
