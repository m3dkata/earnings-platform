from django.urls import path
from . import views

urlpatterns = [
    path("", views.NotificationListView.as_view(), name="notification_list"),
    path("<int:pk>/read/", views.mark_as_read, name="mark_notification_read"),
]
