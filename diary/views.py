from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.http import Http404
from .models import DiaryEntry
from .forms import DiaryEntryForm


# HELPER FUNCTION - Reusable across all views

def get_user_entry_or_403(user, entry_id):
    """
    Get diary entry that belongs to user or raise PermissionDenied
    Args:
        user: The current user
        entry_id: The entry ID to fetch
    Returns:
        DiaryEntry object if user owns it
    Raises:
        Http404: If entry doesn't exist
        PermissionDenied: If user doesn't own the entry
    """
    try:
        entry = DiaryEntry.objects.get(pk=entry_id)
        if entry.user != user:
            raise PermissionDenied(
                "You don't have permission to access this entry"
                )
        return entry
    except DiaryEntry.DoesNotExist:
        raise Http404("Diary entry not found")


@login_required
def diary_home(request):
    """Display user's diary entries - only their own"""
    entries = DiaryEntry.objects.filter(user=request.user)
    return render(request, 'diary/diary_home.html', {'entries': entries})


@login_required
def add_entry(request):
    """Add new diary entry for logged-in user"""
    if request.method == 'POST':
        form = DiaryEntryForm(request.POST)
        if form.is_valid():
            entry = form.save(commit=False)
            entry.user = request.user
            entry.save()
            messages.success(request, 'Entry added successfully!')
            return redirect('diary:diary_home')
    else:
        form = DiaryEntryForm()
    return render(request, 'diary/add_entry.html', {'form': form})


@login_required
def view_entry(request, entry_id):
    """View diary entry - ONLY if it belongs to the current user"""
    entry = get_user_entry_or_403(request.user, entry_id)

    return render(request, 'diary/view_entry.html', {'entry': entry})


@login_required
def edit_entry(request, entry_id):
    entry = get_user_entry_or_403(request.user, entry_id)

    if request.method == 'POST':
        form = DiaryEntryForm(request.POST, instance=entry)
        if form.is_valid():
            form.save()
            messages.success(request, 'Entry update successfully!')
            return redirect('diary:view_entry', entry_id=entry.id)
    else:
        form = DiaryEntryForm(instance=entry)

    return render(request, 'diary/edit_entry.html', {
        'form': form, 'entry': entry
        })


@login_required
def delete_entry(request, entry_id):
    entry = get_user_entry_or_403(request.user, entry_id)
    if request.method == 'POST':
        entry.delete()
        messages.success(request, 'Entry deleted successfully!')
        return redirect('diary:diary_home')

    return render(request, 'diary/delete_entry.html', {'entry': entry})
