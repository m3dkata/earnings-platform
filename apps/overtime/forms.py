from django import forms
from .models import OvertimeRequest

class OvertimeRequestForm(forms.ModelForm):
    class Meta:
        model = OvertimeRequest
        fields = ['date', 'start_time', 'end_time', 'description']
        widgets = {
            'date': forms.DateInput(
                attrs={
                    'type': 'date',
                    'class': 'rounded-lg bg-slate-50 border text-slate-900 focus:ring-purple-500 focus:border-purple-500 block w-full p-2.5 dark:bg-slate-700 dark:border-slate-600 dark:text-white'
                }
            ),
            'start_time': forms.TimeInput(
                attrs={
                    'type': 'time',
                    'class': 'rounded-lg bg-slate-50 border text-slate-900 focus:ring-purple-500 focus:border-purple-500 block w-full p-2.5 dark:bg-slate-700 dark:border-slate-600 dark:text-white'
                }
            ),
            'end_time': forms.TimeInput(
                attrs={
                    'type': 'time',
                    'class': 'rounded-lg bg-slate-50 border text-slate-900 focus:ring-purple-500 focus:border-purple-500 block w-full p-2.5 dark:bg-slate-700 dark:border-slate-600 dark:text-white'
                }
            ),
            'description': forms.Textarea(
                attrs={
                    'rows': 3,
                    'class': 'rounded-lg bg-slate-50 border text-slate-900 focus:ring-purple-500 focus:border-purple-500 block w-full p-2.5 dark:bg-slate-700 dark:border-slate-600 dark:text-white'
                }
            ),
        }
