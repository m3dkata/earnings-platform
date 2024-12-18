from django import forms
from .models import Employee, Workshop, Leave


class EmployeeActivationForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not Workshop.objects.exists():
            for choice in Workshop.WORKSHOP_CHOICES:
                Workshop.objects.create(name=choice[0])

        self.fields["workshop"].queryset = Workshop.objects.all()

    class Meta:
        model = Employee
        fields = ["number", "position", "workshop"]
        widgets = {
            "number": forms.NumberInput(
                attrs={
                    "class": "w-full rounded-lg bg-slate-50 border text-slate-900 focus:ring-purple-500 focus:border-purple-500 block flex-1 min-w-0 text-sm border-slate-300 p-2.5  dark:bg-slate-700 dark:border-slate-600 dark:placeholder-slate-400 dark:text-white dark:focus:ring-purple-500 dark:focus:border-purple-500"
                }
            ),
            "position": forms.Select(
                attrs={
                    "class": "w-full rounded-lg bg-slate-50 border text-slate-900 focus:ring-purple-500 focus:border-purple-500 block flex-1 min-w-0 text-sm border-slate-300 p-2.5  dark:bg-slate-700 dark:border-slate-600 dark:placeholder-slate-400 dark:text-white dark:focus:ring-purple-500 dark:focus:border-purple-500"
                }
            ),
            "workshop": forms.Select(
                attrs={
                    "class": "w-full rounded-lg bg-slate-50 border text-slate-900 focus:ring-purple-500 focus:border-purple-500 block flex-1 min-w-0 text-sm border-slate-300 p-2.5  dark:bg-slate-700 dark:border-slate-600 dark:placeholder-slate-400 dark:text-white dark:focus:ring-purple-500 dark:focus:border-purple-500"
                }
            ),
        }


class LeaveRequestForm(forms.ModelForm):
    class Meta:
        model = Leave
        fields = ["leave_type", "start_datetime", "end_datetime", "reason"]
        widgets = {
            "leave_type": forms.Select(
                attrs={
                    "class": "rounded-lg bg-slate-50 border text-slate-900 focus:ring-purple-500 focus:border-purple-500 block w-full p-2.5 dark:bg-slate-700 dark:border-slate-600 dark:text-white"
                }
            ),
            "start_datetime": forms.DateTimeInput(
                attrs={
                    "type": "datetime-local",
                    "class": "rounded-lg bg-slate-50 border text-slate-900 focus:ring-purple-500 focus:border-purple-500 block w-full p-2.5 dark:bg-slate-700 dark:border-slate-600 dark:text-white",
                }
            ),
            "end_datetime": forms.DateTimeInput(
                attrs={
                    "type": "datetime-local",
                    "class": "rounded-lg bg-slate-50 border text-slate-900 focus:ring-purple-500 focus:border-purple-500 block w-full p-2.5 dark:bg-slate-700 dark:border-slate-600 dark:text-white",
                }
            ),
            "reason": forms.Textarea(
                attrs={
                    "rows": 3,
                    "class": "rounded-lg bg-slate-50 border text-slate-900 focus:ring-purple-500 focus:border-purple-500 block w-full p-2.5 dark:bg-slate-700 dark:border-slate-600 dark:text-white",
                }
            ),
        }


class LeaveFilterForm(forms.Form):
    month = forms.DateField(
        required=False,
        widget=forms.DateInput(
            attrs={
                "type": "month",
                "class": "rounded-lg bg-slate-50 border text-slate-900 focus:ring-purple-500 focus:border-purple-500 block w-full p-2.5 dark:bg-slate-700 dark:border-slate-600 dark:text-white",
            }
        ),
    )
