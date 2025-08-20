// static/js/habit-tracker.js
// Habit tracker functionality

/**
 * Toggle habit completion for today
 * @param {number} habitId - ID of the habit to toggle
 */
function toggleHabit(habitId) {
    const button = document.getElementById(`toggle-btn-${habitId}`);
    const icon = document.getElementById(`toggle-icon-${habitId}`);
    const text = document.getElementById(`toggle-text-${habitId}`);
    const streak = document.getElementById(`streak-${habitId}`);

    if (!button) {
        console.error(`Button not found for habit ${habitId}`);
        return;
    }

    // Disable button temporarily
    button.disabled = true;

    fetch(`/modules/habit-tracker/toggle/${habitId}/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
            'X-Requested-With': 'XMLHttpRequest',
            'Content-Type': 'application/json',
        }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        if (data.success) {
            // Update button appearance
            if (data.completed) {
                button.className = 'btn btn-lg habit-toggle-btn btn-success';
                if (icon) icon.className = 'fas fa-check-circle me-2';
                if (text) text.textContent = 'Completed!';
            } else {
                button.className = 'btn btn-lg habit-toggle-btn btn-outline-success';
                if (icon) icon.className = 'fas fa-circle me-2';
                if (text) text.textContent = 'Mark Done';
            }

            // Update streak
            if (streak) {
                streak.textContent = data.streak;
            }

            // Show success animation
            button.style.transform = 'scale(0.95)';
            setTimeout(() => {
                button.style.transform = 'scale(1)';
            }, 150);

            // Show success message using global function
            if (typeof showMessage === 'function') {
                showMessage(data.message, 'success');
            } else {
                alert(data.message);
            }
        } else {
            if (typeof showMessage === 'function') {
                showMessage(data.message || 'Failed to update habit.', 'error');
            } else {
                alert(data.message || 'Failed to update habit.');
            }
        }
    })
    .catch(error => {
        console.error('Error:', error);
        if (typeof showMessage === 'function') {
            showMessage('Something went wrong. Please try again.', 'error');
        } else {
            alert('Something went wrong. Please try again.');
        }
    })
    .finally(() => {
        button.disabled = false;
    });
}

/**
 * Initialize color picker functionality for habit forms
 */
function initializeColorPicker() {
    const colorInput = document.querySelector('input[type="color"]');
    const colorPreview = document.getElementById('color-preview');

    if (colorInput && colorPreview) {
        // Update color preview when color changes
        colorInput.addEventListener('input', function() {
            colorPreview.style.backgroundColor = this.value;
        });

        // Set initial color
        colorPreview.style.backgroundColor = colorInput.value;
    }
}

/**
 * Validate habit form before submission
 * @param {Event} e - Form submit event
 */
function validateHabitForm(e) {
    const habitNameInput = document.querySelector('input[name="habit_name"]');

    if (habitNameInput && habitNameInput.value.trim().length < 2) {
        e.preventDefault();
        habitNameInput.focus();

        if (typeof showMessage === 'function') {
            showMessage('Habit name must be at least 2 characters long.', 'warning');
        } else {
            alert('Habit name must be at least 2 characters long.');
        }
        return false;
    }

    return true;
}

/**
 * Initialize habit tracker functionality
 */
function initializeHabitTracker() {
    // Prevent duplicate initialization
    if (window.habitTrackerInitialized) {
        return;
    }
    window.habitTrackerInitialized = true;

    // Initialize color picker if on habit form page
    initializeColorPicker();

    // Add form validation if habit form exists
    const habitForm = document.getElementById('habit-form');
    if (habitForm) {
        habitForm.addEventListener('submit', validateHabitForm);
    }

    // Setup habit toggle buttons
    const toggleButtons = document.querySelectorAll('.habit-toggle-btn');
    toggleButtons.forEach(button => {
        button.addEventListener('click', function() {
            const habitCard = this.closest('.habit-card');
            if (habitCard) {
                const habitId = habitCard.dataset.habitId;
                if (habitId) {
                    toggleHabit(parseInt(habitId));
                }
            }
        });
    });

    console.log('Habit tracker functionality initialized');
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeHabitTracker();
});

console.log('Habit Tracker JS loaded successfully');
