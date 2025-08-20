/**
 * Initialize Stripe payment form
 */
function initializeStripeCheckout() {
    // Get Stripe public key and client secret from hidden elements
    const stripePublicKeyElement = document.getElementById('id_stripe_public_key');
    const clientSecretElement = document.getElementById('id_client_secret');

    if (!stripePublicKeyElement || !clientSecretElement) {
        console.error('Stripe configuration not found');
        return;
    }

    const stripePublicKey = stripePublicKeyElement.textContent.slice(1, -1);
    const clientSecret = clientSecretElement.textContent.slice(1, -1);

    if (!stripePublicKey) {
        console.error('Stripe public key is missing');
        showMessage('Payment configuration error. Please contact support.', 'error');
        return;
    }

    // Initialize Stripe
    const stripe = Stripe(stripePublicKey);
    const elements = stripe.elements();

    // Style for Stripe elements
    const style = {
        base: {
            color: '#32325d',
            fontFamily: '"Helvetica Neue", Helvetica, sans-serif',
            fontSmoothing: 'antialiased',
            fontSize: '16px',
            '::placeholder': {
                color: '#aab7c4'
            }
        },
        invalid: {
            color: '#fa755a',
            iconColor: '#fa755a'
        }
    };

    // Create card element
    const card = elements.create('card', {style: style});
    card.mount('#card-element');

    // Handle real-time validation errors
    card.addEventListener('change', function(event) {
        const displayError = document.getElementById('card-errors');
        if (event.error) {
            displayError.textContent = event.error.message;
        } else {
            displayError.textContent = '';
        }
    });

    // Handle form submission
    const form = document.getElementById('payment-form');
    if (form) {
        form.addEventListener('submit', function(ev) {
            ev.preventDefault();

            // Disable button and show spinner
            const submitButton = document.getElementById('submit-button');
            const buttonText = document.getElementById('button-text');
            const loadingSpinner = document.getElementById('loading-spinner');

            if (submitButton) {
                submitButton.disabled = true;
            }

            if (buttonText) {
                buttonText.classList.add('d-none');
            }

            if (loadingSpinner) {
                loadingSpinner.classList.remove('d-none');
            }

            // Confirm payment with Stripe
            stripe.confirmCardPayment(clientSecret, {
                payment_method: {
                    card: card,
                    billing_details: {
                        name: form.full_name ? form.full_name.value : '',
                        email: form.email ? form.email.value : '',
                        phone: form.phone_number ? form.phone_number.value : '',
                    }
                }
            }).then(function(result) {
                if (result.error) {
                    // Show error to customer
                    const errorDiv = document.getElementById('card-errors');
                    if (errorDiv) {
                        errorDiv.textContent = result.error.message;
                    }

                    // Re-enable button
                    if (submitButton) {
                        submitButton.disabled = false;
                    }

                    if (buttonText) {
                        buttonText.classList.remove('d-none');
                    }

                    if (loadingSpinner) {
                        loadingSpinner.classList.add('d-none');
                    }

                    showMessage(result.error.message, 'error');
                } else {
                    // Payment succeeded, submit form
                    if (result.paymentIntent.status === 'succeeded') {
                        form.submit();
                    }
                }
            });
        });
    }
}

/**
 * Setup checkout form validation
 */
function setupCheckoutValidation() {
    setupFormValidation('payment-form', {
        'full_name': {
            required: true,
            minLength: 2,
            message: 'Please enter your full name.'
        },
        'email': {
            required: true,
            pattern: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
            message: 'Please enter a valid email address.'
        },
        'phone_number': {
            required: true,
            minLength: 10,
            message: 'Please enter a valid phone number.'
        }
    });
}

/**
 * Initialize checkout functionality
 */
function initializeCheckout() {
    // Initialize Stripe if on checkout page
    if (document.getElementById('payment-form')) {
        initializeStripeCheckout();
        setupCheckoutValidation();
    }

    console.log('Checkout JS initialized successfully');
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeCheckout();
});

console.log('Checkout JS loaded successfully');
