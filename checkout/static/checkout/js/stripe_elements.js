**
 * Enhanced Stripe Elements for Checkout
 * Core Logic/payment flow inspired by Stripe documentation
 */

// Get Stripe configuration safely
function getStripeConfig() {
    try {
        const publicKeyElement = document.getElementById('id_stripe_public_key');
        const clientSecretElement = document.getElementById('id_client_secret');

        if (!publicKeyElement || !clientSecretElement) {
            throw new Error('Stripe configuration not found');
        }

        return {
            publicKey: JSON.parse(publicKeyElement.textContent),
            clientSecret: JSON.parse(clientSecretElement.textContent)
        };
    } catch (error) {
        console.error('Error getting Stripe configuration:', error);
        showErrorMessage('Payment configuration error. Please refresh the page.');
        return null;
    }
}

// Show error message to user
function showErrorMessage(message) {
    const errorDiv = document.getElementById('card-errors');
    if (errorDiv) {
        errorDiv.textContent = message;
    }

    // Also show with global message system if available
    if (typeof showMessage === 'function') {
        showMessage(message, 'error');
    }
}

// Initialize Stripe
const config = getStripeConfig();
if (!config) {
    // Stop execution if configuration is missing
    console.error('Cannot initialize Stripe - missing configuration');
} else {
    const stripe = Stripe(config.publicKey);
    const elements = stripe.elements();

    // Create card element with enhanced styling
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

    // Get form elements
    const form = document.getElementById('payment-form');
    const submitButton = document.getElementById('submit-button');
    const buttonText = document.getElementById('button-text');
    const loadingSpinner = document.getElementById('loading-spinner');

    if (!form || !submitButton) {
        console.error('Required form elements not found');
    } else {
        // Handle form submission
        form.addEventListener('submit', function(ev) {
            ev.preventDefault();

            // Validate form first
            if (!validateForm()) {
                return;
            }

            // Disable button and show spinner
            setSubmitButtonState(true);

            stripe.confirmCardPayment(config.clientSecret, {
                payment_method: {
                    card: card,
                    billing_details: {
                        name: form.full_name.value.trim(),
                        email: form.email.value.trim(),
                        phone: form.phone_number.value.trim(),
                    }
                }
            }).then(function(result) {
                if (result.error) {
                    // Show error to customer
                    showErrorMessage(result.error.message);
                    setSubmitButtonState(false);
                } else {
                    // Payment succeeded
                    if (result.paymentIntent.status === 'succeeded') {
                        // Add payment intent ID to form
                        const paymentIntentInput = document.createElement('input');
                        paymentIntentInput.type = 'hidden';
                        paymentIntentInput.name = 'payment_intent_id';
                        paymentIntentInput.value = result.paymentIntent.id;
                        form.appendChild(paymentIntentInput);

                        // Show success message briefly
                        if (typeof showMessage === 'function') {
                            showMessage('Payment successful! Processing your order...', 'success');
                        }

                        // Submit the form
                        form.submit();
                    } else {
                        showErrorMessage('Payment was not completed. Please try again.');
                        setSubmitButtonState(false);
                    }
                }
            }).catch(function(error) {
                console.error('Payment processing error:', error);
                showErrorMessage('An error occurred processing your payment. Please try again.');
                setSubmitButtonState(false);
            });
        });
    }

    /**
     * Set submit button loading state
     * @param {boolean} loading - Whether button should show loading state
     */
    function setSubmitButtonState(loading) {
        if (submitButton) {
            submitButton.disabled = loading;
        }

        if (buttonText) {
            buttonText.style.display = loading ? 'none' : 'inline';
        }

        if (loadingSpinner) {
            loadingSpinner.style.display = loading ? 'inline-block' : 'none';
        }
    }

    /**
     * Validate form before submission
     * @returns {boolean} Whether form is valid
     */
    function validateForm() {
        const fullName = form.full_name.value.trim();
        const email = form.email.value.trim();
        const phoneNumber = form.phone_number.value.trim();

        if (!fullName) {
            showErrorMessage('Please enter your full name.');
            form.full_name.focus();
            return false;
        }

        if (!email || !isValidEmail(email)) {
            showErrorMessage('Please enter a valid email address.');
            form.email.focus();
            return false;
        }

        if (!phoneNumber) {
            showErrorMessage('Please enter your phone number.');
            form.phone_number.focus();
            return false;
        }

        return true;
    }

    /**
     * Simple email validation
     * @param {string} email - Email to validate
     * @returns {boolean} Whether email is valid
     */
    function isValidEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }

    console.log('Stripe Elements initialized successfully');
}
