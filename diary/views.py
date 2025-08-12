from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import DiaryEntry
from .forms import DiaryEntryForm


@login_required
def diary_home(request):
    entries = DiaryEntry.objects.filter(user=request.user)
    return render(request, 'diary/diary_home.html', {'entries': entries})


@login_required
def add_entry(request):
    if request.method == 'POST':
        form = DiaryEntryForm(request.POST)
        if form.is_valid():
            entry=form.save(commit=False)
            entry.user = request.user
            entry.save()
            messages.success(request, 'Entry added successfully!')
            return redirect('diary:diary_home')
    else:
        form = DiaryEntryForm()
    return render(request, 'diary/add_entry.html', {'form': form})


@login_required
def view_entry(request, entry_id):
    entry = get_object_or_404(DiaryEntry, pk=entry_id)
    return render(request, 'diary/view_entry.html', {'entry': entry})
