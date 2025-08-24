from django.db import models
from django.contrib.auth.models import User


class Category(models.Model):
    name = models.CharField(max_length=254)
    friendly_name = models.CharField(max_length=254, null=True, blank=True)

    class Meta:
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name


class Module(models.Model):
    MODULE_TYPES = [
        ('meal_planner', 'Meal Planner'),
        ('cleaning_schedule', 'Cleaning Schedule'),
        ('stickers', 'Digital Stickers'),
        ('habit_tracker', 'Habit Tracker'),
    ]

    category = models.ForeignKey(
        'Category', null=True, blank=True, on_delete=models.SET_NULL
        )
    name = models.CharField(max_length=254)
    module_type = models.CharField(max_length=50, choices=MODULE_TYPES)
    description = models.TextField()
    price = models.DecimalField(max_digits=6, decimal_places=2)
    image = models.ImageField(null=True, blank=True)  # ändrat från images

    def __str__(self):
        return self.name


class UserModule(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    module = models.ForeignKey(Module, on_delete=models.CASCADE)
    purchase_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'module']

    def __str__(self):
        return f'{self.user.username} - {self.module.name}'
