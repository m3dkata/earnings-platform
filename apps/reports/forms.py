from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from apps.employees.models import Employee
from .models import Report, ReportOperation
from apps.operations.models import Operation
from django.forms import modelformset_factory

class ReportForm(forms.ModelForm):
    date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        error_messages={
            'required': 'Date is required',
            'invalid': 'Enter a valid date'
        }
    )
    
    class Meta:
        model = Report
        fields = ['date']
        
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user and user.is_staff:
            self.fields['employee'] = forms.ModelChoiceField(
                queryset=Employee.objects.all(),
                widget=forms.Select(attrs={
                    'class': 'select2',
                    'data-minimum-input-length': '1',
                    'data-placeholder': 'Select Employee',
                }),
                error_messages={
                    'required': 'Employee selection is required',
                    'invalid_choice': 'Select a valid employee'
                }
            )
            
    def clean_date(self):
        date = self.cleaned_data['date']
        if date > timezone.now().date():
            raise ValidationError("Report date cannot be in the future")
        return date
    
    def clean(self):
        cleaned_data = super().clean()
        date = cleaned_data.get('date')
        employee = cleaned_data.get('employee')
        
        if date and employee:
            if Report.objects.filter(employee=employee, date=date).exists():
                raise ValidationError("Report for this employee and date already exists")
        return cleaned_data

class ReportOperationForm(forms.ModelForm):
    operation = forms.ModelChoiceField(
        queryset=Operation.objects.all(),
        widget=forms.Select(attrs={
            'class': 'select2',
            'data-minimum-input-length': '1',
            'data-placeholder': 'Operation code'
        }),
        error_messages={
            'required': 'Operation selection is required',
            'invalid_choice': 'Select a valid operation'
        }
    )
    quantity = forms.IntegerField(
        min_value=1,
        error_messages={
            'required': 'Quantity is required',
            'min_value': 'Quantity must be greater than 0',
            'invalid': 'Enter a valid number'
        }
    )

    class Meta:
        model = ReportOperation
        fields = ['operation', 'quantity']
        
    def clean(self):
        cleaned_data = super().clean()
        operation = cleaned_data.get('operation')
        quantity = cleaned_data.get('quantity')
        
        if operation and quantity:
            if self.instance and self.instance.pk:
                if ReportOperation.objects.filter(
                    report=self.instance.report,
                    operation=operation
                ).exclude(pk=self.instance.pk).exists():
                    raise ValidationError("This operation is already added to the report")
        return cleaned_data

ReportOperationFormSet = modelformset_factory(
    ReportOperation,
    form=ReportOperationForm,
    extra=10,
    max_num=10,
    can_delete=True,
    validate_max=True,
    error_messages={
        'too_many_forms': 'Maximum 10 operations allowed per report'
    },
    fields=['operation', 'quantity', 'id']
)
