# tests/test_modules.py
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from decimal import Decimal
from datetime import date

from shop.models import Category, Module, UserModule
from modules.models import MealPlan


class MealPlannerTests(TestCase):
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.category = Category.objects.create(name='wellness')
        self.module = Module.objects.create(
            category=self.category,
            name='Meal Planner Pro',
            module_type='meal_planner',
            description='Plan your meals',
            price=Decimal('9.99')
        )

    def test_meal_planner_requires_login(self):
        """Test that meal planner requires authentication"""
        response = self.client.get(reverse('modules:meal_planner'))
        # Should redirect to login page
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/accounts/login'))

    def test_meal_planner_requires_module_ownership(self):
        """Test that user must own the module to access meal planner"""
        self.client.login(username='testuser', password='testpass123')

        response = self.client.get(reverse('modules:meal_planner'))
        # Should redirect to shop because user doesn't own module
        self.assertEqual(response.status_code, 302)

    def test_meal_planner_access_with_ownership(self):
        """Test that user can access meal planner when they own the module"""
        # Give user ownership of the module
        UserModule.objects.create(user=self.user, module=self.module)

        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('modules:meal_planner'))

        # Should show the meal planner page
        self.assertEqual(response.status_code, 200)

    def test_meal_plan_creation(self):
        """Test creating a meal plan"""
        # Give user ownership of the module
        UserModule.objects.create(user=self.user, module=self.module)

        self.client.login(username='testuser', password='testpass123')

        response = self.client.post(reverse('modules:add_meal_plan'), {
            'date': date.today(),
            'breakfast': 'Oatmeal with berries',
            'lunch': 'Chicken salad',
            'dinner': 'Grilled salmon',
            'water_intake': 8,
        })

        # Should redirect after successful creation
        self.assertEqual(response.status_code, 302)

        # Check that meal plan was created
        self.assertTrue(MealPlan.objects.filter(
            user=self.user,
            breakfast='Oatmeal with berries'
        ).exists())

    def test_meal_plan_model(self):
        """Test MealPlan model basic functionality"""
        meal_plan = MealPlan.objects.create(
            user=self.user,
            date=date.today(),
            breakfast='Test breakfast',
            water_intake=5
        )

        # Test string representation
        expected = f"{self.user.username} - Meal Plan {meal_plan.date}"
        self.assertEqual(str(meal_plan), expected)

        # Test that it was saved correctly
        self.assertEqual(meal_plan.breakfast, 'Test breakfast')
        self.assertEqual(meal_plan.water_intake, 5)


class ShopIntegrationTests(TestCase):
    def setUp(self):
        """Set up test data for shop integration"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    def test_shop_page_loads(self):
        """Test that shop page loads correctly"""
        response = self.client.get(reverse('shop:modules'))
        self.assertEqual(response.status_code, 200)

    def test_home_page_loads(self):
        """Test that home page loads correctly"""
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
