from django.urls import path
from . import views

urlpatterns = [
    path('panel/', views.supervisor_dashboard_view, name='supervisor_dashboard'),
]