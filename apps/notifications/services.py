from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import Notification
from django.contrib.auth import get_user_model


class NotificationService:
    @staticmethod
    def notify_staff_new_registration(new_user):
        staff_users = get_user_model().objects.filter(is_staff=True)
        channel_layer = get_channel_layer()

        for staff_user in staff_users:
            Notification.objects.create(
                recipient=staff_user,
                notification_type="registration",
                message=f"New user registered: {new_user.first_name} {new_user.last_name}",
            )

            async_to_sync(channel_layer.group_send)(
                f"user_{staff_user.id}",
                {
                    "type": "notification_message",
                    "message": f"New user registered: {new_user.first_name} {new_user.last_name}",
                },
            )

    @staticmethod
    def notify_report_status(report, status):
        channel_layer = get_channel_layer()

        Notification.objects.create(
            recipient=report.employee.user,
            notification_type="report_status",
            message=f"Your report has been {status}",
            report=report,
        )

        async_to_sync(channel_layer.group_send)(
            f"user_{report.employee.user.id}",
            {
                "type": "notification_message",
                "message": f"Your report from {report.date} has been {status}",
            },
        )

    @staticmethod
    def notify_staff_new_report(report):
        staff_users = get_user_model().objects.filter(is_staff=True)
        channel_layer = get_channel_layer()

        for staff_user in staff_users:
            Notification.objects.create(
                recipient=staff_user,
                notification_type="report_submission",
                message=f"New report submitted by {report.employee.user.get_full_name()}",
                report=report,
            )

            async_to_sync(channel_layer.group_send)(
                f"user_{staff_user.id}",
                {
                    "type": "notification_message",
                    "message": f"New report submitted by {report.employee.user.get_full_name()} for {report.date}",
                },
            )

    @staticmethod
    def notify_leave_request(leave):
        staff_users = get_user_model().objects.filter(is_staff=True)
        channel_layer = get_channel_layer()

        for staff_user in staff_users:
            Notification.objects.create(
                recipient=staff_user,
                notification_type="leave_request",
                message=f"New leave request from {leave.employee.user.get_full_name()}",
            )

            async_to_sync(channel_layer.group_send)(
                f"user_{staff_user.id}",
                {
                    "type": "notification_message",
                    "message": f"New leave request from {leave.employee.user.get_full_name()}",
                },
            )

    @staticmethod
    def notify_leave_status(leave):
        channel_layer = get_channel_layer()

        Notification.objects.create(
            recipient=leave.employee.user,
            notification_type="leave_status",
            message=f"Your leave request has been {leave.status.lower()}",
        )

        async_to_sync(channel_layer.group_send)(
            f"user_{leave.employee.user.id}",
            {
                "type": "notification_message",
                "message": f"Your leave request for {leave.start_datetime.date()} has been {leave.status.lower()}",
            },
        )
