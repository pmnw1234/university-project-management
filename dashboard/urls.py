from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    path("projects/", views.projects, name="projects"),
    path("projects/create/",views.create_project,name="create_project"),
    path("projects/<int:project_id>/", views.project_detail, name="project_detail"),
    path("projects/<int:project_id>/milestones/", views.milestones_view, name="milestones"),
    path("projects/<int:project_id>/milestones/add/", views.add_milestone, name="add_milestone"),
    path("milestones/<int:milestone_id>/tasks/", views.milestone_tasks, name="milestone_tasks"),
    path("milestones/<int:milestone_id>/tasks/add/", views.add_task, name="add_task"),
    path("tasks/<int:task_id>/", views.task_detail, name="task_detail"),
    path("tasks/<int:task_id>/status/", views.update_task_status, name="update_task_status"),
    path("tasks/<int:task_id>/upload/", views.upload_task_attachment, name="upload_task_attachment"),
    path('profile/edit/', views.edit_profile, name='edit_profile'),

    path('admin-panel/', views.admin_dashboard_view, name='admin_dashboard'),

]