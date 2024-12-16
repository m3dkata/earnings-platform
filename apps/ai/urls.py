from django.urls import path
from . import views

urlpatterns = [
    path("query/", views.ai_query, name="ai_query"),
    path("history/", views.get_chat_history, name="chat_history"),
]
