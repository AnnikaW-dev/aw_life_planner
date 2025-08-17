from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone

from shop.models import UserModule
from .models import MealPlan, CleaningTask, HabitTracker
from .forms import MealPlanForm, CleaningTaskForm, HabitTrackerForm


def check_module_access(user, module_type):
    """ Check if user has purchased the required module """
    return UserModule.objects.filter(
        user=user,
        module__module_type=module_type
    ).exists()

@login_required
def meal_planner(request):
    """ Chack if user has access """
    if not check_module_access(request.user , 'meal_planner'):
        messages.error(
            request,
            'You need to purchase the Meal Planner module to access this feature.'
            )
        return redirect('shop:modules')

    meal_plans = MealPlan.objects.filter(user=request.user)
    today = timezone.now().date()
    context = {
        'meal_plans': meal_plans,
        'today': today,
    }
    return render(request, 'modules/meal_planner.html', context)


@login_required
def add_meal_plan(request):
    if not check_module_access(request.user , 'meal_planner'):
        messages.error(
            request,
            'You need to purchase the Meal Planner module to access this feature.'
            )
        return redirect('shop:modules')

    if request .method == 'POST':
        form = MealPlanForm(request.POST)
        if form.is_valid():
            meal_plan = form.save(commit=False)
            meal_plan.user = request.user
            meal_plan.save()
            messages.success(request, 'Meal Plan added successfully!')
            return redirect('modules:meal_planner')
    else:
        form = MealPlanForm(initial={
            'date':timezone.now().date()
        })
    return render(request, 'modules/add_meal_plan.html', {
        'form':form
    })


@login_required
def cleaning_schedule(request):
    if not check_module_access(request.user, 'cleaning_schedule'):
        messages.error(
            request,
            'You need to purchase the Cleaning Schedule module to access this feature.'
            )
        return redirect('shop:modules')

    tasks = CleaningTask.objects.filter(user=request.user, is_active=True)
    overdue_tasks = tasks.filter(next_due__lt=timezone.now().date())
    context = {
        'tasks': tasks,
        'overdue_tasks': overdue_tasks
    }
    return render(request, 'modules/cleaning_schedule.html', context)


@login_required
def habit_tracker(request):
    if not check_module_access(request.user , 'habit_tracker'):
        messages.error(
            request,
            'You need to purchase the Habit tracker module to access this feature.'
            )
        return redirect('shop:modules')

    habits = HabitTracker.objects.filter(user=request.user, is_active=True)
    context = {
        'habits': habits,
    }
    return render(request, 'modules/habit_tracker.html', context)
