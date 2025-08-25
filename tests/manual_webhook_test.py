# manual_webhook_test.py (in project root)

import requests
import time
from datetime import datetime


class WebhookTester:
    def __init__(self, base_url="http://127.0.0.1:8000"):
        self.base_url = base_url
        self.webhook_url = f"{base_url}/checkout/webhook/"

    def create_test_event(
            self, event_type,
            payment_intent_id,
            username="testuser",
            amount=999
            ):
        """Create a test webhook event"""
        return {
            "id": f"evt_{int(time.time())}",
            "object": "event",
            "api_version": "2020-08-27",
            "created": int(time.time()),
            "data": {
                "object": {
                    "id": payment_intent_id,
                    "object": "payment_intent",
                    "amount": amount,
                    "currency": "usd",
                    "status": "succeeded" if "succeeded"
                    in event_type else "requires_payment_method",
                    "metadata": {
                        "username": username,
                        "order_id": f"test_order_{int(time.time())}"
                    },
                    "charges": {
                        "data": [{
                            "id": f"ch_{int(time.time())}",
                            "billing_details": {
                                "name": "Test User",
                                "email": "test@example.com"
                            }
                        }]
                    }
                }
            },
            "livemode": False,
            "pending_webhooks": 1,
            "request": {
                "id": None,
                "idempotency_key": None
            },
            "type": event_type
        }

    def send_webhook(self, event_data):
        """Send webhook to Django app"""
        headers = {
            'Content-Type': 'application/json',
            'Stripe-Signature': 'test_signature'
            # In real testing, this would be properly signed
        }

        try:
            response = requests.post(
                self.webhook_url,
                json=event_data,
                headers=headers,
                timeout=10
            )
            return response
        except requests.exceptions.RequestException as e:
            print(f"❌ Error sending webhook: {e}")
            return None

    def test_successful_payment_flow(self):
        """Test successful payment webhook flow"""
        print("🧪 Testing Successful Payment Flow...")

        payment_intent_id = f"pi_test_{int(time.time())}"

        # 1. Test payment_intent.created
        created_event = self.create_test_event(
            "payment_intent.created", payment_intent_id
            )
        response = self.send_webhook(created_event)

        if response and response.status_code == 200:
            print("✅ payment_intent.created - SUCCESS")
        else:
            print(
                f"❌ payment_intent.created - FAILED "
                f"({response.status_code if response else 'No response'})"
                )

        time.sleep(1)  # Simulate time between events

        # 2. Test payment_intent.succeeded
        succeeded_event = self.create_test_event(
            "payment_intent.succeeded", payment_intent_id
            )
        response = self.send_webhook(succeeded_event)

        if response and response.status_code == 200:
            print("✅ payment_intent.succeeded - SUCCESS")
        else:
            print(f"❌ payment_intent.succeeded - FAILED "
                  f"({response.status_code if response else 'No response'})")

    def test_error_scenarios(self):
        """Test various error scenarios"""
        print("\n🧪 Testing Error Scenarios...")

        # Test 1: Invalid JSON payload
        print("Testing invalid JSON payload...")
        response = requests.post(
            self.webhook_url,
            data="invalid json",
            headers={
                'Content-Type': 'application/json',
                'Stripe-Signature': 'test'
                  },
            timeout=10
        )

        if response.status_code == 400:
            print("✅ Invalid JSON - Correctly rejected (400)")
        else:
            print(f"❌ Invalid JSON - Wrong response ({response.status_code})")

        # Test 2: Missing user in metadata
        print("Testing missing user metadata...")
        event = self.create_test_event
        ("payment_intent.succeeded", f"pi_test_{int(time.time())}"
         )
        event['data']['object']['metadata'] = {}  # Remove username

        response = self.send_webhook(event)
        if response and response.status_code == 200:
            print("✅ Missing user metadata - Handled gracefully")
        else:
            print(
                f"❌ Missing user metadata - Failed "
                f"({response.status_code if response else 'No response'})"
                )

        # Test 3: Nonexistent user
        print("Testing nonexistent user...")
        event = self.create_test_event(
            "payment_intent.succeeded",
            f"pi_test_{int(time.time())}", username="nonexistent_user"
            )

        response = self.send_webhook(event)
        if response and response.status_code == 200:
            print("✅ Nonexistent user - Handled gracefully")
        else:
            print(
                f"❌ Nonexistent user - Failed "
                f"({response.status_code if response else 'No response'})"
                )

    def test_duplicate_events(self):
        """Test duplicate event handling"""
        print("\n🧪 Testing Duplicate Event Handling...")

        payment_intent_id = f"pi_test_{int(time.time())}"
        event = self.create_test_event(
            "payment_intent.succeeded", payment_intent_id
            )

        success_count = 0

        # Send same event 3 times
        for i in range(3):
            response = self.send_webhook(event)
            if response and response.status_code == 200:
                success_count += 1
                print(f"✅ Duplicate event #{i+1} - Handled successfully")
            else:
                print(f"❌ Duplicate event #{i+1} - Failed")
            time.sleep(0.5)

        if success_count == 3:
            print("✅ All duplicate events handled successfully")
        else:
            print(f"⚠️  Only {success_count}/3 duplicate events succeeded")

    def test_high_volume(self):
        """Test high volume of webhooks"""
        print("\n🧪 Testing High Volume Webhooks...")

        success_count = 0
        total_events = 10

        for i in range(total_events):
            payment_intent_id = f"pi_test_volume_{int(time.time())}_{i}"
            event = self.create_test_event(
                "payment_intent.succeeded", payment_intent_id
                )

            response = self.send_webhook(event)
            if response and response.status_code == 200:
                success_count += 1
                print(f"✅ Event {i+1}/{total_events} - Success")
            else:
                print(f"❌ Event {i+1}/{total_events} - Failed")

            time.sleep(0.1)  # Small delay between events

        print(f"\n📊 High Volume Test Results: "
              f"{success_count}/{total_events} succeeded")
        if success_count == total_events:
            print("✅ All high volume events processed successfully")
        else:
            print(f"⚠️  {total_events - success_count} events failed")

    def run_all_tests(self):
        """Run comprehensive webhook tests"""
        print("🚀 Starting Comprehensive Webhook Testing")
        print("=" * 60)
        print(f"Target URL: {self.webhook_url}")
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)

        # Run all test categories
        self.test_successful_payment_flow()
        self.test_error_scenarios()
        self.test_duplicate_events()
        self.test_high_volume()

        print("\n" + "=" * 60)
        print("🏁 Webhook Testing Complete!")
        print("✅ Check the output above for detailed results")
        print("=" * 60)


if __name__ == "__main__":
    tester = WebhookTester()
    tester.run_all_tests()
