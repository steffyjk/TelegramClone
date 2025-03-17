# core/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('generate_qr/', views.generate_qr_view, name='generate_qr'),
    path('check_login_status/', views.check_login_status, name='check_login_status'),
]
