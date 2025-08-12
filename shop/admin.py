from django.contrib import admin
from .models import Category, Module, UserModule


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'friendly_name']


@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'category',
        'module_type',
        'price',
    ]
    list_filter = [
        'category',
        'module_type',
    ]


@admin.register(UserModule)
class UserModuleAdmin(admin.ModelAdmin):
    list_display = [
        'user',
        'module',
        'purchase_date',
    ]
    list_filter = [
        'module',
        'purchase_date',
    ]
