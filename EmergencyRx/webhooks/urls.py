from django.urls import path

from . import views

urlpatterns = [
    path('webhooks/sms/', views.sms_webhook, name='sms_webhook'),
]
