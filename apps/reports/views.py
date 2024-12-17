import calendar
from datetime import datetime
from django.db import transaction
from django.utils import timezone
from django.views.generic import CreateView, UpdateView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.shortcuts import redirect
from apps.employees.models import Employee
from .models import Report, ReportOperation
from .forms import ReportForm, ReportOperationFormSet
from apps.payrolls.tasks import generate_payroll
from .mixins import WorkHourRestrictionMixin
from django.db.models import Q
from django.contrib import messages
from apps.notifications.services import NotificationService


class ReportListView(LoginRequiredMixin, ListView):
    model = Report
    paginate_by = 10

    def get_template_names(self):
        if self.request.user.is_staff:
            return ["reports/admin_report_list.html"]
        return ["reports/employee_report_list.html"]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_staff:
            date_str = self.request.GET.get("date")
            if date_str:
                selected_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            else:
                selected_date = timezone.now().date()

            reports = (
                Report.objects.filter(date=selected_date)
                .select_related("employee__user", "employee__workshop")
                .prefetch_related("reportoperation_set__operation")
            )

            employees_without_reports = Employee.objects.filter(
                ~Q(report__date=selected_date)
            ).select_related("user", "workshop")

            context.update(
                {
                    "selected_date": selected_date,
                    "reports": reports,
                    "employees_without_reports": employees_without_reports,
                }
            )
        else:
            month_year = self.request.GET.get(
                "month_year", timezone.now().strftime("%Y-%m")
            )
            year, month = map(int, month_year.split("-"))
            calendar_dates = calendar.monthcalendar(year, month)

            reports = Report.objects.filter(
                employee=self.request.user.employee_profile, date__month=month
            ).select_related("employee__user")

            employee_reports = {}
            for report in reports:
                employee_reports[report.date.day] = {
                    "id": report.id,
                    "status": report.status,
                    "total_percent": report.total_percent,
                    "total_sum": report.total_sum,
                }

            context.update(
                {
                    "calendar_dates": calendar_dates,
                    "month_year": month_year,
                    "employee_reports": employee_reports,
                }
            )

        return context


class ReportCreateView(LoginRequiredMixin, WorkHourRestrictionMixin, CreateView):
    model = Report
    form_class = ReportForm
    template_name = "reports/report_form.html"
    success_url = reverse_lazy("report-list")

    def get_initial(self):
        initial = super().get_initial()
        date = self.request.GET.get("date")
        employee_id = self.request.GET.get("employee")

        if date:
            initial["date"] = date
        if employee_id and self.request.user.is_staff:
            initial["employee"] = Employee.objects.get(pk=employee_id)

        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context["formset"] = ReportOperationFormSet(self.request.POST)
        else:
            context["formset"] = ReportOperationFormSet(
                queryset=ReportOperation.objects.none()
            )
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        formset = context["formset"]

        if not formset.is_valid():
            messages.error(
                self.request, "Please check the operations data and try again."
            )
            return self.form_invalid(form)

        report = form.save(commit=False)

        if self.request.user.is_staff:
            report.employee = form.cleaned_data.get("employee")
        else:
            report.employee = self.request.user.employee_profile

        report.status = "SUBMITTED" if "submit" in self.request.POST else "DRAFT"
        report.save()

        if formset.is_valid():
            instances = formset.save(commit=False)
            for instance in instances:
                instance.report = report
                instance.save()

        if report.status == "SUBMITTED":
            NotificationService.notify_staff_new_report(report)
        messages.success(self.request, f"Report {report.status} successfully!")
        return redirect(self.success_url)

    def form_invalid(self, form):
        messages.error(self.request, "Please check the form data and try again.")
        return super().form_invalid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs


class ReportUpdateView(LoginRequiredMixin, WorkHourRestrictionMixin, UpdateView):
    model = Report
    form_class = ReportForm
    success_url = reverse_lazy("report-list")

    def get_template_names(self):
        if self.request.user.is_staff:
            return ["reports/admin_report_form.html"]
        return ["reports/report_form.html"]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["report"] = self.object
        context["employee"] = self.object.employee
        context["operations"] = ReportOperation.objects.filter(
            report=self.object
        ).select_related("operation")
        context["total_percent"] = self.object.total_percent
        context["total_sum"] = self.object.total_sum

        if not self.request.user.is_staff and self.object.status != "APPROVED":
            if self.request.POST:
                context["formset"] = ReportOperationFormSet(
                    self.request.POST, queryset=context["operations"]
                )
            else:
                context["formset"] = ReportOperationFormSet(
                    queryset=context["operations"]
                )
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        if request.user.is_staff:
            if "approve" in request.POST:
                self.object.status = "APPROVED"
                NotificationService.notify_report_status(self.object, "APPROVED")
                messages.success(
                    self.request, f"Report {self.object.status.lower()} successfully!"
                )
                generate_payroll.delay(
                    self.object.employee.id, self.object.date.strftime("%Y-%m-%d")
                )
            elif "reject" in request.POST:
                self.object.status = "REJECTED"
                NotificationService.notify_report_status(self.object, "REJECTED")
                messages.success(
                    self.request, f"Report {self.object.status.lower()} successfully!"
                )
            self.object.save()
            return redirect(self.success_url)
        return super().post(request, *args, **kwargs)

    def form_invalid(self, form):
        messages.error(self.request, "Please check the form data and try again.")
        return super().form_invalid(form)

    def form_valid(self, form):
        if not self.request.user.is_staff:
            context = self.get_context_data()
            formset = context["formset"]

            if not formset.is_valid():
                messages.error(
                    self.request, "Please check the operations data and try again."
                )
                return self.form_invalid(form)

            if formset.is_valid():
                with transaction.atomic():
                    self.object = form.save()
                    ReportOperation.objects.filter(report=self.object).delete()

                    for form in formset:
                        if form.cleaned_data and not form.cleaned_data.get("DELETE"):
                            operation = form.cleaned_data.get("operation")
                            quantity = form.cleaned_data.get("quantity")
                            if operation and quantity:
                                ReportOperation.objects.create(
                                    report=self.object,
                                    operation=operation,
                                    quantity=quantity,
                                )

                    if "submit" in self.request.POST:
                        self.object.status = "SUBMITTED"
                        NotificationService.notify_staff_new_report(self.object)
                    elif "draft" in self.request.POST:
                        self.object.status = "DRAFT"
                    self.object.save()
                    messages.success(
                        self.request,
                        f"Report {self.object.status.lower()} successfully!",
                    )
        return redirect(self.success_url)
