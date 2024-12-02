from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema
from django.shortcuts import get_object_or_404
from apps.payrolls.models import Payroll
from apps.api.serializers.payrolls import PayrollSerializer

class PayrollListCreateAPIView(APIView):
    @extend_schema(
        responses={200: PayrollSerializer(many=True)}
    )
    def get(self, request):
        if request.user.is_staff:
            payrolls = Payroll.objects.select_related('employee__user').all()
        else:
            payrolls = Payroll.objects.select_related('employee__user').filter(
                employee__user=request.user
            )
        serializer = PayrollSerializer(payrolls, many=True)
        return Response(serializer.data)

    @extend_schema(
        request=PayrollSerializer,
        responses={201: PayrollSerializer}
    )
    def post(self, request):
        serializer = PayrollSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PayrollDetailAPIView(APIView):
    def get_object(self, pk, user):
        payroll = get_object_or_404(Payroll, pk=pk)
        if not user.is_staff and payroll.employee.user != user:
            raise PermissionDenied()
        return payroll

    @extend_schema(
        responses={200: PayrollSerializer}
    )
    def get(self, request, pk):
        payroll = self.get_object(pk, request.user)
        serializer = PayrollSerializer(payroll)
        return Response(serializer.data)

    @extend_schema(
        request=PayrollSerializer,
        responses={200: PayrollSerializer}
    )
    def put(self, request, pk):
        payroll = self.get_object(pk, request.user)
        serializer = PayrollSerializer(payroll, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        responses={204: None}
    )
    def delete(self, request, pk):
        payroll = self.get_object(pk, request.user)
        payroll.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
