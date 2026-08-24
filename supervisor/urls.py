from django.urls import path
from . import views

urlpatterns = [
    path('panel/', views.supervisor_dashboard, name='supervisor_dashboard'),
    path('supervisor/projects/', views.supervisor_projects, name='supervisor_projects'),
    path('supervisor/reviews/', views.supervisor_reviews, name='supervisor_reviews'),
    path('supervisor/edit-profile/', views.supervisor_edit_profile, name='supervisor_edit_profile'),
]