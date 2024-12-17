from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema
from django.shortcuts import get_object_or_404
from apps.operations.models import Operation, Rate
from apps.api.serializers.operations import OperationSerializer, RateSerializer


class OperationListCreateAPIView(APIView):
    @extend_schema(responses={200: OperationSerializer(many=True)})
    def get(self, request):
        operations = Operation.objects.select_related("category").all()
        serializer = OperationSerializer(operations, many=True)
        return Response(serializer.data)

    @extend_schema(request=OperationSerializer, responses={201: OperationSerializer})
    def post(self, request):
        serializer = OperationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OperationDetailAPIView(APIView):
    @extend_schema(responses={200: OperationSerializer})
    def get(self, request, pk):
        operation = get_object_or_404(
            Operation.objects.select_related("category"), pk=pk
        )
        serializer = OperationSerializer(operation)
        return Response(serializer.data)

    @extend_schema(request=OperationSerializer, responses={200: OperationSerializer})
    def put(self, request, pk):
        operation = get_object_or_404(Operation, pk=pk)
        serializer = OperationSerializer(operation, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(responses={204: None})
    def delete(self, request, pk):
        operation = get_object_or_404(Operation, pk=pk)
        operation.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class RateListCreateAPIView(APIView):
    @extend_schema(responses={200: RateSerializer(many=True)})
    def get(self, request):
        rates = Rate.objects.all()
        serializer = RateSerializer(rates, many=True)
        return Response(serializer.data)

    @extend_schema(request=RateSerializer, responses={201: RateSerializer})
    def post(self, request):
        serializer = RateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RateDetailAPIView(APIView):
    @extend_schema(responses={200: RateSerializer})
    def get(self, request, pk):
        rate = get_object_or_404(Rate, pk=pk)
        serializer = RateSerializer(rate)
        return Response(serializer.data)

    @extend_schema(request=RateSerializer, responses={200: RateSerializer})
    def put(self, request, pk):
        rate = get_object_or_404(Rate, pk=pk)
        serializer = RateSerializer(rate, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(responses={204: None})
    def delete(self, request, pk):
        rate = get_object_or_404(Rate, pk=pk)
        rate.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
