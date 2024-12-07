from django import forms
from .models import Payroll
from datetime import datetime

COMMON_FIELD_CLASSES = 'rounded-lg bg-slate-50 border text-slate-900 focus:ring-purple-500 focus:border-purple-500 block flex-1 min-w-0 w-full text-sm border-slate-300 p-2.5  dark:bg-slate-800 dark:border-slate-600 dark:placeholder-slate-400 dark:text-white dark:focus:ring-purple-500 dark:focus:border-purple-500'

class PayrollCreateForm(forms.ModelForm):
    month = forms.CharField(widget=forms.DateInput(attrs={'class': COMMON_FIELD_CLASSES, 'type': 'month'}))
    class Meta:
        model = Payroll
        fields = ['employee', 'month', 'vacation_days', 'sick_days', 'bank_transfer']
        widgets = {
            'employee': forms.Select(attrs={'class': COMMON_FIELD_CLASSES}),
            'vacation_days': forms.NumberInput(attrs={'class': COMMON_FIELD_CLASSES}),
            'sick_days': forms.NumberInput(attrs={'class': COMMON_FIELD_CLASSES}),
            'bank_transfer': forms.NumberInput(attrs={'class': COMMON_FIELD_CLASSES})
        }
    def clean_month(self):
        month_str = self.cleaned_data['month']
        return datetime.strptime(f"{month_str}-01", "%Y-%m-%d").date()
class PayrollUpdateForm(forms.ModelForm):
    class Meta:
        model = Payroll
        fields = ['vacation_days', 'sick_days', 'bank_transfer']
        widgets = {
            'vacation_days': forms.NumberInput(attrs={'class': COMMON_FIELD_CLASSES}),
            'sick_days': forms.NumberInput(attrs={'class': COMMON_FIELD_CLASSES}),
            'bank_transfer': forms.NumberInput(attrs={'class': COMMON_FIELD_CLASSES})
        }
