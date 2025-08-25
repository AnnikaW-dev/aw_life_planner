import json
import stripe
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from unittest.mock import patch
from checkout.models import Order, OrderLineItem
from shop.models import Module, UserModule, Category


class WebhookTestCase(TestCase):
    def setUp(self):
        """Set up test data"""
        self.client = Client()

        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

        # Create test category and module
        self.category = Category.objects.create(
            name='test_category',
            friendly_name='Test Category'
        )

        self.module = Module.objects.create(
            name='Test Module',
            module_type='meal_planner',
            description='Test module description',
            price=9.99,
            category=self.category
        )

        # Mock webhook secret
        self.webhook_secret = 'whsec_test_secret'

    def create_mock_webhook_event(self, event_type, payment_intent_data):
        """Create a mock webhook event"""
        return {
            'id': 'evt_test_webhook',
            'object': 'event',
            'type': event_type,
            'data': {
                'object': payment_intent_data
            },
            'created': 1234567890,
            'livemode': False,
            'pending_webhooks': 1,
            'request': {
                'id': 'req_test',
                'idempotency_key': None
            }
        }

    def create_mock_payment_intent(self, status='succeeded', amount=999):
        """Create mock payment intent data"""
        return {
            'id': 'pi_test_payment_intent',
            'object': 'payment_intent',
            'amount': amount,
            'currency': 'usd',
            'status': status,
            'metadata': {
                'username': self.user.username,
                'user_id': str(self.user.id)
            },
            'charges': {
                'data': [{
                    'id': 'ch_test_charge',
                    'billing_details': {
                        'name': 'Test User',
                        'email': 'test@example.com'
                    }
                }]
            }
        }


class WebhookSuccessTests(WebhookTestCase):
    """Test successful webhook scenarios"""

    @patch('stripe.Webhook.construct_event')
    def test_payment_intent_succeeded_webhook(self, mock_construct_event):
        """Test successful payment_intent.succeeded webhook"""
        # Create mock event
        payment_intent = self.create_mock_payment_intent()
        event = self.create_mock_webhook_event(
            'payment_intent.succeeded', payment_intent
            )
        mock_construct_event.return_value = event

        # Create existing order (normal flow)
        order = Order.objects.create(
            user=self.user,
            full_name='Test User',
            email='test@example.com',
            phone_number='1234567890',
            total=9.99,
            stripe_pid='pi_test_payment_intent'
        )

        # Send webhook
        response = self.client.post(
            reverse('checkout:stripe_webhook'),
            data=json.dumps(event),
            content_type='application/json',
            HTTP_STRIPE_SIGNATURE='test_signature'
        )

        self.assertEqual(response.status_code, 200)

        # Verify order still exists and unchanged
        order.refresh_from_db()
        self.assertEqual(order.stripe_pid, 'pi_test_payment_intent')

    @patch('stripe.Webhook.construct_event')
    def test_payment_intent_created_webhook(self, mock_construct_event):
        """Test payment_intent.created webhook"""
        payment_intent = self.create_mock_payment_intent(
            status='requires_payment_method'
            )
        event = self.create_mock_webhook_event(
            'payment_intent.created', payment_intent
            )
        mock_construct_event.return_value = event

        response = self.client.post(
            reverse('checkout:stripe_webhook'),
            data=json.dumps(event),
            content_type='application/json',
            HTTP_STRIPE_SIGNATURE='test_signature'
        )

        self.assertEqual(response.status_code, 200)

    @patch('stripe.Webhook.construct_event')
    def test_backup_order_creation_from_webhook(self, mock_construct_event):
        """Test order creation when main flow fails"""
        payment_intent = self.create_mock_payment_intent()
        event = self.create_mock_webhook_event(
            'payment_intent.succeeded', payment_intent
            )
        mock_construct_event.return_value = event

        # Don't create order first - simulate main flow failure
        self.assertEqual(Order.objects.count(), 0)

        response = self.client.post(
            reverse('checkout:stripe_webhook'),
            data=json.dumps(event),
            content_type='application/json',
            HTTP_STRIPE_SIGNATURE='test_signature'
        )

        self.assertEqual(response.status_code, 200)

        # Verify order was created by webhook
        self.assertEqual(Order.objects.count(), 1)
        order = Order.objects.first()
        self.assertEqual(order.stripe_pid, 'pi_test_payment_intent')
        self.assertEqual(order.user, self.user)


