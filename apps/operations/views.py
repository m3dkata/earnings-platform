from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.contrib import messages
from django.db.models import Q
from django.db.models.deletion import ProtectedError
from .models import Operation, Rate
from .forms import OperationForm, RateForm
from django.contrib.auth.mixins import PermissionRequiredMixin


class OperationListView(ListView):
    model = Operation
    template_name = "operations/operation_list.html"
    context_object_name = "operations"
    paginate_by = 12

    def get_queryset(self):
        queryset = Operation.objects.select_related("category")
        search = self.request.GET.get("search", "").strip()
        if search:
            queryset = queryset.filter(
                Q(code__icontains=search)
                | Q(name__icontains=search)
                | Q(category__category__icontains=search)
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        paginator = context["paginator"]
        page = context["page_obj"]
        context["page_range"] = range(
            max(page.number - 2, 1), min(page.number + 2, paginator.num_pages) + 1
        )
        return context


class OperationCreateView(PermissionRequiredMixin, CreateView):
    model = Operation
    form_class = OperationForm
    template_name = "operations/partials/operation_form.html"
    success_url = reverse_lazy("operations_list")
    permission_required = "operations.add_operation"

    def form_valid(self, form):
        self.object = form.save()
        messages.success(self.request, "Operation created successfully")
        return redirect(self.success_url)

    def form_invalid(self, form):
        messages.error(
            self.request, "Operation creation failed. Please check the form."
        )
        return super().form_invalid(form)


class OperationUpdateView(PermissionRequiredMixin, UpdateView):
    model = Operation
    form_class = OperationForm
    template_name = "operations/partials/operation_form.html"
    success_url = reverse_lazy("operations_list")
    permission_required = "operations.change_operation"

    def form_valid(self, form):
        self.object = form.save()
        messages.success(self.request, "Operation updated successfully")
        return redirect(self.success_url)

    def form_invalid(self, form):
        messages.error(self.request, "Operation update failed. Please check the form.")
        return super().form_invalid(form)


class OperationDeleteView(PermissionRequiredMixin, DeleteView):
    model = Operation
    template_name = "operations/delete_modal.html"
    success_url = reverse_lazy("operations_list")
    permission_required = "operations.delete_operation"

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        try:
            self.object.delete()
            messages.success(request, "Operation deleted successfully")
        except ProtectedError:
            messages.error(
                request,
                "Cannot delete this operation as it is being used by other objects",
            )
        return redirect(self.success_url)


class RateListView(ListView):
    model = Rate
    template_name = "operations/rate_list.html"
    context_object_name = "rates"


class RateCreateView(PermissionRequiredMixin, CreateView):
    model = Rate
    form_class = RateForm
    template_name = "operations/partials/rate_form.html"
    success_url = reverse_lazy("rates_list")
    permission_required = "operations.add_rate"

    def form_valid(self, form):
        self.object = form.save()
        messages.success(self.request, "Rate created successfully")
        return redirect(self.success_url)

    def form_invalid(self, form):
        messages.error(self.request, "Rate creation failed. Please check the form.")
        return super().form_invalid(form)


class RateUpdateView(PermissionRequiredMixin, UpdateView):
    model = Rate
    form_class = RateForm
    template_name = "operations/partials/rate_form.html"
    success_url = reverse_lazy("rates_list")
    permission_required = "operations.change_rate"

    def form_valid(self, form):
        self.object = form.save()
        messages.success(self.request, "Rate updated successfully")
        return redirect(self.success_url)

    def form_invalid(self, form):
        messages.error(self.request, "Rate update failed. Please check the form.")
        return super().form_invalid(form)


class RateDeleteView(PermissionRequiredMixin, DeleteView):
    model = Rate
    template_name = "operations/delete_rate_modal.html"
    success_url = reverse_lazy("rates_list")
    permission_required = "operations.delete_rate"

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        try:
            self.object.delete()
            messages.success(request, "Rate deleted successfully")
        except ProtectedError:
            messages.error(
                request,
                "Cannot delete this rate because it is being used by operations",
            )
        return redirect(self.success_url)
