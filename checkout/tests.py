from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User

class WebhookTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    def test_webhook_endpoint_exists(self):
        """Test that webhook endpoint exists"""
        response = self.client.post('/checkout/webhook/')
        # Should return 400 for invalid webhook (no proper signature)
        self.assertEqual(response.status_code, 400)

    def test_webhook_get_not_allowed(self):
        """Test that webhook only accepts POST requests"""
        response = self.client.get('/checkout/webhook/')
        self.assertEqual(response.status_code, 405)  # Method not allowed

    def test_checkout_page_loads(self):
        """Test that checkout page requires login"""
        response = self.client.get('/checkout/')
        # Should redirect to login
        self.assertEqual(response.status_code, 302)

    def test_checkout_with_login(self):
        """Test checkout page with authenticated user"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/checkout/')
        # Should redirect to shop (empty cart)
        self.assertEqual(response.status_code, 302)
