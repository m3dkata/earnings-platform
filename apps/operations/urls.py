from django.urls import path
from . import views

urlpatterns = [
    path('', views.OperationListView.as_view(), name='operations_list'),
    path('create/', views.OperationCreateView.as_view(), name='operation_create'),
    path('<int:pk>/edit/', views.OperationUpdateView.as_view(), name='operation_edit'),
    path('<int:pk>/delete/', views.OperationDeleteView.as_view(), name='operation_delete'),
    
    path('rates/', views.RateListView.as_view(), name='rates_list'),
    path('rates/create/', views.RateCreateView.as_view(), name='rate_create'),
    path('rates/<int:pk>/edit/', views.RateUpdateView.as_view(), name='rate_edit'),
    path('rates/<int:pk>/delete/', views.RateDeleteView.as_view(), name='rate_delete'),
]