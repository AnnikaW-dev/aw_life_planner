# checkout/admin.py - UPDATED TO USE ACTUAL FIELD
from django.contrib import admin
from .models import Order, OrderLineItem


class OrderLineItemAdminInline(admin.TabularInline):
    model = OrderLineItem
    readonly_fields = ('lineitem_total',)  # This field exists in your model
    extra = 0
    can_delete = False


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
