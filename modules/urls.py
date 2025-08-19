# modules/urls.py
from django.urls import path
from . import views

app_name = 'modules'

urlpatterns = [
    # Meal Planner
    path('meal-planner/', views.meal_planner, name='meal_planner'),
    path('meal-planner/add/', views.add_meal_plan, name='add_meal_plan'),

    # Cleaning Schedule
    path('cleaning-schedule/', views.cleaning_schedule, name='cleaning_schedule'),
    path('cleaning-schedule/add/', views.add_cleaning_task, name='add_cleaning_task'),
    path('cleaning-schedule/edit/<int:task_id>/', views.edit_cleaning_task, name='edit_cleaning_task'),
    path('cleaning-schedule/delete/<int:task_id>/', views.delete_cleaning_task, name='delete_cleaning_task'),
    path('cleaning-schedule/complete/<int:task_id>/', views.complete_cleaning_task, name='complete_cleaning_task'),

    # Habit Tracker
    path('habit-tracker/', views.habit_tracker, name='habit_tracker'),
    path('habit-tracker/add/', views.add_habit, name='add_habit'),
    path('habit-tracker/edit/<int:habit_id>/', views.edit_habit, name='edit_habit'),
    path('habit-tracker/delete/<int:habit_id>/', views.delete_habit, name='delete_habit'),
    path('habit-tracker/toggle/<int:habit_id>/', views.toggle_habit, name='toggle_habit'),
]
