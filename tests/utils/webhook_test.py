# manual_webhook_test.py - Test script for Stripe webhooks
import os
import requests


def test_webhook_endpoint(heroku_app_url):
    """Test if webhook endpoint is accessible"""
    webhook_url = f"{heroku_app_url}/checkout/webhook/"

    try:
        # Test GET request (should return 405 Method Not Allowed)
        response = requests.get(webhook_url)
        print(f"✅ Webhook endpoint accessible: {response.status_code}")

        return True
    except requests.exceptions.RequestException as e:
        print(f"❌ Webhook endpoint not accessible: {e}")
        return False


def verify_stripe_keys():
    """Verify Stripe keys are properly configured"""
    public_key = os.environ.get('STRIPE_PUBLIC_KEY')
    secret_key = os.environ.get('STRIPE_SECRET_KEY')
    webhook_secret = os.environ.get('STRIPE_WH_SECRET')

    print("Stripe Configuration:")
    print(f"✅ Public Key: {
        '✓' if public_key and public_key.startswith('pk_') else '❌'
        }")
    print(f"✅ Secret Key: {
        '✓' if secret_key and secret_key.startswith('sk_') else '❌'
        }")
    print(f"✅ Webhook Secret: {
        '✓' if webhook_secret and webhook_secret.startswith('whsec_') else '❌'
        }")

    return all([public_key, secret_key, webhook_secret])


def test_payment_flow():
    """Manual test checklist for payment flow"""
    print("\n📋 Manual Payment Flow Test Checklist:")
    print("1. [ ] Add items to cart")
    print("2. [ ] Proceed to checkout")
    print("3. [ ] Fill in delivery details")
    print("4. [ ] Use Stripe test card: 4242 4242 4242 4242")
    print("5. [ ] Complete payment")
    print("6. [ ] Verify order confirmation page")
    print("7. [ ] Check order appears in user profile")
    print("8. [ ] Verify order appears in admin panel")
    print("9. [ ] Check Stripe dashboard for payment event")
    print("10. [ ] Verify webhook received in Stripe dashboard")


if __name__ == "__main__":
    # Replace with your Heroku app URL
    HEROKU_APP_URL = "https://aw-life-planner-ms4-f700cbfe6055.herokuapp.com"

    print("🧪 Testing Stripe Webhook Configuration\n")

    # Test 1: Verify environment variables
    keys_ok = verify_stripe_keys()

    # Test 2: Test webhook endpoint accessibility
    endpoint_ok = test_webhook_endpoint(HEROKU_APP_URL)

    # Test 3: Manual test checklist
    test_payment_flow()

    if keys_ok and endpoint_ok:
        print("\n🎉 Webhook setup looks good! Ready for manual testing.")
    else:
        print("\n⚠️  Issues found. Please fix before testing.")
