from django.urls import path

from . import views

urlpatterns = [
    path('facility/inventory/', views.inventory_home, name='inventory_home'),
    path('facility/inventory/blood/save/', views.blood_stock_save, name='blood_stock_save'),
    path('facility/inventory/supply/save/', views.medical_supply_save, name='medical_supply_save'),
]
