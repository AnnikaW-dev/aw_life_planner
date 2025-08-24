from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from .models import DiaryEntry
from datetime import date


class DiaryModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )

    def test_diary_entry_creation(self):
        """Test creating a diary entry"""
        entry = DiaryEntry.objects.create(
            user=self.user,
            title='Test Entry',
            content='This is a test.',
            date=date.today()
        )
        self.assertEqual(str(entry), f"{self.user.username} - {entry.date}")
        self.assertEqual(entry.title, 'Test Entry')


class DiaryViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )

    def test_diary_home_requires_login(self):
        """Test that diary home requires authentication"""
        response = self.client.get(reverse('diary:diary_home'))
        self.assertEqual(response.status_code, 302)
        # Check that it redirects to the login page (
        # with or without query params)
        self.assertTrue(response.url.startswith('/accounts/login'))

    def test_diary_home_authenticated(self):
        """Test diary home for authenticated user"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('diary:diary_home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'diary/diary_home.html')