class WebhookErrorTests(WebhookTestCase):
    """Test webhook error scenarios"""

    def test_invalid_signature(self):
        """Test webhook with invalid signature"""
        with patch('stripe.Webhook.construct_event') as mock_construct:
            mock_construct.side_effect = (
                stripe.error.SignatureVerificationError(
                    'Invalid signature',
                    'sig_header'
                    )
            )

            response = self.client.post(
                reverse('checkout:stripe_webhook'),
                data='invalid_payload',
                content_type='application/json',
                HTTP_STRIPE_SIGNATURE='invalid_signature'
            )

            self.assertEqual(response.status_code, 400)

    def test_invalid_payload(self):
        """Test webhook with invalid payload"""
        with patch('stripe.Webhook.construct_event') as mock_construct:
            mock_construct.side_effect = ValueError('Invalid payload')

            response = self.client.post(
                reverse('checkout:stripe_webhook'),
                data='invalid_json',
                content_type='application/json',
                HTTP_STRIPE_SIGNATURE='test_signature'
            )

            self.assertEqual(response.status_code, 400)

    def test_missing_user_metadata(self):
        """Test webhook with missing user metadata"""
        with patch('stripe.Webhook.construct_event') as mock_construct:
            payment_intent = self.create_mock_payment_intent()
            payment_intent['metadata'] = {}  # Remove username
            event = self.create_mock_webhook_event(
                'payment_intent.succeeded', payment_intent
                )
            mock_construct.return_value = event

            response = self.client.post(
                reverse('checkout:stripe_webhook'),
                data=json.dumps(event),
                content_type='application/json',
                HTTP_STRIPE_SIGNATURE='test_signature'
            )

            # Should still return 200 but log error
            self.assertEqual(response.status_code, 200)
            # Order should not be created
            self.assertEqual(Order.objects.count(), 0)

    def test_nonexistent_user(self):
        """Test webhook with non-existent user"""
        with patch('stripe.Webhook.construct_event') as mock_construct:
            payment_intent = self.create_mock_payment_intent()
            payment_intent['metadata']['username'] = 'nonexistent_user'
            event = self.create_mock_webhook_event(
                'payment_intent.succeeded', payment_intent
                )
            mock_construct.return_value = event

            response = self.client.post(
                reverse('checkout:stripe_webhook'),
                data=json.dumps(event),
                content_type='application/json',
                HTTP_STRIPE_SIGNATURE='test_signature'
            )

            self.assertEqual(response.status_code, 200)
            self.assertEqual(Order.objects.count(), 0)


class WebhookIntegrationTests(WebhookTestCase):
    """Integration tests for webhook flow"""

    @patch('stripe.Webhook.construct_event')
    def test_complete_payment_flow_with_webhook(self, mock_construct_event):
        """Test complete payment flow with webhook verification"""
        # 1. Create payment intent (simulate checkout page load)
        payment_intent = self.create_mock_payment_intent()

        # Create order (simulate successful payment)
        Order.objects.create(
            user=self.user,
            full_name='Test User',
            email='test@example.com',
            phone_number='1234567890',
            total=9.99,
            stripe_pid='pi_test_payment_intent'
        )

        # Send webhook (simulate Stripe confirmation)
        event = self.create_mock_webhook_event(
            'payment_intent.succeeded', payment_intent
            )
        mock_construct_event.return_value = event

        response = self.client.post(
            reverse('checkout:stripe_webhook'),
            data=json.dumps(event),
            content_type='application/json',
            HTTP_STRIPE_SIGNATURE='test_signature'
        )

        # Verify webhook processed successfully
        self.assertEqual(response.status_code, 200)

        # Verify all data is consistent
        self.assertEqual(Order.objects.count(), 1)
        self.assertEqual(OrderLineItem.objects.count(), 1)
        self.assertEqual(UserModule.objects.count(), 1)

        # Verify user has module access
        self.assertTrue(
            UserModule.objects.filter(
                user=self.user, module=self.module
                ).exists()
        )


class WebhookPerformanceTests(WebhookTestCase):
    """Test webhook performance and reliability"""

    @patch('stripe.Webhook.construct_event')
    def test_duplicate_webhook_handling(self, mock_construct_event):
        """Test handling of duplicate webhook events"""
        payment_intent = self.create_mock_payment_intent()
        event = self.create_mock_webhook_event(
            'payment_intent.succeeded', payment_intent
            )
        mock_construct_event.return_value = event

        # Create order first
        Order.objects.create(
            user=self.user,
            full_name='Test User',
            email='test@example.com',
            phone_number='1234567890',
            total=9.99,
            stripe_pid='pi_test_payment_intent'
        )

        # Send webhook multiple times (simulate Stripe retries)
        for i in range(3):
            response = self.client.post(
                reverse('checkout:stripe_webhook'),
                data=json.dumps(event),
                content_type='application/json',
                HTTP_STRIPE_SIGNATURE='test_signature'
            )
            self.assertEqual(response.status_code, 200)

        # Verify only one order exists
        self.assertEqual(Order.objects.count(), 1)

    @patch('stripe.Webhook.construct_event')
    def test_webhook_with_large_payload(self, mock_construct_event):
        """Test webhook with large payload"""
        payment_intent = self.create_mock_payment_intent()
        # Add large metadata
        payment_intent['metadata']['large_data'] = 'x' * 1000
        event = self.create_mock_webhook_event(
            'payment_intent.succeeded', payment_intent
            )
        mock_construct_event.return_value = event

        response = self.client.post(
            reverse('checkout:stripe_webhook'),
            data=json.dumps(event),
            content_type='application/json',
            HTTP_STRIPE_SIGNATURE='test_signature'
        )

        self.assertEqual(response.status_code, 200)
