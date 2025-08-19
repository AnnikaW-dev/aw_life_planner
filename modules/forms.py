# modules/forms.py
from django import forms
from django.utils import timezone
from .models import MealPlan, CleaningTask, HabitTracker

class MealPlanForm(forms.ModelForm):
    class Meta:
        model = MealPlan
        fields = ['date', 'breakfast', 'lunch', 'dinner', 'snacks', 'water_intake', 'notes']
        widgets = {
            'date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
                'value': timezone.now().date()
            }),
            'breakfast': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'lunch': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'dinner': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'snacks': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'water_intake': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

class CleaningTaskForm(forms.ModelForm):
    class Meta:
        model = CleaningTask
        fields = ['task_name', 'room', 'frequency', 'next_due', 'notes']
        widgets = {
            'task_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Vacuum Living Room'}),
            'room': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Living Room'}),
            'frequency': forms.Select(attrs={'class': 'form-control'}),
            'next_due': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control date-input',
                'min': timezone.now().date(),
                'required': True
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Any additional notes...'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set default next_due to today if creating new task
        if not self.instance.pk:
            self.fields['next_due'].initial = timezone.now().date()

        # Make fields required
        self.fields['task_name'].required = True
        self.fields['room'].required = True
        self.fields['frequency'].required = True
        self.fields['next_due'].required = True

    def clean_next_due(self):
        next_due = self.cleaned_data.get('next_due')
        if next_due and next_due < timezone.now().date():
            raise forms.ValidationError("Next due date cannot be in the past.")
        return next_due

class HabitTrackerForm(forms.ModelForm):
    class Meta:
        model = HabitTracker
        fields = ['habit_name', 'description', 'target_frequency', 'color']
        widgets = {
            'habit_name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'target_frequency': forms.Select(attrs={'class': 'form-control'}),
            'color': forms.TextInput(attrs={'type': 'color', 'class': 'form-control form-control-color'}),
        }
