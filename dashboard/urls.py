from django.urls import path
from . import views

urlpatterns = [
    # Paths mapped to the view function we created above
    path('', views.dashboard_view, name='dashboard'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path("projects/", views.projects, name="projects"),
    path("projects/create/",views.create_project,name="create_project"),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
]