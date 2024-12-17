from apps.api.serializers.notifications import NotificationSerializer
from rest_framework import viewsets
from apps.notifications.models import Notification
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated


class NotificationViewSet(viewsets.ModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(recipient=self.request.user).order_by(
            "-created_at"
        )

    def list(self, request):
        notifications = self.get_queryset()
        data = self.serializer_class(notifications, many=True).data
        return Response({"notifications": data})
