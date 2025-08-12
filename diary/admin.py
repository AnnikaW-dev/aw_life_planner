from django.contrib import admin
from .models import DiaryEntry


@admin.register(DiaryEntry)
class DiaryEntryAdmin(admin.ModelAdmin):
    list_display = [
        'user',
        'date',
        'title',
        'mood',
        'created_at',
    ]
    list_filter = [
        'mood',
        'created_at',
        'date',
    ]
    seach_fields =[
        'title',
        'content',
        'user__username',
    ]
    date_hierarchy = 'date'
