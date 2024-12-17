from django.utils import timezone
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy, reverse
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.contrib import messages
from django.views import View
from django.template.loader import get_template
from xhtml2pdf import pisa
from .models import Payroll
from .forms import PayrollCreateForm, PayrollUpdateForm
import qrcode
import base64
from io import BytesIO


class PayrollListView(LoginRequiredMixin, ListView):
    model = Payroll
    template_name = "payrolls/payroll_list.html"
    context_object_name = "payrolls"

    def get_queryset(self):
        queryset = Payroll.objects.select_related("employee__user")
        now = timezone.now()

        if self.request.user.is_staff:
            month_year = self.request.GET.get(
                "month_year", f"{now.year}-{now.month:02d}"
            )
            year, month = map(int, month_year.split("-"))
            queryset = queryset.filter(month__year=year, month__month=month)
        else:
            selected_year = self.request.GET.get("year", now.year)
            queryset = queryset.filter(
                employee=self.request.user.employee_profile, month__year=selected_year
            )

        payrolls = list(queryset)
        for payroll in payrolls:
            payroll.qr_code = self.get_qr_code(payroll)
        return payrolls

    def get_qr_code(self, payroll):
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        url = self.request.build_absolute_uri(
            reverse("payroll-pdf", kwargs={"pk": payroll.pk})
        )
        qr.add_data(url)
        qr.make(fit=True)

        img_buffer = BytesIO()
        img = qr.make_image(fill_color="black", back_color="white")
        img.save(img_buffer, format="PNG")
        img_str = base64.b64encode(img_buffer.getvalue()).decode()
        return img_str

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if not self.request.user.is_staff:
            current_year = timezone.now().year
            available_years = range(current_year - 5, current_year + 1)
            context["years"] = available_years
            context["selected_year"] = int(self.request.GET.get("year", current_year))
        return context


class PayrollPDFView(UserPassesTestMixin, View):
    def test_func(self):
        payroll = get_object_or_404(Payroll, pk=self.kwargs["pk"])
        return self.request.user.is_staff or payroll.employee.user == self.request.user

    def get(self, request, pk):
        payroll = get_object_or_404(Payroll, pk=pk)
        template = get_template("payrolls/payroll_pdf.html")
        html = template.render({"payroll": payroll})

        result = BytesIO()
        pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result)

        if not pdf.err:
            response = HttpResponse(result.getvalue(), content_type="application/pdf")
            response["Content-Disposition"] = f"filename=payroll_{payroll.pk}.pdf"
            return response

        return HttpResponse("Error generating PDF", status=400)


class PayrollCreateView(UserPassesTestMixin, CreateView):
    model = Payroll
    form_class = PayrollCreateForm
    template_name = "payrolls/payroll_form.html"
    success_url = reverse_lazy("payroll-list")

    def test_func(self):
        return self.request.user.is_staff

    def form_valid(self, form):
        try:
            return super().form_valid(form)
        except Exception as e:
            messages.error(self.request, str(e))
            return self.form_invalid(form)


class PayrollUpdateView(UserPassesTestMixin, UpdateView):
    model = Payroll
    form_class = PayrollUpdateForm
    template_name = "payrolls/payroll_form.html"
    success_url = reverse_lazy("payroll-list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["object"] = self.get_object()
        return context

    def test_func(self):
        return self.request.user.is_staff


class PayrollDeleteView(UserPassesTestMixin, DeleteView):
    model = Payroll
    success_url = reverse_lazy("payroll-list")
    template_name = "payrolls/payroll_confirm_delete.html"

    def test_func(self):
        return self.request.user.is_staff
