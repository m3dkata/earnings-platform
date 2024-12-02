from django import forms
from .models import Employee

class EmployeeActivationForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = ['number', 'position', 'workshop']
        widgets = {
            'number': forms.NumberInput(attrs={'class': 'w-full rounded-lg bg-slate-50 border text-slate-900 focus:ring-purple-500 focus:border-purple-500 block flex-1 min-w-0 text-sm border-slate-300 p-2.5  dark:bg-slate-700 dark:border-slate-600 dark:placeholder-slate-400 dark:text-white dark:focus:ring-purple-500 dark:focus:border-purple-500'}),
            'position': forms.Select(attrs={'class': 'w-full rounded-lg bg-slate-50 border text-slate-900 focus:ring-purple-500 focus:border-purple-500 block flex-1 min-w-0 text-sm border-slate-300 p-2.5  dark:bg-slate-700 dark:border-slate-600 dark:placeholder-slate-400 dark:text-white dark:focus:ring-purple-500 dark:focus:border-purple-500'}),
            'workshop': forms.Select(attrs={'class': 'w-full rounded-lg bg-slate-50 border text-slate-900 focus:ring-purple-500 focus:border-purple-500 block flex-1 min-w-0 text-sm border-slate-300 p-2.5  dark:bg-slate-700 dark:border-slate-600 dark:placeholder-slate-400 dark:text-white dark:focus:ring-purple-500 dark:focus:border-purple-500'})
        }
