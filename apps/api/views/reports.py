from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema
from rest_framework.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from django.db import transaction
from apps.reports.models import Report
from apps.api.serializers.reports import ReportSerializer
from apps.reports.mixins import WorkHourRestrictionMixin
from apps.notifications.services import NotificationService


class ReportListCreateAPIView(WorkHourRestrictionMixin, APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(responses={200: ReportSerializer(many=True)})
    def get(self, request):
        if request.user.is_staff:
            reports = (
                Report.objects.select_related("employee__user")
                .prefetch_related("reportoperation_set__operation")
                .all()
            )
        else:
            reports = (
                Report.objects.select_related("employee__user")
                .prefetch_related("reportoperation_set__operation")
                .filter(employee__user=request.user)
            )
        serializer = ReportSerializer(reports, many=True)
        return Response(serializer.data)

    @extend_schema(request=ReportSerializer, responses={201: ReportSerializer})
    def post(self, request):
        serializer = ReportSerializer(data=request.data)
        if serializer.is_valid():
            with transaction.atomic():
                if not request.user.is_staff:
                    serializer.validated_data["employee"] = (
                        request.user.employee_profile
                    )
                report = serializer.save()
                report.status = "SUBMITTED"
                report.save()

                NotificationService.notify_staff_new_report(report)
                return Response(
                    ReportSerializer(report).data, status=status.HTTP_201_CREATED
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ReportDetailAPIView(WorkHourRestrictionMixin, APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk, user):
        report = get_object_or_404(Report, pk=pk)
        if not user.is_staff and report.employee.user != user:
            raise PermissionDenied()
        return report

    @extend_schema(responses={200: ReportSerializer})
    def get(self, request, pk):
        report = self.get_object(pk, request.user)
        serializer = ReportSerializer(report)
        return Response(serializer.data)

    @extend_schema(request=ReportSerializer, responses={200: ReportSerializer})
    def put(self, request, pk):
        report = self.get_object(pk, request.user)

        if request.user.is_staff:
            if "status" in request.data:
                report.status = request.data["status"]
                report.save()
                NotificationService.notify_report_status(report, report.status)
                return Response(ReportSerializer(report).data)

        serializer = ReportSerializer(report, data=request.data)
        if serializer.is_valid():
            with transaction.atomic():
                report = serializer.save()
                return Response(ReportSerializer(report).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(responses={204: None})
    def delete(self, request, pk):
        report = self.get_object(pk, request.user)
        report.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
