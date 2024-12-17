from django import forms
from .models import Operation, Rate


class BaseModelForm(forms.ModelForm):
    default_widget_attrs = {
        "class": "rounded-lg bg-slate-50 border text-slate-900 focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-slate-700 dark:border-slate-600 dark:placeholder-slate-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500"
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if hasattr(field.widget, "attrs"):
                field.widget.attrs.update(self.default_widget_attrs)


class OperationForm(BaseModelForm):
    class Meta:
        model = Operation
        fields = ["code", "name", "time", "category"]
        widgets = {
            "time": forms.NumberInput(attrs={"step": "0.01"}),
        }
        error_messages = {
            "code": {
                "unique": "This operation code already exists.",
                "required": "Operation code is required.",
                "invalid": "Please enter a valid operation code.",
            },
            "name": {
                "required": "Operation name is required.",
                "max_length": "Operation name cannot exceed 255 characters.",
            },
            "time": {
                "required": "Operation time is required.",
                "invalid": "Please enter a valid time value.",
            },
            "category": {
                "required": "Category selection is required.",
                "invalid": "Please select a valid category.",
            },
        }

    def clean_code(self):
        code = self.cleaned_data.get("code")
        if code is not None and code < 0:
            raise forms.ValidationError("Operation code cannot be negative.")
        return code

    def clean_time(self):
        time = self.cleaned_data.get("time")
        if time is not None and time <= 0:
            raise forms.ValidationError("Operation time must be greater than zero.")
        return time


class RateForm(BaseModelForm):
    class Meta:
        model = Rate
        fields = ["category", "price"]
        widgets = {
            "price": forms.NumberInput(attrs={"step": "0.01"}),
        }
        error_messages = {
            "category": {
                "required": "Category selection is required.",
                "invalid_choice": "Please select a valid category.",
            },
            "price": {
                "required": "Price is required.",
                "invalid": "Please enter a valid price.",
                "max_digits": "Price cannot exceed 10 digits.",
                "decimal_places": "Price must have exactly 2 decimal places.",
            },
        }

    def clean_price(self):
        price = self.cleaned_data.get("price")
        if price is not None and price <= 0:
            raise forms.ValidationError("Price must be greater than zero.")
        return price

    def clean(self):
        cleaned_data = super().clean()
        category = cleaned_data.get("category")
        price = cleaned_data.get("price")

        if category and price:
            exists_query = Rate.objects.filter(category=category)
            if self.instance.pk:
                exists_query = exists_query.exclude(pk=self.instance.pk)
            if exists_query.exists():
                raise forms.ValidationError("A rate for this category already exists.")

        return cleaned_data
