# modules/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
from datetime import timedelta
from shop.models import UserModule
from .models import MealPlan, CleaningTask, HabitTracker, HabitLog
from .forms import MealPlanForm, CleaningTaskForm, HabitTrackerForm


def check_module_access(user, module_type):
    """Check if user has purchased the required module"""
    return UserModule.objects.filter(
        user=user,
        module__module_type=module_type
    ).exists()


@login_required
def meal_planner(request):
    """Meal planner view"""
    if not check_module_access(request.user, 'meal_planner'):
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
    """Add meal plan view"""
    if not check_module_access(request.user, 'meal_planner'):
        messages.error(
            request,
            'You need to purchase the Meal Planner module to access this feature.'
            )
        return redirect('shop:modules')

    if request.method == 'POST':
        form = MealPlanForm(request.POST)
        if form.is_valid():
            meal_plan = form.save(commit=False)
            meal_plan.user = request.user
            meal_plan.save()
            messages.success(request, 'Meal plan added successfully!')
            return redirect('modules:meal_planner')
    else:
        form = MealPlanForm(initial={'date': timezone.now().date()})

    return render(request, 'modules/add_meal_plan.html', {'form': form})


@login_required
def cleaning_schedule(request):
    """Cleaning schedule view"""
    if not check_module_access(request.user, 'cleaning_schedule'):
        messages.error(
            request,
            'You need to purchase the Cleaning Schedule module to access this feature.'
            )
        return redirect('shop:modules')

    tasks = CleaningTask.objects.filter(
        user=request.user, is_active=True
        ).order_by('next_due')
    overdue_tasks = tasks.filter(next_due__lt=timezone.now().date())
    today = timezone.now().date()

    context = {
        'tasks': tasks,
        'overdue_tasks': overdue_tasks,
        'today': today,
    }
    return render(request, 'modules/cleaning_schedule.html', context)


@login_required
def add_cleaning_task(request):
    """Add cleaning task view"""
    if not check_module_access(request.user, 'cleaning_schedule'):
        messages.error(
            request,
            'You need to purchase the Cleaning Schedule module to access this feature.'
            )
        return redirect('shop:modules')

    if request.method == 'POST':
        form = CleaningTaskForm(request.POST)
        if form.is_valid():
            cleaning_task = form.save(commit=False)
            cleaning_task.user = request.user
            cleaning_task.save()
            messages.success(
                request,
                f'Cleaning task "{cleaning_task.task_name}" added successfully!'
                )
            return redirect('modules:cleaning_schedule')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CleaningTaskForm()

    return render(request, 'modules/add_cleaning_task.html', {'form': form})


@login_required
def edit_cleaning_task(request, task_id):
    """Edit cleaning task view"""
    if not check_module_access(request.user, 'cleaning_schedule'):
        messages.error(request, 'You need to purchase the Cleaning Schedule module to access this feature.')
        return redirect('shop:modules')

    task = get_object_or_404(CleaningTask, id=task_id, user=request.user)

    if request.method == 'POST':
        form = CleaningTaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            messages.success(
                request,
                f'Cleaning task "{task.task_name}" updated successfully!'
                )
            return redirect('modules:cleaning_schedule')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CleaningTaskForm(instance=task)

    return render(
        request,
        'modules/edit_cleaning_task.html',
        {'form': form, 'task': task}
        )


@login_required
def delete_cleaning_task(request, task_id):
    """Delete cleaning task view"""
    if not check_module_access(request.user, 'cleaning_schedule'):
        messages.error(
            request,
            'You need to purchase the Cleaning Schedule module to access this feature.'
            )
        return redirect('shop:modules')

    task = get_object_or_404(CleaningTask, id=task_id, user=request.user)

    if request.method == 'POST':
        task_name = task.task_name
        task.delete()
        messages.success(request, f'Cleaning task "{task_name}" deleted successfully!')
        return redirect('modules:cleaning_schedule')

    return render(request, 'modules/delete_cleaning_task.html', {'task': task})


@login_required
def complete_cleaning_task(request, task_id):
    """Mark cleaning task as complete and update next due date"""
    if not check_module_access(request.user, 'cleaning_schedule'):
        messages.error(
            request,
            'You need to purchase the Cleaning Schedule module to access this feature.'
            )
        return redirect('shop:modules')

    task = get_object_or_404(CleaningTask, id=task_id, user=request.user)

    # Update last completed and calculate next due date
    task.last_completed = timezone.now().date()

    # Calculate next due date based on frequency
    if task.frequency == 'daily':
        task.next_due = task.last_completed + timedelta(days=1)
    elif task.frequency == 'weekly':
        task.next_due = task.last_completed + timedelta(weeks=1)
    elif task.frequency == 'monthly':
        # Add approximately 30 days for monthly
        task.next_due = task.last_completed + timedelta(days=30)

    task.save()
    messages.success(
        request, f'Task "{task.task_name}" marked as complete! Next due: {task.next_due}'
        )
    return redirect('modules:cleaning_schedule')


