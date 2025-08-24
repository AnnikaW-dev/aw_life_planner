# checkout/admin.py - CORRECTED VERSION
from django.contrib import admin
from .models import Order, OrderLineItem


class OrderLineItemAdminInline(admin.TabularInline):
    model = OrderLineItem
    readonly_fields = ('get_module_price',)  # Changed from 'lineitem_total' to 'get_module_price'
    extra = 0  # Don't show extra empty forms
    can_delete = False  # Prevent deletion of line items

    def get_module_price(self, obj):
        """Display the module price"""
        if obj and obj.module:
            return f"${obj.module.price}"
        return "N/A"
    get_module_price.short_description = 'Price'


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    inlines = (OrderLineItemAdminInline,)
    readonly_fields = (
        'order_number',
        'user',
        'date',
        'total'
    )
    fields = (
        'order_number',
        'user',
        'date',
        'full_name',
        'email',
        'phone_number',
        'total',
        'stripe_pid',
    )
    list_display = (
        'order_number',
        'date',
        'full_name',
        'total',
    )
    ordering = ('-date',)
