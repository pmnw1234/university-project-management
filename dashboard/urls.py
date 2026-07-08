from django.urls import path
from . import views

urlpatterns = [
    # Paths mapped to the view function we created above
    path('', views.dashboard_view, name='dashboard'),
]