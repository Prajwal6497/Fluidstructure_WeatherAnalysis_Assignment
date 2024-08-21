from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/<str:city>/', views.weather_dashboard, name='weather_dashboard'),
]