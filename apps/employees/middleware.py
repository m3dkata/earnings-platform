from django.shortcuts import render
from django.utils import timezone
from .models import Leave


class LeaveCheckMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated and not request.user.is_staff:
            excluded_paths = [
                "/accounts/logout/",
                "/static/",
                "/media/",
            ]

            if not any(request.path.startswith(path) for path in excluded_paths):
                current_time = timezone.now()

                leave = Leave.objects.filter(
                    employee__user=request.user,
                    status="APPROVED",
                    start_datetime__lte=current_time,
                    end_datetime__gte=current_time,
                ).first()

                if leave:
                    formatted_end = leave.end_datetime.strftime("%H:%M %d/%m/%y")
                    return render(
                        request,
                        "employees/leave_block.html",
                        {"end_time": formatted_end},
                    )

        return self.get_response(request)
