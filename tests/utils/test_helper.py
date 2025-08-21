# tests/utils/test_helpers.py

from django.contrib.auth.models import User
from shop.models import Module, Category, UserModule
from checkout.models import Order, OrderLineItem
from modules.models import MealPlan, CleaningTask, HabitTracker
from django.test import Client

class TestDataFactory:
    """Factory for creating test data"""

    @staticmethod
    def create_test_user(username='testuser', email='test@example.com'):
        """Create a test user"""
        return User.objects.create_user(
            username=username,
            email=email,
            password='testpass123'
        )

    @staticmethod
    def create_test_category(name='test_category'):
        """Create a test category"""
        return Category.objects.create(
            name=name,
            friendly_name=name.replace('_', ' ').title()
        )

    @staticmethod
    def create_test_module(category=None, module_type='meal_planner', price=9.99):
        """Create a test module"""
        if not category:
            category = TestDataFactory.create_test_category()

        return Module.objects.create(
            name=f'Test {module_type.replace("_", " ").title()}',
            module_type=module_type,
            description=f'Test {module_type} description',
            price=price,
            category=category
        )

    @staticmethod
    def create_test_order(user, stripe_pid='pi_test_12345', total=9.99):
        """Create a test order"""
        return Order.objects.create(
            user=user,
            full_name=f'{user.first_name} {user.last_name}' or user.username,
            email=user.email,
            phone_number='1234567890',
            total=total,
            stripe_pid=stripe_pid
        )

    @staticmethod
    def create_user_module(user, module):
        """Grant user access to a module"""
        return UserModule.objects.create(user=user, module=module)

    @staticmethod
    def create_complete_purchase(user, module):
        """Create a complete purchase scenario"""
        order = TestDataFactory.create_test_order(user, total=module.price)

        OrderLineItem.objects.create(
            order=order,
            module=module,
            lineitem_total=module.price
        )

        user_module = TestDataFactory.create_user_module(user, module)

        return {
            'order': order,
            'user_module': user_module
        }

class WebhookTestHelpers:
    """Helper functions for webhook testing"""

    @staticmethod
    def create_stripe_event(event_type, payment_intent_id, username, amount=999):
        """Create a mock Stripe webhook event"""
        return {
            'id': f'evt_test_{payment_intent_id}',
            'object': 'event',
            'type': event_type,
            'data': {
                'object': {
                    'id': payment_intent_id,
                    'object': 'payment_intent',
                    'amount': amount,
                    'currency': 'usd',
                    'status': 'succeeded' if 'succeeded' in event_type else 'requires_payment_method',
                    'metadata': {
                        'username': username
                    }
                }
            },
            'created': 1234567890,
            'livemode': False
        }

    @staticmethod
    def send_webhook_event(client, event_data):
        """Send a webhook event to the Django app"""
        return client.post(
            '/checkout/webhook/',
            data=event_data,
            content_type='application/json',
            HTTP_STRIPE_SIGNATURE='test_signature'
        )

class ModuleTestHelpers:
    """Helper functions for module testing"""

    @staticmethod
    def create_meal_plan(user, date=None):
        """Create a test meal plan"""
        from django.utils import timezone

        return MealPlan.objects.create(
            user=user,
            date=date or timezone.now().date(),
            breakfast='Test breakfast',
            lunch='Test lunch',
            dinner='Test dinner',
            water_intake=8
        )

    @staticmethod
    def create_cleaning_task(user, task_name='Test Task'):
        """Create a test cleaning task"""
        from django.utils import timezone

        return CleaningTask.objects.create(
            user=user,
            task_name=task_name,
            room='Test Room',
            frequency='weekly',
            next_due=timezone.now().date()
        )

    @staticmethod
    def create_habit(user, habit_name='Test Habit'):
        """Create a test habit"""
        return HabitTracker.objects.create(
            user=user,
            habit_name=habit_name,
            description='Test habit description',
            target_frequency='daily',
            color='#3498db'
        )

class AuthTestHelpers:
    """Helper functions for authentication testing"""

    @staticmethod
    def login_user(client, user):
        """Log in a user"""
        return client.login(username=user.username, password='testpass123')

    @staticmethod
    def create_authenticated_client(user=None):
        """Create a client with an authenticated user"""
        if not user:
            user = TestDataFactory.create_test_user()

        client = Client()
        client.login(username=user.username, password='testpass123')
        return client, user
