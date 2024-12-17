from datetime import datetime
from django.shortcuts import redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from .models import OvertimeRequest
from .forms import OvertimeRequestForm
from django.contrib import messages

class OvertimeListView(LoginRequiredMixin, ListView):
    model = OvertimeRequest
    template_name = 'overtime/overtime_list.html'
    context_object_name = 'overtime_requests'
    
    def get_queryset(self):
        if self.request.user.is_staff or self.request.user.is_superuser:
            return OvertimeRequest.objects.all()
        return OvertimeRequest.objects.filter(employee=self.request.user.employee_profile)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_staff'] = self.request.user.is_staff or self.request.user.is_superuser
        return context

class OvertimeDetailView(LoginRequiredMixin, DetailView):
    model = OvertimeRequest
    template_name = 'overtime/overtime_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['can_approve'] = self.request.user.is_staff or self.request.user.is_superuser
        context['can_edit'] = (not context['can_approve'] and 
                             self.object.status in ['pending', 'rejected'] and 
                             self.object.employee == self.request.user.employee_profile)
        return context

class OvertimeCreateView(LoginRequiredMixin, CreateView):
    model = OvertimeRequest
    form_class = OvertimeRequestForm
    template_name = 'overtime/overtime_form.html'
    
    def form_valid(self, form):
        form.instance.employee = self.request.user.employee_profile
        start = datetime.combine(form.instance.date, form.instance.start_time)
        end = datetime.combine(form.instance.date, form.instance.end_time)
        duration = end - start
        form.instance.hours = round(duration.total_seconds() / 3600, 2)
        messages.success(self.request, 'Overtime request created successfully!')
        return super().form_valid(form)

class OvertimeUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = OvertimeRequest
    form_class = OvertimeRequestForm
    template_name = 'overtime/overtime_form.html'

    def test_func(self):
        overtime = self.get_object()
        if self.request.user.is_staff or self.request.user.is_superuser:
            return False
        return (self.request.user.employee_profile == overtime.employee and 
                overtime.status in ['pending', 'rejected'])
        
class OvertimeDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = OvertimeRequest
    template_name = 'overtime/overtime_confirm_delete.html'
    success_url = reverse_lazy('overtime:list')

    def test_func(self):
        return self.request.user.is_staff or self.request.user.is_superuser
    
class OvertimeApproveView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = OvertimeRequest
    http_method_names = ['post']
    
    def test_func(self):
        return self.request.user.is_staff
    
    def post(self, request, *args, **kwargs):
        overtime = self.get_object()
        overtime.status = 'approved'
        overtime.approved_by = request.user
        overtime.save()
        messages.success(request, 'Overtime request approved successfully')
        return redirect('overtime:detail', pk=overtime.pk)

class OvertimeRejectView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = OvertimeRequest
    http_method_names = ['post']
    
    def test_func(self):
        return self.request.user.is_staff
    
    def post(self, request, *args, **kwargs):
        overtime = self.get_object()
        overtime.status = 'rejected'
        overtime.approved_by = request.user
        overtime.save()
        messages.success(request, 'Overtime request rejected successfully')
        return redirect('overtime:detail', pk=overtime.pk)
