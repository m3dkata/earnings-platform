from django.shortcuts import redirect
from django.contrib import messages
from django.views.generic import TemplateView
from django.apps import apps

class BaseTemplateView(TemplateView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_superuser:
            models_data = []
            for app_config in apps.get_app_configs():
                if not app_config.name.startswith('django.'):
                    for model in app_config.get_models():
                        models_data.append({
                            'name': model._meta.verbose_name.capitalize(),
                            'app_label': model._meta.app_label,
                            'model_name': model._meta.model_name
                        })
            context['models_data'] = models_data
        return context
