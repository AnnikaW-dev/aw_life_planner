# modules/urls.py
from django.urls import path
from . import views

app_name = 'modules'

urlpatterns = [
    path('meal-planner/', views.meal_planner, name='meal_planner'),
    path('meal-planner/add/', views.add_meal_plan, name='add_meal_plan'),
    path('cleaning-schedule/', views.cleaning_schedule, name='cleaning_schedule'),
    path('habit-tracker/', views.habit_tracker, name='habit_tracker'),
]
