"""
URL configuration for EmergencyRx project.
"""
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('pages.urls')),
    path('', include('accounts.urls')),
    path('', include('facilities.urls')),
    path('', include('inventory.urls')),
    path('', include('emergency_requests.urls')),
    path('', include('notifications.urls')),
    path('', include('webhooks.urls')),
]
