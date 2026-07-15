from django.urls import path

from . import views

urlpatterns = [
    path('search/', views.facility_search, name='facility_search'),
    path('facility/register/', views.facility_register, name='facility_register'),
    path('facility/dashboard/', views.facility_dashboard, name='facility_dashboard'),
    path('facility/profile/', views.facility_profile, name='facility_profile'),
    path('facility/requests/', views.facility_requests_list, name='facility_requests'),
    path('facility/requests/<int:broadcast_id>/respond/', views.facility_respond, name='facility_respond'),
    path('leaderboard/', views.leaderboard, name='leaderboard'),
]
