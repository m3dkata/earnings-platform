from django.http import Http404
from django.core.exceptions import PermissionDenied
from django.shortcuts import render

def bad_request(request, exception):
    context = {}
    response = render(request, "errors/400.html", context)
    response.status_code = 400
    return response

def permission_denied(request, exception):
    context = {}
    response = render(request, "errors/403.html", context)
    response.status_code = 403
    return response

def page_not_found(request, exception):
    context = {}
    response = render(request, "errors/404.html", context)
    response.status_code = 404
    return response

def server_error(request):
    context = {}
    response = render(request, "errors/500.html", context)
    response.status_code = 500
    return response

def csrf_failure(request, reason=""):
    context = {'reason': reason}
    response = render(request, 'errors/403_csrf.html', context)
    response.status_code = 403
    return response
