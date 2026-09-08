from django.urls import path

from . import health, views

urlpatterns = [
    path('webhook/', views.webhook, name='webhook'),
    path('health/', health.health, name='health'),
]
