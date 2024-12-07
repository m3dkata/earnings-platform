from rest_framework import serializers
from apps.operations.models import Operation, Rate

class RateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rate
        fields = ['id', 'price', 'category']
        read_only_fields = ['id']

class OperationSerializer(serializers.ModelSerializer):
    category = RateSerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Rate.objects.all(),
        source='category',
        write_only=True
    )

    class Meta:
        model = Operation
        fields = ['id', 'code', 'name', 'time', 'price', 'date_added', 'category', 'category_id']
        read_only_fields = ['id', 'price', 'date_added']