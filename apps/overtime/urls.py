from django.urls import path
from . import views

app_name = 'overtime'

urlpatterns = [
    path('', views.OvertimeListView.as_view(), name='list'),
    path('create/', views.OvertimeCreateView.as_view(), name='create'),
    path('<int:pk>/', views.OvertimeDetailView.as_view(), name='detail'),
    path('<int:pk>/update/', views.OvertimeUpdateView.as_view(), name='update'),
    path('<int:pk>/delete/', views.OvertimeDeleteView.as_view(), name='delete'),
    path('<int:pk>/approve/', views.OvertimeApproveView.as_view(), name='approve'),
    path('<int:pk>/reject/', views.OvertimeRejectView.as_view(), name='reject'),
]
