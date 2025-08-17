from django import forms
from .models import MealPlan, CleaningTask, HabitTracker


class MealPlanForm(forms.ModelForm):
    class Meta:
        model = MealPlan
        fields = [
            'date', 'breakfast',
            'lunch', 'dinner',
            'snacks', 'water_intake',
            'notes',
        ]
        widgets = {
            'date': forms.DateInput(attrs={
                'type': 'date', 'class': 'form-control'
            }),
            'breakfast': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'What did you have for breakfast?' }),
            'lunch': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'What did you have for lunch?' }),
            'dinner': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'What did you have for dinner?' }),
            'snacks': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Any snacks?' }),
            'water_intake': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'placeholder': 'Number of glasses'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Any additional notes...' }),
        }



class CleaningTaskForm(forms.ModelForm):
    class Meta:
        model = CleaningTask
        fields = [
            'task_name', 'room',
            'frequency', 'next_due',
            'notes',
        ]
        widgets = {
            'date': forms.DateInput(attrs={
                'type': 'date', 'class': 'form-control'
            }),
            'task_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Vacuum carpet' }),
            'room': forms.TextInput(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'e.g., Living Room' }),
            'frequency': forms.Select(attrs={'class': 'form-control'}),
            'next_due': forms.DateInput(attrs={'type': 'date', 'class': 'form-control' }),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Any special instructions...' }),
        }



class HabitTrackerForm(forms.ModelForm):
    class Meta:
        model = HabitTracker
        fields = ['habit_name', 'description', 'target_frequency', 'color', ]
        widgets = {
            'habit_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Exercise, Read, Meditate'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Describe your habit...'}),
            'target_frequency': forms.Select(attrs={'class': 'form-control'}),
            'color': forms.DateInput(attrs={'type': 'color', 'class': 'form-control form-control-color'}),
            # 'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Any special instructions...'}),
        }
