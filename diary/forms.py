from django import forms
from .models import DiaryEntry


class DiaryEntryForm(forms.ModelForm):
    class Meta:
        model = DiaryEntry
        fields = [
            'date',
            'title',
            'content',
            'mood',
        ]
        widgets = {
            'date':forms.DateInput(attrs={
                'type': 'date', 'class': 'form-control'
                }),
            'title': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-control', 'rows': 5
            }),
            'mood': forms.Select(attrs={
                'class': 'form-control'
            }),
        }
