/**
 * Initialize color picker functionality for any color input
 */
function initializeColorPickers() {
    const colorInputs = document.querySelectorAll('input[type="color"]');

    colorInputs.forEach(colorInput => {
        const colorPreview = document.getElementById('color-preview');

        if (colorInput && colorPreview) {
            // Update color preview when color changes
            colorInput.addEventListener('input', function() {
                colorPreview.style.backgroundColor = this.value;
            });

            // Set initial color
            colorPreview.style.backgroundColor = colorInput.value;
        }
    });
}

/**
 * Generic form validation
 * @param {string} formId - ID of the form to validate
 * @param {Object} rules - Validation rules object
 */
function setupFormValidation(formId, rules) {
    const form = document.getElementById(formId);

    if (form) {
        form.addEventListener('submit', function(e) {
            let isValid = true;

            // Check each validation rule
            for (const [fieldName, rule] of Object.entries(rules)) {
                const field = form.querySelector(`[name="${fieldName}"]`);

                if (field) {
                    if (rule.required && !field.value.trim()) {
                        e.preventDefault();
                        field.focus();
                        showMessage(rule.message || `${fieldName} is required.`, 'warning');
                        isValid = false;
                        break;
                    }

                    if (rule.minLength && field.value.trim().length < rule.minLength) {
                        e.preventDefault();
                        field.focus();
                        showMessage(rule.message || `${fieldName} must be at least ${rule.minLength} characters long.`, 'warning');
                        isValid = false;
                        break;
                    }

                    if (rule.pattern && !rule.pattern.test(field.value)) {
                        e.preventDefault();
                        field.focus();
                        showMessage(rule.message || `${fieldName} format is invalid.`, 'warning');
                        isValid = false;
                        break;
                    }
                }
            }

            return isValid;
        });
    }
}

/**
 * Setup habit form validation specifically
 */
function setupHabitFormValidation() {
    setupFormValidation('habit-form', {
        'habit_name': {
            required: true,
            minLength: 2,
            message: 'Habit name must be at least 2 characters long.'
        }
    });
}

/**
 * Setup diary form validation
 */
function setupDiaryFormValidation() {
    setupFormValidation('diary-form', {
        'title': {
            required: true,
            minLength: 3,
            message: 'Title must be at least 3 characters long.'
        },
        'content': {
            required: true,
            minLength: 10,
            message: 'Content must be at least 10 characters long.'
        }
    });
}

/**
 * Auto-resize textareas
 */
function setupAutoResizeTextareas() {
    const textareas = document.querySelectorAll('textarea');

    textareas.forEach(textarea => {
        // Set initial height
        textarea.style.height = 'auto';
        textarea.style.height = textarea.scrollHeight + 'px';

        // Add resize listener
        textarea.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = this.scrollHeight + 'px';
        });
    });
}

/**
 * Initialize all form functionality
 */
function initializeForms() {
    // Initialize color pickers
    initializeColorPickers();

    // Setup form validations
    setupHabitFormValidation();
    setupDiaryFormValidation();

    // Setup auto-resize textareas
    setupAutoResizeTextareas();

    console.log('Forms JS initialized successfully');
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeForms();
});

console.log('Forms JS loaded successfully');
