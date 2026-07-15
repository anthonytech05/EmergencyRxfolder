from django.urls import path

from . import views

urlpatterns = [
    path('request/', views.request_create, name='request_create'),
    path('request/mine/', views.my_requests, name='my_requests'),
    path('request/<int:pk>/', views.request_status, name='request_status'),
]
