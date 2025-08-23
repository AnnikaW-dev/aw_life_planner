# tests/test_webhooks.py

import json
import stripe
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.conf import settings
from unittest.mock import patch, Mock
from checkout.models import Order, OrderLineItem
from shop.models import Module, UserModule, Category

class WebhookTestCase(TestCase):
    """Base test case for webhook tests"""

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

    def create_mock_payment_intent(self, status='succeeded', amount=999, pid=None):
        """Create mock payment intent data with unique ID"""
        if pid is None:
            pid = f'pi_test_payment_intent_{id(self)}'  # Make unique per test instance

        return {
            'id': pid,
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
    def test_payment_intent_succeeded_existing_order(self, mock_construct_event):
        """Test webhook when order already exists (normal flow)"""
        pid = 'pi_test_existing_order'
        payment_intent = self.create_mock_payment_intent(pid=pid)
        event = self.create_mock_webhook_event('payment_intent.succeeded', payment_intent)
        mock_construct_event.return_value = event

        # Create existing order with same PID
        order = Order.objects.create(
            user=self.user,
            full_name='Test User',
            email='test@example.com',
            phone_number='1234567890',
            total=9.99,
            stripe_pid=pid
        )

        response = self.client.post(
            reverse('checkout:stripe_webhook'),
            data=json.dumps(event),
            content_type='application/json',
            HTTP_STRIPE_SIGNATURE='test_signature'
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Order.objects.count(), 1)

    @patch('stripe.Webhook.construct_event')
    def test_payment_intent_succeeded_backup_creation(self, mock_construct_event):
        """Test order creation when main flow fails"""
        pid = 'pi_test_backup_creation'
        payment_intent = self.create_mock_payment_intent(pid=pid)
        event = self.create_mock_webhook_event('payment_intent.succeeded', payment_intent)
        mock_construct_event.return_value = event

        # No existing order - webhook should create one
        self.assertEqual(Order.objects.count(), 0)

        response = self.client.post(
            reverse('checkout:stripe_webhook'),
            data=json.dumps(event),
            content_type='application/json',
            HTTP_STRIPE_SIGNATURE='test_signature'
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Order.objects.count(), 1)

        order = Order.objects.first()
        self.assertEqual(order.stripe_pid, pid)
        self.assertEqual(order.user, self.user)

class WebhookErrorTests(WebhookTestCase):
    """Test webhook error handling"""

    def test_invalid_signature(self):
        """Test webhook with invalid signature"""
        with patch('stripe.Webhook.construct_event') as mock_construct:
            mock_construct.side_effect = stripe.error.SignatureVerificationError(
                'Invalid signature', 'sig_header'
            )

            response = self.client.post(
                reverse('checkout:stripe_webhook'),
                data='test_payload',
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

    @patch('stripe.Webhook.construct_event')
    def test_missing_user_metadata(self, mock_construct_event):
        """Test webhook with missing user metadata"""
        pid = 'pi_test_missing_metadata'
        payment_intent = self.create_mock_payment_intent(pid=pid)
        payment_intent['metadata'] = {}  # Remove username
        event = self.create_mock_webhook_event('payment_intent.succeeded', payment_intent)
        mock_construct_event.return_value = event

        # Make sure no orders exist initially
        self.assertEqual(Order.objects.count(), 0)

        response = self.client.post(
            reverse('checkout:stripe_webhook'),
            data=json.dumps(event),
            content_type='application/json',
            HTTP_STRIPE_SIGNATURE='test_signature'
        )

        # Should return 200 but not create order
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Order.objects.count(), 0)

class WebhookReliabilityTests(WebhookTestCase):
    """Test webhook reliability and edge cases"""

    @patch('stripe.Webhook.construct_event')
    def test_duplicate_webhook_handling(self, mock_construct_event):
        """Test handling of duplicate webhook events"""
        pid = 'pi_test_duplicate_handling'
        payment_intent = self.create_mock_payment_intent(pid=pid)
        event = self.create_mock_webhook_event('payment_intent.succeeded', payment_intent)
        mock_construct_event.return_value = event

        # Create order first
        Order.objects.create(
            user=self.user,
            full_name='Test User',
            email='test@example.com',
            phone_number='1234567890',
            total=9.99,
            stripe_pid=pid
        )

        # Send webhook multiple times
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
