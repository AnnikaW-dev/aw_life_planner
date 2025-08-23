// static/js/diary.js
// Diary functionality

/**
 * Setup diary entry search functionality
 */
function setupDiarySearch() {
    const searchInput = document.getElementById('diary-search');
    const entryCards = document.querySelectorAll('.diary-entry-card');

    if (searchInput && entryCards.length > 0) {
        searchInput.addEventListener('input', function() {
            const searchTerm = this.value.toLowerCase();

            entryCards.forEach(card => {
                const title = card.querySelector('.card-title')?.textContent.toLowerCase() || '';
                const content = card.querySelector('.card-text')?.textContent.toLowerCase() || '';

                if (title.includes(searchTerm) || content.includes(searchTerm)) {
                    card.style.display = 'block';
                } else {
                    card.style.display = 'none';
                }
            });
        });
    }
}

/**
 * Setup mood selector functionality
 */
function setupMoodSelector() {
    const moodInputs = document.querySelectorAll('input[name="mood"]');

    moodInputs.forEach(input => {
        input.addEventListener('change', function() {
            // Remove selected class from all labels
            const allLabels = document.querySelectorAll('.mood-option');
            allLabels.forEach(label => label.classList.remove('selected'));

            // Add selected class to current label
            const currentLabel = this.parentElement;
            if (currentLabel) {
                currentLabel.classList.add('selected');
            }
        });
    });
}

/**
 * Setup character counter for diary content
 */
function setupCharacterCounter() {
    const contentTextarea = document.querySelector('textarea[name="content"]');
    const charCounter = document.getElementById('char-counter');

    if (contentTextarea && charCounter) {
        function updateCounter() {
            const count = contentTextarea.value.length;
            charCounter.textContent = `${count} characters`;

            // Change color based on length
            if (count > 500) {
                charCounter.className = 'text-success';
            } else if (count > 100) {
                charCounter.className = 'text-warning';
            } else {
                charCounter.className = 'text-muted';
            }
        }

        contentTextarea.addEventListener('input', updateCounter);
        updateCounter(); // Initial count
    }
}

/**
 * Setup diary entry confirmation for delete
 */
function setupDeleteConfirmation() {
    const deleteButtons = document.querySelectorAll('.btn-delete-entry');

    deleteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            const entryTitle = this.dataset.entryTitle || 'this entry';

            if (!confirm(`Are you sure you want to delete "${entryTitle}"? This action cannot be undone.`)) {
                e.preventDefault();
                return false;
            }
        });
    });
}

/**
 * Initialize diary functionality
 */
function initializeDiary() {
    // Setup search functionality
    setupDiarySearch();

    // Setup mood selector
    setupMoodSelector();

    // Setup character counter
    setupCharacterCounter();

    // Setup delete confirmation
    setupDeleteConfirmation();

    console.log('Diary JS initialized successfully');
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeDiary();
});

console.log('Diary JS loaded successfully');
