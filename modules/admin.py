from django.contrib import admin
from .models import MealPlan, CleaningTask, Sticker, DiarySticker, HabitTracker, HabitLog


@admin.register(MealPlan)
class MealPlanAdmin (admin.ModelAdmin):
    list_display = [
        'user', 'date',
        'water_intake',
        'created_at',
    ]
    list_filter = [
        'date',
        'created_at',
    ]
    search_fields = [
        'user_username',
        'breakfast',
        'lunch', 'dinner',
    ]
    date_hierarchy = 'date'


@admin.register(CleaningTask)
class CleaningTaskAdmin (admin.ModelAdmin):
    list_display = [
        'user', 'task_name',
        'room', 'frequency',
        'next_due',
        'is_active',
    ]
    list_filter = [
        'frequency',
        'is_active',
        'room',
    ]
    search_fields = [
        'user_username',
        'task_name',
        'room',
    ]


@admin.register(Sticker)
class StickerAdmin (admin.ModelAdmin):
    list_display = [
        'name', 'category',
        'is_premium',
        'created_at',
    ]
    list_filter = [
        'category',
        'is_premium',
        'created_at',
    ]
    search_fields = [
        'name',
        'category',
    ]


@admin.register(DiarySticker)
class DiaryStickerAdmin(admin.ModelAdmin):
    list_display = [
        'diary_entry', 'sticker',
        'position_x', 'position_y',
        'size',
        ]
    list_filter = [
        'sticker__category'
        ]


@admin.register(HabitTracker)
class HabitTrackerAdmin (admin.ModelAdmin):
    list_display = [
        'user', 'habit_name',
        'target_frequency', 'is_active',
        'created_at',
    ]
    list_filter = [
        'target_frequency', 'is_active',
    ]
    search_fields = [
        'user__username',
        'habit_name',
    ]


@admin.register(HabitLog)
class HabitLogAdmin (admin.ModelAdmin):
    list_display = [
         'habit', 'date',
        'completed',
    ]
    list_filter = [
        'date', 'completed',
    ]
    date_hierarchy = 'date'
