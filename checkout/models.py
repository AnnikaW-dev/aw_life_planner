# checkout/models.py - FIXED VERSION
from django.db import models
from django.contrib.auth.models import User
from shop.models import Module

import uuid


class Order(models.Model):
    order_number = models.CharField(max_length=32, null=True, editable=False)
    user = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True)
    full_name = models.CharField(max_length=50, null=False, blank=False)
    email = models.EmailField(max_length=254, null=False, blank=False)
    phone_number = models.CharField(max_length=20, null=False, blank=False)
    date = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(
        max_digits=10, decimal_places=2, null=False, default=0)
    stripe_pid = models.CharField(
        max_length=254, null=False, blank=False, default='')

    def _generate_order_number(self):
        return uuid.uuid4().hex.upper()

    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = self._generate_order_number()
        super().save(*args, **kwargs)

    def __str__(self):
        """ String representation of the order """
        return f"Order {self.order_number or self.id}"

    class Meta:
        ordering = ['-date']


class OrderLineItem(models.Model):
    order = models.ForeignKey(
        Order, null=False, blank=False, on_delete=models.CASCADE,
        related_name='lineitems')
    module = models.ForeignKey(
        Module, null=False, blank=False, on_delete=models.CASCADE)
    lineitem_total = models.DecimalField(
        max_digits=6, decimal_places=2, null=False,
        blank=False, editable=False)

    def save(self, *args, **kwargs):
        self.lineitem_total = self.module.price
        super().save(*args, **kwargs)

    def __str__(self):
        # FIXED: Removed the invalid :number format specifier
        return f'Module {self.module.name} on order {self.order.order_number}'