@login_required
def habit_tracker(request):
    """Display habit tracker with today's progress"""
    if not check_module_access(request.user, 'habit_tracker'):
        messages.error(
            request,
            'You need to purchase the Habit Tracker module to access this feature.'
            )
        return redirect('shop:modules')

    habits = HabitTracker.objects.filter(user=request.user, is_active=True)
    today = timezone.now().date()
    # Get today's habit logs for each habit
    habit_data = []

    for habit in habits:
        try:
            habit_log = HabitLog.objects.get(habit=habit, date=today)
            completed_today = habit_log.completed
        except HabitLog.DoesNotExist:
            completed_today = False
        # Calculate current streak
        streak = calculate_habit_streak(habit)
        habit_data.append({
            'habit': habit,
            'completed_today': completed_today,
            'streak': streak,
        })
    context = {
        'habit_data': habit_data,
        'today': today,
    }

    return render(request, 'modules/habit_tracker.html', context)


@login_required
def add_habit(request):
    """Add habit view"""
    if not check_module_access(request.user, 'habit_tracker'):
        messages.error(
            request,
            'You need to purchase the Habit Tracker module to access this feature.'
            )
        return redirect('shop:modules')

    if request.method == 'POST':
        form = HabitTrackerForm(request.POST)
        if form.is_valid():
            habit = form.save(commit=False)
            habit.user = request.user
            habit.save()
            messages.success(
                request,
                f'Habit "{habit.habit_name}" added successfully!'
                )
            return redirect('modules:habit_tracker')
    else:
        form = HabitTrackerForm()

    return render(request, 'modules/add_habit.html', {'form': form})


@login_required
def toggle_habit(request, habit_id):
    """Toggle habit completion for today via AJAX"""
    if request.method == 'POST':
        habit = get_object_or_404(HabitTracker, id=habit_id, user=request.user)
        today = timezone.now().date()

        # Get or create today's habit log
        habit_log, created = HabitLog.objects.get_or_create(
            habit=habit,
            date=today,
            defaults={'completed': False}
        )
        # Toggle completion status
        habit_log.completed = not habit_log.completed
        habit_log.save()

        # Calculate new streak
        streak = calculate_habit_streak(habit)

        return JsonResponse({
            'success': True,
            'completed': habit_log.completed,
            'streak': streak,
            'message': f'Habit {"completed" if habit_log.completed else "unchecked"} for today!'
        })

    return JsonResponse({'success': False, 'message': 'Invalid request'})


@login_required
def edit_habit(request, habit_id):
    """Edit habit view"""
    if not check_module_access(request.user, 'habit_tracker'):
        messages.error(
            request,
            'You need to purchase the Habit Tracker module to access this feature.'
            )
        return redirect('shop:modules')

    habit = get_object_or_404(HabitTracker, id=habit_id, user=request.user)

    if request.method == 'POST':
        form = HabitTrackerForm(request.POST, instance=habit)
        if form.is_valid():
            form.save()
            messages.success(
                request,
                f'Habit "{habit.habit_name}" updated successfully!'
                )
            return redirect('modules:habit_tracker')
    else:
        form = HabitTrackerForm(instance=habit)

    return render(
        request,
        'modules/edit_habit.html', {'form': form, 'habit': habit}
        )


@login_required
def delete_habit(request, habit_id):
    """Delete habit view"""
    if not check_module_access(request.user, 'habit_tracker'):
        messages.error(
            request,
            'You need to purchase the Habit Tracker module to access this feature.'
            )
        return redirect('shop:modules')

    habit = get_object_or_404(HabitTracker, id=habit_id, user=request.user)

    if request.method == 'POST':
        habit_name = habit.habit_name
        habit.delete()
        messages.success(
            request,
            f'Habit "{habit_name}" deleted successfully!'
            )
        return redirect('modules:habit_tracker')

    return render(request, 'modules/delete_habit.html', {'habit': habit})


def calculate_habit_streak(habit):
    """Calculate current streak for a habit"""
    today = timezone.now().date()
    streak = 0
    current_date = today

    # Count backwards from today to find consecutive completed days
    while True:
        try:
            log = HabitLog.objects.get(habit=habit, date=current_date)
            if log.completed:
                streak += 1
                current_date -= timezone.timedelta(days=1)
            else:
                break
        except HabitLog.DoesNotExist:
            break

    return streak
