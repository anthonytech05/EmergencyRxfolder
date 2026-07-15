from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('share-your-story/', views.submit_testimonial, name='submit_testimonial'),
]
